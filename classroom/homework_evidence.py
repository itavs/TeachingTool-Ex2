"""Source-bound quote validation and conservative public-output privacy checks."""
from .models import SubmissionVersion


def source_text(job, evidence):
    if evidence['source'] == 'target':
        return job.target_text
    return job.peer_snapshots[evidence['peer_index']]['text']


def collect_evidence(individual, comparison):
    rows = []
    for row in individual.get('findings',[]):
        rows.extend({'source':'target','peer_index':None,'quote':q,'removed':False,
                     'label':f"Individual criterion {row['criterion_index']+1}"} for q in row['quotes'])
    rows.extend({**item,'removed':False,'label':'Comparison'} for item in comparison.get('evidence',[]))
    return rows


def annotated_evidence(job, rows):
    return [{**item,'verified':not item['removed'] and bool(item['quote']) and item['quote'] in source_text(job,item)}
            for item in rows]


def privacy_error(job, text):
    # These are defensive exact-text checks, not semantic anonymity certification.
    folded = text.casefold()
    peers = SubmissionVersion.objects.filter(pk__in=[p['id'] for p in job.peer_snapshots]).select_related('student')
    for peer in peers:
        user = peer.student
        for identity in [user.username,user.email,user.get_full_name()]:
            if len(identity.strip()) >= 4 and identity.casefold() in folded:
                return 'Remove peer identities before publication.'
    for peer in job.peer_snapshots:
        source = peer['text']
        # Do not block common short technical terms. Block verbatim peer passages.
        if (source and source.casefold() in folded) or any(source[i:i+80].casefold() in folded
                                                         for i in range(max(0,len(source)-79))):
            return 'Remove verbatim peer passages. Publish an anonymous conceptual comparison only.'
    return ''
