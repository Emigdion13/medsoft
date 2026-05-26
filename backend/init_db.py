"""
Database initialization script - creates default organization, admin user,
sample doctors, patients, and appointments for testing.
CRLF-safe alternative to bash heredocs in startup.sh.
"""
import os
import sys
from datetime import datetime, timedelta


def _get_tz():
    """Return the project default timezone (America/Santo_Domingo)."""
    from zoneinfo import ZoneInfo
    return ZoneInfo(os.environ.get("TZ", "America/Santo_Domingo"))


def init():
    import django

    # Set settings module explicitly (strip whitespace from .env files)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings_docker".strip())
    if not os.environ.get("DATABASE_URL"):
        # Fallback: build DATABASE_URL from individual env vars
        db_parts = {k.strip(): v.strip() for k, v in os.environ.items() if k.startswith("DB_")}
        if all(k in db_parts for k in ("DB_NAME", "DB_USER", "DB_HOST")):
            os.environ["DATABASE_URL"] = (
                f"postgresql://{db_parts['DB_USER']}:{db_parts.get('DB_PASSWORD', '')}"
                f"@{db_parts['DB_HOST']}:{db_parts.get('DB_PORT', '5432')}/{db_parts['DB_NAME']}"
            )

    django.setup()

    from apps.core.organizations.models import Organization
    from apps.core.users.models import User
    from apps.doctors.models import Doctor, Specialty
    from apps.patients.models import Patient
    from apps.appointments.models import Appointment

    # ── Organization ───────────────────────────────────────────────
    org, created = Organization.objects.get_or_create(
        name="Default Organization",
        defaults={
            "rnc": "123456789",
            "phone": "+1-809-000-0000",
            "email": "contact@medisoft.local",
            "address": "Default address",
            "province": "Santo Domingo",
            "municipality": "Santo Domingo",
            "is_active": True,
        },
    )
    print(f"Organization {'created' if created else 'exists'}: {org.name} (pk={org.pk})")

    # ── Admin User ─────────────────────────────────────────────────
    password = os.environ.get("DJANGO_ADMIN_PASSWORD", "admin123")
    email = os.environ.get("DJANGO_ADMIN_EMAIL", "admin@medisoft.local")

    user, created = User.objects.get_or_create(
        username="admin",
        defaults={
            "organization": org,
            "email": email,
            "first_name": "System",
            "last_name": "Administrator",
            "role": "ADMINISTRATOR",
            "is_active": True,
            "is_superuser": True,
            "is_staff": True,
        },
    )

    # Always ensure correct password and superuser status
    if not user.check_password(password):
        user.set_password(password)
    user.email = email
    user.role = "ADMINISTRATOR"
    user.is_active = True
    user.is_superuser = True
    user.is_staff = True
    user.save()
    print(f"Admin user {'created' if created else 'updated'}: {user.username} (pk={user.pk})")

    tz = _get_tz()

    # ── Specialty ──────────────────────────────────────────────────
    specialty, _ = Specialty.objects.get_or_create(
        code="GEN",
        defaults={"name": "Medicina General", "is_active": True},
    )

    # ── Doctor (linked to admin user) ──────────────────────────────
    doctor, created = Doctor.objects.get_or_create(
        cedula="00112233456",
        defaults={
            "organization": org,
            "user": user,
            "license_number": "RM-001-2024",
            "medical_college_number": "MC-001",
            "first_name": "Carlos",
            "last_name": "Mendez",
            "specialty_main": specialty,
            "phone": "+1-809-555-0100",
            "email": "carlos.mendez@medisoft.local",
            "is_active": True,
        },
    )
    print(f"Doctor {'created' if created else 'exists'}: {doctor.first_name} {doctor.last_name}")

    # ── Doctor User (separate login for the doctor) ───────────────
    doctor_user, created = User.objects.get_or_create(
        username="doctor",
        defaults={
            "organization": org,
            "email": "carlos.mendez@medisoft.local",
            "first_name": "Carlos",
            "last_name": "Mendez",
            "role": "DOCTOR",
            "is_active": True,
        },
    )
    if not doctor_user.check_password("doctor123"):
        doctor_user.set_password("doctor123")
    doctor_user.role = "DOCTOR"
    doctor_user.is_active = True
    doctor_user.save()
    # Link doctor to doctor_user
    doctor.user = doctor_user
    doctor.save(update_fields=['user'])
    print(f"Doctor user {'created' if created else 'updated'}: {doctor_user.username} (pw: doctor123)")

    # ── Secretary User ────────────────────────────────────────────
    secretary_user, created = User.objects.get_or_create(
        username="secretary",
        defaults={
            "organization": org,
            "email": "secretary@medisoft.local",
            "first_name": "Maria",
            "last_name": "Lopez",
            "role": "SECRETARY",
            "is_active": True,
        },
    )
    if not secretary_user.check_password("secretary123"):
        secretary_user.set_password("secretary123")
    secretary_user.role = "SECRETARY"
    secretary_user.is_active = True
    secretary_user.save()
    print(f"Secretary user {'created' if created else 'updated'}: {secretary_user.username} (pw: secretary123)")

    # ── Assign secretary to doctor ────────────────────────────────
    from apps.doctors.models import SecretaryDoctor
    sd, created = SecretaryDoctor.objects.get_or_create(
        secretary=secretary_user,
        doctor=doctor,
        defaults={"is_active": True},
    )
    print(f"Secretary-Doctor assignment {'created' if created else 'exists'}: {sd}")

    # ── Patients ───────────────────────────────────────────────────
    patient_data = [
        {
            "cedula": "00223344567",
            "first_name": "Ana",
            "last_name": "Garcia",
            "birth_date": datetime(1985, 6, 15, tzinfo=tz).date(),
            "sex": "F",
        },
        {
            "cedula": "00334455678",
            "first_name": "Luis",
            "last_name": "Martinez",
            "birth_date": datetime(1990, 3, 22, tzinfo=tz).date(),
            "sex": "M",
        },
    ]

    patients = []
    for pd in patient_data:
        p, _ = Patient.objects.get_or_create(
            cedula=pd["cedula"],
            defaults={
                "organization": org,
                **pd,
            },
        )
        patients.append(p)
        print(f"Patient {'created' if p._state.adding else 'exists'}: {p.first_name} {p.last_name}")

    # ── Sample Appointment (for cancel test) ───────────────────────
    now = datetime.now(tz)
    appt_start = now.replace(hour=14, minute=0, second=0, microsecond=0) + timedelta(days=1)
    appt_end = appt_start + timedelta(hours=1)

    # Only create if no future appointments exist (idempotent)
    existing = Appointment.objects.filter(
        organization=org,
        start_at__gte=now,
        deleted_at__isnull=True,
    ).exists()

    if not existing:
        Appointment.objects.create(
            organization=org,
            doctor=doctor,
            patient=patients[0],
            start_at=appt_start,
            end_at=appt_end,
            appointment_type="CONSULTA",
            reason="Chequeo general de rutina",
            status="PROGRAMADA",
            created_by=user,
        )
        print(f"Appointment created: {appt_start.strftime('%Y-%m-%d %H:%M')}")
    else:
        print("Appointment already exists (skipped)")


if __name__ == "__main__":
    init()
