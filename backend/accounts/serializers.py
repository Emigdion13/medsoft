
from django.utils import timezone
from rest_framework import serializers

from apps.core.users.models import User
from apps.core.organizations.models import Organization
from apps.doctors.models import Specialty, Doctor
from apps.patients.models import Patient
from apps.appointments.models import Appointment


class TimeZoneDateTimeField(serializers.DateTimeField):
    """DateTimeField that treats naive datetimes as America/Santo_Domingo timezone."""
    
    def to_internal_value(self, value):
        """Convert incoming value to datetime, treating naive datetimes as DR time."""
        if value is None:
            return value
        
        # Let the parent handle parsing
        dt = super().to_internal_value(value)
        
        # If datetime is naive (no timezone), assume it's in America/Santo_Domingo
        if dt is not None and dt.tzinfo is None:
            dr_tz = timezone.get_fixed_timezone(-240)  # America/Santo_Domingo is UTC-4
            dt = timezone.make_aware(dt, dr_tz)
        
        return dt


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""

    id = serializers.UUIDField(source='pk', read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'role',
            'organization',
            'is_active',
            'is_staff',
        ]
        read_only_fields = ['id', 'is_active', 'is_staff', 'organization']
        extra_kwargs = {
            'organization': {'read_only': True},
        }


class LoginSerializer(serializers.Serializer):
    """Serializer for login endpoint."""

    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for registration endpoint."""

    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
            'confirm_password',
        ]

    def validate(self, attrs: dict) -> dict:
        """Validate password confirmation matches and uniqueness."""
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'Las contraseñas no coinciden'})

        # Get the organization for uniqueness checks
        org = Organization.objects.first()
        if not org:
            raise serializers.ValidationError({'organization': 'No se encontró una organización. Por favor, contacte al soporte.'})

        # Check for existing user with same username in this organization
        if User.objects.filter(organization=org, username=attrs['username']).exists():
            raise serializers.ValidationError({'username': 'Ya existe un usuario con este nombre de usuario en esta organización'})

        # Check for existing user with same email in this organization
        if User.objects.filter(organization=org, email=attrs['email'].lower()).exists():
            raise serializers.ValidationError({'email': 'Ya existe un usuario con este correo electrónico en esta organización'})

        return attrs

    def create(self, validated_data: dict) -> User:
        """Create user with hashed password."""
        # Get the first organization (there should be one from initial setup)
        org = Organization.objects.first()
        if not org:
            raise serializers.ValidationError({'organization': 'No se encontró una organización. Por favor, contacte al soporte.'})
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password'],
            organization_id=org.id,
        )
        return user


class TokenRefreshSerializer(serializers.Serializer):
    """Serializer for token refresh endpoint."""

    refresh = serializers.CharField()


class AuthResponseSerializer(serializers.Serializer):
    """Serializer for auth response (tokens + user)."""

    access = serializers.CharField(required=False, default='')
    refresh = serializers.CharField(required=False, default='')
    user = UserSerializer()


# ── Specialty ──────────────────────────────────────────────────────────

class SpecialtySerializer(serializers.ModelSerializer):
    """Serializer for Specialty model."""

    id = serializers.UUIDField(source='pk', read_only=True)

    class Meta:
        model = Specialty
        fields = ['id', 'code', 'name', 'description', 'is_active']
        read_only_fields = ['id']


# ── Doctor ─────────────────────────────────────────────────────────────

class DoctorSerializer(serializers.ModelSerializer):
    """Serializer for Doctor model."""

    id = serializers.UUIDField(source='pk', read_only=True)
    specialty_main = SpecialtySerializer(read_only=True)
    specialty_main_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Doctor
        fields = [
            'id', 'organization', 'cedula', 'license_number', 'medical_college_number',
            'first_name', 'last_name', 'specialty_main', 'specialty_main_id',
            'phone', 'email', 'office_room', 'is_active',
        ]
        read_only_fields = ['id', 'organization']
        extra_kwargs = {
            'organization': {'read_only': True},
        }

    def create(self, validated_data: dict) -> Doctor:
        specialty_main_id = validated_data.pop('specialty_main_id', None)
        if specialty_main_id:
            from apps.doctors.models import Specialty
            validated_data['specialty_main'] = Specialty.objects.get(
                pk=specialty_main_id
            )
        return super().create(validated_data)

    def update(self, instance: Doctor, validated_data: dict) -> Doctor:
        specialty_main_id = validated_data.pop('specialty_main_id', None)
        if specialty_main_id:
            from apps.doctors.models import Specialty
            validated_data['specialty_main'] = Specialty.objects.get(
                pk=specialty_main_id
            )
        return super().update(instance, validated_data)


# ── Patient ────────────────────────────────────────────────────────────

class PatientSerializer(serializers.ModelSerializer):
    """Serializer for Patient model."""

    id = serializers.UUIDField(source='pk', read_only=True)
    age = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = [
            'id', 'organization', 'identity_type', 'cedula', 'passport_number',
            'first_name', 'last_name', 'birth_date', 'age', 'sex',
            'nationality', 'phone_primary', 'phone_secondary', 'email',
            'address', 'province', 'municipality',
            'blood_type', 'allergies', 'chronic_conditions',
            'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relation',
            'ars_provider', 'ars_affiliation_number',
            'status',
        ]
        read_only_fields = ['id', 'organization']
        extra_kwargs = {
            'organization': {'read_only': True},
        }

    def get_age(self, obj: Patient) -> int | None:
        if obj.birth_date:
            from datetime import date
            today = date.today()
            age = today.year - obj.birth_date.year
            if (today.month, today.day) < (obj.birth_date.month, obj.birth_date.day):
                age -= 1
            return age
        return None


# ── Appointment ────────────────────────────────────────────────────────

class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer for Appointment model."""

    id = serializers.UUIDField(source='pk', read_only=True)
    doctor = DoctorSerializer(read_only=True)
    doctor_id = serializers.UUIDField(write_only=True)
    patient = PatientSerializer(read_only=True)
    patient_id = serializers.UUIDField(write_only=True)
    
    # Use custom field that treats naive datetimes as America/Santo_Domingo
    start_at = TimeZoneDateTimeField()
    end_at = TimeZoneDateTimeField()

    class Meta:
        model = Appointment
        fields = [
            'id', 'organization', 'doctor', 'doctor_id', 'patient', 'patient_id',
            'start_at', 'end_at', 'appointment_type', 'reason',
            'status', 'notes', 'created_by', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'organization', 'created_by', 'created_at', 'updated_at']
        extra_kwargs = {
            'organization': {'read_only': True},
        }

    def validate(self, attrs: dict) -> dict:
        """Validate that end_at > start_at and check for appointment overlaps."""
        if attrs.get('end_at') and attrs.get('start_at') and attrs['end_at'] <= attrs['start_at']:
            raise serializers.ValidationError({'end_at': 'La hora de finalización debe ser posterior a la de inicio'})

        # Check for overlapping appointments on the same doctor
        request = self.context.get('request')
        
        # Get doctor_id - from attrs (for new appointments) or existing instance
        doctor_id = attrs.get('doctor_id') or getattr(self.instance, 'doctor_id', None)
        start_at = attrs.get('start_at')
        end_at = attrs.get('end_at')

        if doctor_id and start_at and end_at:
            # Check for overlaps with any user in context (or without authentication)
            overlapping = Appointment.objects.filter(
                doctor_id=doctor_id,
                status__in=['PROGRAMADA', 'CONFIRMADA', 'EN_CURSO'],
                start_at__lt=end_at,
                end_at__gt=start_at,
            )
            if self.instance:
                overlapping = overlapping.exclude(pk=self.instance.pk)

            if overlapping.exists():
                raise serializers.ValidationError({
                    'start_at': 'El médico ya tiene una cita en este horario',
                    'end_at': 'El médico ya tiene una cita en este horario',
                })

        # Call parent validate to ensure field validators run
        return super().validate(attrs)

    def create(self, validated_data: dict) -> Appointment:
        """Set organization and created_by from authenticated user."""
        # Extract foreign key IDs before they're used
        doctor_id = validated_data.pop('doctor_id', None)
        patient_id = validated_data.pop('patient_id', None)

        request = self.context.get('request')

        # Set organization from the requesting user's default organization
        if request and hasattr(request, 'user'):
            user_org = getattr(request.user, 'default_organization', None)
            if user_org:
                validated_data['organization'] = user_org
            else:
                # Fallback: get first org if user has no default
                from apps.core.organizations.models import Organization
                org = Organization.objects.first()
                if org:
                    validated_data['organization'] = org

        # Now set the actual foreign key objects/IDs for the parent create to use
        if doctor_id:
            validated_data['doctor_id'] = doctor_id
        if patient_id:
            validated_data['patient_id'] = patient_id

        return super().create(validated_data)
