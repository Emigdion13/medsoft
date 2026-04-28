from rest_framework import serializers

from apps.core.users.models import User
from apps.core.organizations.models import Organization
from apps.doctors.models import Specialty, Doctor
from apps.patients.models import Patient
from apps.appointments.models import Appointment


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
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match'})
        
        # Get the organization for uniqueness checks
        org = Organization.objects.first()
        if not org:
            raise serializers.ValidationError({'organization': 'No organization found. Please contact support.'})
        
        # Check for existing user with same username in this organization
        if User.objects.filter(organization=org, username=attrs['username']).exists():
            raise serializers.ValidationError({'username': 'A user with this username already exists in this organization'})
        
        # Check for existing user with same email in this organization  
        if User.objects.filter(organization=org, email=attrs['email'].lower()).exists():
            raise serializers.ValidationError({'email': 'A user with this email already exists in this organization'})
        
        return attrs

    def create(self, validated_data: dict) -> User:
        """Create user with hashed password."""
        # Get the first organization (there should be one from initial setup)
        org = Organization.objects.first()
        if not org:
            raise serializers.ValidationError({'organization': 'No organization found. Please contact support.'})
        
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
        """Validate that end_at > start_at."""
        if attrs.get('end_at') and attrs.get('start_at') and attrs['end_at'] <= attrs['start_at']:
            raise serializers.ValidationError({'end_at': 'End time must be after start time'})
        return attrs

    def create(self, validated_data: dict) -> Appointment:
        """Set created_by from authenticated user."""
        validated_data.pop('doctor_id')
        validated_data.pop('patient_id')
        request = self.context['request']
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
        return super().create(validated_data)
