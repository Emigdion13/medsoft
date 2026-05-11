"""
Django management command to seed the database with realistic test data.

Usage:
    python manage.py seed_db --help
    python manage.py seed_db                    # Default: minimal set
    python manage.py seed_db --full             # Full dataset (doctors, patients, appointments)
    python manage.py seed-db --organizations 2  # Create multiple organizations
"""
import uuid

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from zoneinfo import ZoneInfo

from apps.core.organizations.models import Organization
from apps.core.users.models import User
from apps.doctors.models import Doctor, Specialty
from apps.patients.models import Patient
from apps.appointments.models import Appointment


TZ = ZoneInfo("America/Santo_Domingo")


# ── Seed data constants ───────────────────────────────────────────────

SPECIALTIES_DATA = [
    {"code": "GEN", "name": "Medicina General"},
    {"code": "INT", "name": "Medicina Interna"},
    {"code": "PED", "name": "Pediatría"},
    {"code": "GYN", "name": "Ginecología y Obstetricia"},
    {"code": "SUR", "name": "Cirugía General"},
    {"code": "CAR", "name": "Cardiología"},
    {"code": "DER", "name": "Dermatología"},
    {"code": "NEU", "name": "Neurología"},
    {"code": "ORT", "name": "Ortopedia y Traumatología"},
    {"code": "OFT", "name": "Oftalmología"},
]

DOCTORS_DATA = [
    {
        "cedula": "00112233456",
        "first_name": "Carlos",
        "last_name": "Méndez",
        "specialty_code": "GEN",
        "license": "RM-001-2024",
        "college": "MC-001",
        "room": "A-101",
    },
    {
        "cedula": "00223344567",
        "first_name": "María",
        "last_name": "Rodríguez",
        "specialty_code": "GYN",
        "license": "RM-002-2024",
        "college": "MC-002",
        "room": "B-205",
    },
    {
        "cedula": "00334455678",
        "first_name": "José",
        "last_name": "Hernández",
        "specialty_code": "PED",
        "license": "RM-003-2024",
        "college": "MC-003",
        "room": "C-310",
    },
    {
        "cedula": "00445566789",
        "first_name": "Ana",
        "last_name": "Martínez",
        "specialty_code": "CAR",
        "license": "RM-004-2024",
        "college": "MC-004",
        "room": "D-102",
    },
    {
        "cedula": "00556677890",
        "first_name": "Luis",
        "last_name": "Fernández",
        "specialty_code": "SUR",
        "license": "RM-005-2024",
        "college": "MC-005",
        "room": "E-401",
    },
]

PATIENTS_DATA = [
    {
        "cedula": "10123456789",
        "first_name": "Juan",
        "last_name": "Pérez",
        "birth_year": 1985,
        "sex": "M",
    },
    {
        "cedula": "10234567890",
        "first_name": "María",
        "last_name": "García",
        "birth_year": 1990,
        "sex": "F",
    },
    {
        "cedula": "10345678901",
        "first_name": "Pedro",
        "last_name": "Sánchez",
        "birth_year": 1978,
        "sex": "M",
    },
    {
        "cedula": "10456789012",
        "first_name": "Laura",
        "last_name": "Torres",
        "birth_year": 1995,
        "sex": "F",
    },
    {
        "cedula": "10567890123",
        "first_name": "Roberto",
        "last_name": "Ramírez",
        "birth_year": 1965,
        "sex": "M",
    },
    {
        "cedula": "10678901234",
        "first_name": "Carmen",
        "last_name": "López",
        "birth_year": 2000,
        "sex": "F",
    },
    {
        "cedula": "10789012345",
        "first_name": "Diego",
        "last_name": "Vargas",
        "birth_year": 1988,
        "sex": "M",
    },
    {
        "cedula": "10890123456",
        "first_name": "Sofía",
        "last_name": "Morales",
        "birth_year": 1972,
        "sex": "F",
    },
]

APPOINTMENT_TEMPLATES = [
    # (doctor_idx, patient_idx, hours_offset, duration_hours, appt_type, reason, status)
    (0, 0, 1, 1, "CONSULTA", "Chequeo general de rutina", "PROGRAMADA"),
    (0, 1, 2, 1, "CONTROL", "Control post-operatorio", "PROGRAMADA"),
    (1, 2, 1, 1.5, "CONSULTA", "Consulta ginecológica anual", "CONFIRMADA"),
    (2, 3, 3, 1, "SEGUIMIENTO", "Seguimiento pediátrico", "PROGRAMADA"),
    (3, 4, 1, 1, "CONSULTA", "Evaluación cardíaca", "EN_CURSO"),
    (4, 5, 2, 2, "CONSULTA", "Consulta quirúrgica pre-operatoria", "PROGRAMADA"),
    (0, 6, 4, 1, "CONTROL", "Control de presión arterial", "PROGRAMADA"),
    (1, 7, 5, 1, "SEGUIMIENTO", "Seguimiento prenatal", "CONFIRMADA"),
]


# ── Helpers ───────────────────────────────────────────────────────────

def _create_org(index: int = 0) -> Organization:
    """Create an organization with a unique name."""
    names = [
        ("Clínica Central Santo Domingo", "Clínica Central"),
        ("Centro Médico del Este", "CME"),
        ("Hospital Nacional Dr. Blandín", "Blandín"),
    ]
    if index >= len(names):
        name = f"Organización {index + 1}"
        trade_name = None
    else:
        name, trade_name = names[index]

    org, created = Organization.objects.get_or_create(
        id=uuid.uuid4(),
        defaults={
            "name": name,
            "trade_name": trade_name or "",
            "rnc": f"RNC{10000 + index}",
            "phone": f"+1-809-{500 + index:03d}-{index:04d}",
            "email": f"contacto{index}@clinica.local",
            "address": f"Dirección {index + 1}, Santo Domingo",
            "province": "Distrito Nacional",
            "municipality": "Santo Domingo Este",
        },
    )
    return org


def _create_admin_user(org: Organization, username: str = "admin") -> User:
    """Create or retrieve the admin user for an organization."""
    user, created = User.objects.get_or_create(
        id=uuid.uuid4(),
        username=username,
        defaults={
            "organization": org,
            "email": f"{username}@{org.name.lower().replace(' ', '')}.local",
            "first_name": "Sistema",
            "last_name": "Administrador",
            "role": "ADMINISTRATOR",
            "is_active": True,
            "is_superuser": True,
            "is_staff": True,
        },
    )
    if created:
        user.set_password("admin123")
        user.save()
    return user


def _create_specialties() -> dict[str, Specialty]:
    """Create all specialty records. Returns a code->Specialty mapping."""
    mapping = {}
    for spec_data in SPECIALTIES_DATA:
        spec, created = Specialty.objects.get_or_create(
            id=uuid.uuid4(),
            code=spec_data["code"],
            defaults={
                "name": spec_data["name"],
                "description": f"Especialidad médica: {spec_data['name']}",
                "is_active": True,
            },
        )
        mapping[spec.code] = spec
    return mapping


def _create_doctors(
    org: Organization,
    admin_user: User,
    specialties: dict[str, Specialty],
) -> list[Doctor]:
    """Create doctor records linked to the organization."""
    doctors = []
    for doc_data in DOCTORS_DATA:
        specialty = specialties.get(doc_data["specialty_code"])
        if not specialty:
            continue

        user_id = uuid.uuid4()
        user, _ = User.objects.get_or_create(
            id=user_id,
            username=doc_data["cedula"],
            defaults={
                "organization": org,
                "email": f"{doc_data['first_name'].lower()}.{doc_data['last_name'].lower().replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')}@medisoft.local",
                "first_name": doc_data["first_name"],
                "last_name": doc_data["last_name"],
                "role": "DOCTOR",
                "is_active": True,
            },
        )
        if not user.check_password("doctor123"):
            user.set_password("doctor123")
            user.save()

        doctor, created = Doctor.objects.get_or_create(
            id=uuid.uuid4(),
            organization=org,
            cedula=doc_data["cedula"],
            defaults={
                "user": user,
                "license_number": doc_data["license"],
                "medical_college_number": doc_data["college"],
                "first_name": doc_data["first_name"],
                "last_name": doc_data["last_name"],
                "specialty_main": specialty,
                "phone": f"+1-809-{600 + len(doctors):03d}-{len(doctors):04d}",
                "email": user.email,
                "office_room": doc_data["room"],
                "is_active": True,
            },
        )
        doctors.append(doctor)
    return doctors


def _create_patients(
    org: Organization,
    admin_user: User,
) -> list[Patient]:
    """Create patient records."""
    patients = []
    for pat_data in PATIENTS_DATA:
        birth_date_str = f"{pat_data['birth_year']}-{(pat_data['cedula'][-2:] if len(str(pat_data['cedula'])) > 1 else '01')}-15"
        try:
            from datetime import date
            birth_date = date(int(pat_data['birth_year']), int((pat_data['cedula'][-2:] or '6')[:2]) % 12 + 1, min(int(str(pat_data['cedula'])[-2:]) % 28 + 1, 28))
        except (ValueError, TypeError):
            birth_date = date(pat_data["birth_year"], 6, 15)

        patient, created = Patient.objects.get_or_create(
            id=uuid.uuid4(),
            organization=org,
            cedula=pat_data["cedula"],
            defaults={
                "identity_type": "CEDULA",
                "first_name": pat_data["first_name"],
                "last_name": pat_data["last_name"],
                "birth_date": birth_date,
                "sex": pat_data["sex"],
                "nationality": "DOMINICANA",
                "phone_primary": f"+1-809-{700 + len(patients):03d}-{len(patients):04d}",
                "email": f"{pat_data['first_name'].lower()}.{pat_data['last_name'].lower()}@correo.local",
                "blood_type": ["A+", "B+", "O+", "AB+"][len(patients) % 4],
                "province": "Distrito Nacional",
                "municipality": "Santo Domingo Este",
                "status": "ACTIVO",
                "created_by": admin_user,
            },
        )
        patients.append(patient)
    return patients


def _create_appointments(
    doctors: list[Doctor],
    patients: list[Patient],
    admin_user: User,
    org: Organization,
) -> None:
    """Create sample appointments spread across future dates."""
    from datetime import datetime, timedelta

    now = datetime.now(TZ)
    created_count = 0

    for doc_idx, pat_idx, hours_offset, duration_hours, appt_type, reason, status in APPOINTMENT_TEMPLATES:
        if doc_idx >= len(doctors) or pat_idx >= len(patients):
            continue

        doctor = doctors[doc_idx]
        patient = patients[pat_idx]

        # Spread appointments across different days
        start_date = now + timedelta(days=hours_offset, hours=8)  # Start at ~8am offset by days
        start_at = start_date.replace(minute=0, second=0, microsecond=0)
        end_at = start_at + timedelta(hours=duration_hours)

        appointment, created = Appointment.objects.get_or_create(
            id=uuid.uuid4(),
            organization=org,
            doctor=doctor,
            patient=patient,
            defaults={
                "start_at": start_at,
                "end_at": end_at,
                "appointment_type": appt_type,
                "reason": reason,
                "status": status,
                "notes": f"Nota de prueba para cita con {doctor.first_name} el {start_at.strftime('%Y-%m-%d')}",
                "created_by": admin_user,
            },
        )
        if created:
            created_count += 1

    print(f"  Created {created_count} appointments")


# ── Command ───────────────────────────────────────────────────────────

class Command(BaseCommand):
    """Seed the database with realistic test data for a clinic management system."""

    help = (
        "Seeds the database with organizations, users, doctors, patients, "
        "and sample appointments. Useful for development and testing."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--organizations",
            type=int,
            default=1,
            help="Number of organizations to create (default: 1)",
        )
        parser.add_argument(
            "--full",
            action="store_true",
            help="Create full dataset including doctors, patients, and appointments",
        )
        parser.add_argument(
            "--clear-first",
            action="store_true",
            help="Delete all existing seeded data before creating new records",
        )

    def handle(self, *args, **options):
        org_count = options["organizations"]
        full_dataset = options["full"]
        clear_first = options["clear_first"]

        verbosity = options.get("verbosity", 1)

        if verbosity >= 2:
            self.stdout.write("=" * 60)
            self.stdout.write("MEDISOFT DATABASE SEEDER")
            self.stdout.write("=" * 60)

        # ── Clear existing data if requested ────────────────────────
        if clear_first:
            if verbosity >= 1:
                self.stdout.write("\nClearing existing seeded data...")
            with transaction.atomic():
                Appointment.objects.filter(organization__isnull=False).delete()
                Doctor.objects.all().delete()
                Patient.objects.all().delete()
                User.objects.filter(role__in=["DOCTOR", "ADMINISTRATOR"]).exclude(username="admin").delete()
                Specialty.objects.all().delete()
                Organization.objects.all().delete()
            if verbosity >= 1:
                self.stdout.write(self.style.SUCCESS("Existing data cleared"))

        # ── Create organizations ────────────────────────────────────
        if verbosity >= 1:
            self.stdout.write("\nCreating organizations...")

        organizations = []
        for i in range(org_count):
            org = _create_org(i)
            organizations.append(org)
            status_msg = "created" if getattr(org, "_created", False) else "exists"
            if verbosity >= 2:
                self.stdout.write(f"  Organization {i + 1}: {org.name} ({status_msg})")

        # ── Create specialties (shared across orgs) ────────────────
        if full_dataset:
            if verbosity >= 1:
                self.stdout.write("Creating medical specialties...")
            specialties = _create_specialties()
            if verbosity >= 2:
                for code, spec in specialties.items():
                    self.stdout.write(f"  Specialty: {code} - {spec.name}")

        # ── Create users, doctors, patients, appointments per org ───
        for idx, org in enumerate(organizations):
            prefix = f"[Org {idx + 1}: {org.name}] " if org_count > 1 else ""

            if verbosity >= 1:
                self.stdout.write(f"\n{prefix}Setting up users and data...")

            admin_user = _create_admin_user(org)
            if verbosity >= 2:
                self.stdout.write(f"  Admin user: {admin_user.username}")

            if full_dataset:
                # Create doctors
                doctors = _create_doctors(org, admin_user, specialties)
                if verbosity >= 1:
                    self.stdout.write(f"  Created {len(doctors)} doctors")

                # Create patients
                patients = _create_patients(org, admin_user)
                if verbosity >= 1:
                    self.stdout.write(f"  Created {len(patients)} patients")

                # Create appointments
                _create_appointments(doctors, patients, admin_user, org)
            else:
                # Minimal mode: just create the organization and admin user
                pass

        if verbosity >= 1:
            self.stdout.write(self.style.SUCCESS("\n✓ Database seeding completed successfully!"))
            self.stdout.write("\nDefault credentials:")
            self.stdout.write("  Admin:    username=admin / password=admin123")
            if full_dataset:
                self.stdout.write("  Doctors:  username=<cedula> / password=doctor123")
