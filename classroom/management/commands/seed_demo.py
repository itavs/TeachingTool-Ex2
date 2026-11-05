"""Create isolated demo identities; never use or print personal credentials."""
from datetime import datetime, timedelta
import json
from pathlib import Path
import secrets
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from classroom.models import Course, Meeting, Membership

ACCOUNTS = ["lecturer_alpha", "lecturer_beta", "student_alex", "student_blair", "student_casey", "observer"]


class Command(BaseCommand):
    help = "Seed two demo courses and six personal demo accounts; credentials stay in .local/."

    def handle(self, *args, **options):
        user_model = get_user_model()
        path = Path(settings.LOCAL_DIR) / "demo-credentials.json"
        try:
            credentials = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        except (ValueError, OSError) as error:
            raise CommandError("Cannot read local demo credentials; no changes made.") from error
        if not isinstance(credentials, dict):
            raise CommandError("Unexpected local credential format; no changes made.")
        # Do not take over an unrelated pre-existing username or reset passwords on rerun.
        for username in ACCOUNTS:
            existing = user_model.objects.filter(username=username).first()
            password = credentials.get(username)
            if password is not None and not isinstance(password, str):
                raise CommandError("Unexpected credential format; no changes made.")
            if existing and (not password or not existing.check_password(password)):
                raise CommandError(f"Existing account {username} is not owned by this demo seed; no changes made.")
        if not path.exists() and Course.objects.filter(code__in=["DEMO-CS101", "DEMO-SE201"]).exists():
            raise CommandError("Demo course codes already exist without seed credentials; no changes made.")
        for username in ACCOUNTS:
            credentials.setdefault(username, secrets.token_urlsafe(18))
        path.parent.mkdir(parents=True, exist_ok=True)
        # Persist secrets first so a filesystem failure cannot create inaccessible accounts.
        temporary = path.with_suffix(".tmp")
        temporary.write_text(json.dumps(credentials, indent=2) + "\n", encoding="utf-8")
        temporary.replace(path)
        with transaction.atomic():
            users = {}
            for username in ACCOUNTS:
                user, created = user_model.objects.get_or_create(username=username)
                if created:
                    user.set_password(credentials[username])
                    user.save(update_fields=["password"])
                users[username] = user
            alpha, _ = Course.objects.get_or_create(code="DEMO-CS101", defaults={
                "title": "Programming foundations", "description": "Explore objects, classes and clear program design."})
            beta, _ = Course.objects.get_or_create(code="DEMO-SE201", defaults={
                "title": "Software engineering", "description": "From requirements to an implementable design."})
            memberships = [
                ("lecturer_alpha", alpha, "lecturer"), ("lecturer_beta", beta, "lecturer"),
                ("student_alex", alpha, "student"), ("student_blair", beta, "student"),
                ("student_casey", alpha, "student"), ("student_casey", beta, "student"),
                ("lecturer_alpha", beta, "student"),
            ]
            for username, course, role in memberships:
                Membership.objects.get_or_create(user=users[username], course=course, defaults={"role": role})
            tomorrow = timezone.localdate() + timedelta(days=1)
            for course, titles in [(alpha, ["Objects and classes", "Working with methods"]),
                                   (beta, ["Understanding requirements", "Designing components"])]:
                for day, title in enumerate(titles):
                    starts_at = timezone.make_aware(datetime.combine(tomorrow + timedelta(days=day), datetime.min.time()).replace(hour=10))
                    Meeting.objects.get_or_create(course=course, title=title, defaults={
                        "starts_at": starts_at, "description": "A sample meeting for this course. Open it to view the details."})
        self.stdout.write(self.style.SUCCESS("Demo data ready: two courses and six accounts. No passwords printed."))
        self.stdout.write(f"Open local credentials: {path}")
