"""Poll state transitions: authorize freshly, lock meeting first, keep votes final."""
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Count
from django.utils import timezone
from .attendance import authorize, lock_and_authorize, CourseAccessError
from .models import Membership, Poll, PollVote
from .poll_generation import get_poll_generator, GenerationUnavailable
from .poll_contract import validate_generated


class PollError(Exception):
    def __init__(self, message, status=409):
        super().__init__(message)
        self.status = status


def validate_input(kind, language, material):
    if kind not in Poll.Kind.values or language not in Poll.Language.values:
        raise ValidationError('Choose a supported poll type and language.')
    if not isinstance(material, str) or not material.strip() or len(material) > 6000:
        raise ValidationError('Learning material must contain 1–6000 characters and cannot be whitespace only.')


def validate_content(kind, data):
    expected = {'question', 'options'} | ({'correct_index', 'explanation'} if kind == Poll.Kind.COMPREHENSION else set())
    if not isinstance(data, dict) or set(data) != expected:
        raise ValidationError('Invalid poll content fields for this type.')
    if not isinstance(data['question'], str) or not data['question'].strip():
        raise ValidationError('Enter a question.')
    options = data['options']
    if not isinstance(options, list) or len(options) != 4 or any(not isinstance(x, str) or not x.strip() for x in options):
        raise ValidationError('Enter exactly four nonempty options.')
    if len({x.strip() for x in options}) != 4:
        raise ValidationError('Options must be distinct.')
    if kind == Poll.Kind.COMPREHENSION:
        if type(data['correct_index']) is not int or not 0 <= data['correct_index'] <= 3:
            raise ValidationError('Choose one correct option.')
        if not isinstance(data['explanation'], str) or not data['explanation'].strip():
            raise ValidationError('Enter a short explanation.')


def content_of(poll):
    data = {'question': poll.question, 'options': poll.options}
    if poll.kind == Poll.Kind.COMPREHENSION:
        data.update(correct_index=poll.correct_index, explanation=poll.explanation)
    return data


def create_generated_draft(meeting_id, user, kind, language, material):
    authorize(meeting_id, user, Membership.Role.LECTURER)
    validate_input(kind, language, material)
    if language!='en':
        raise GenerationUnavailable('Automatic draft generation is currently available in English only. Hebrew polls can still be edited, published and answered.')
    # Model generation must stay outside database transactions.
    try:
        data = get_poll_generator().generate(material, kind, language)
    except GenerationUnavailable:
        raise
    except Exception:
        raise GenerationUnavailable('Generation failed. No draft was saved. You may retry explicitly.') from None
    try:validate_generated(kind,data)
    except (TypeError,ValueError):raise ValidationError('The generated draft failed content checks.') from None
    validate_content(kind, data)
    with transaction.atomic():
        lock_and_authorize(meeting_id, user, Membership.Role.LECTURER)
        return Poll.objects.create(meeting_id=meeting_id, kind=kind, language=language,
            material=material, question=data['question'].strip(), options=[x.strip() for x in data['options']],
            correct_index=data.get('correct_index'), explanation=data.get('explanation', '').strip(),
            origin='ai', created_at=timezone.now())


def get_poll(meeting_id, poll_id, user):
    meeting, membership = authorize(meeting_id, user)
    poll = Poll.objects.filter(pk=poll_id, meeting=meeting).first()
    if poll is None or (membership.role == Membership.Role.STUDENT and poll.status == Poll.Status.DRAFT):
        raise CourseAccessError(404)
    return poll, membership


def locked_poll(meeting_id, poll_id, user, role):
    lock_and_authorize(meeting_id, user, role)
    poll = Poll.objects.select_for_update().filter(pk=poll_id, meeting_id=meeting_id).first()
    if poll is None:
        raise CourseAccessError(404)
    return poll


def require_draft(poll, version):
    if poll.status != Poll.Status.DRAFT:
        raise PollError('Only an unpublished draft can be edited or published.')
    if poll.version != version:
        raise PollError('This draft changed in another request. Reload and review it before continuing.')


@transaction.atomic
def edit_draft(meeting_id, poll_id, user, version, data):
    poll = locked_poll(meeting_id, poll_id, user, Membership.Role.LECTURER)
    require_draft(poll, version)
    validate_content(poll.kind, data)
    poll.question = data['question'].strip()
    poll.options = [x.strip() for x in data['options']]
    poll.correct_index = data.get('correct_index')
    poll.explanation = data.get('explanation', '').strip()
    poll.version += 1
    poll.save()
    return poll


@transaction.atomic
def publish(meeting_id, poll_id, user, version):
    poll = locked_poll(meeting_id, poll_id, user, Membership.Role.LECTURER)
    require_draft(poll, version)
    validate_input(poll.kind, poll.language, poll.material)
    validate_content(poll.kind, content_of(poll))
    if Poll.objects.filter(meeting_id=meeting_id, status=Poll.Status.ACTIVE).exists():
        raise PollError('This meeting already has an active poll. Close it before publishing another.')
    poll.status = Poll.Status.ACTIVE
    poll.published_at = timezone.now()
    poll.version += 1
    poll.save()
    return poll


@transaction.atomic
def close(meeting_id, poll_id, user):
    poll = locked_poll(meeting_id, poll_id, user, Membership.Role.LECTURER)
    if poll.status == Poll.Status.CLOSED:
        return poll
    if poll.status != Poll.Status.ACTIVE:
        raise PollError('Only an active poll can be closed.')
    poll.status = Poll.Status.CLOSED
    poll.closed_at = timezone.now()
    poll.version += 1
    poll.save()
    return poll


@transaction.atomic
def vote(meeting_id, poll_id, user, option_index):
    poll = locked_poll(meeting_id, poll_id, user, Membership.Role.STUDENT)
    if poll.status == Poll.Status.DRAFT:
        raise CourseAccessError(404)
    if poll.status != Poll.Status.ACTIVE:
        raise PollError('Voting is closed.')
    if type(option_index) is not int or not 0 <= option_index < 4:
        raise ValidationError('Select one of the four options.')
    if PollVote.objects.filter(poll=poll, student=user).exists():
        raise PollError('Your final response was already submitted and cannot be changed.')
    return PollVote.objects.create(poll=poll, student=user, option_index=option_index, submitted_at=timezone.now())


def origin_label_for(poll, membership):
    """Draft review guidance is actionable only for a Lecturer reviewing a draft."""
    if poll.origin == 'demo':
        return poll.origin_label
    if membership.role == Membership.Role.LECTURER and poll.status == Poll.Status.DRAFT:
        return poll.origin_label
    return 'Model-generated poll'


def public_payload(poll, membership, user):
    """Whitelist disclosure fields: never serialize a model instance to students."""
    lecturer = membership.role == Membership.Role.LECTURER
    data = {'id': poll.pk, 'kind': poll.kind, 'kind_label': poll.get_kind_display(),
        'language': poll.language, 'language_label': poll.get_language_display(), 'status': poll.status,
        'origin_label': origin_label_for(poll,membership), 'question': poll.question,
        'options': [{'index': i, 'text': text} for i, text in enumerate(poll.options)]}
    own = poll.votes.filter(student=user).first() if not lecturer else None
    data['has_voted'] = own is not None
    if own:
        data['own_option'] = own.option_index
    data['show_results'] = lecturer or poll.status == Poll.Status.CLOSED
    if data['show_results']:
        grouped = dict(poll.votes.values('option_index').annotate(count=Count('pk')).values_list('option_index', 'count'))
        total = sum(grouped.values())
        data['respondent_count'] = total
        data['results'] = [{'text': text, 'count': grouped.get(i, 0),
            'percent': round(grouped.get(i, 0) * 100 / total, 2) if total else 0}
            for i, text in enumerate(poll.options)]
    data['show_answer'] = poll.kind == Poll.Kind.COMPREHENSION and (lecturer or poll.status == Poll.Status.CLOSED)
    if data['show_answer']:
        data.update(correct_index=poll.correct_index, correct_answer=poll.options[poll.correct_index], explanation=poll.explanation)
    return data
