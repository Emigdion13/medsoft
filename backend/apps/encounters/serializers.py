from rest_framework import serializers

from apps.core.users.models import User
from apps.patients.models import Patient
from apps.doctors.models import Doctor
from apps.appointments.models import Appointment

from .models import Encounter, VitalSign


class PatientLookupSerializer(serializers.ModelSerializer):
    """Minimal patient lookup for nested display."""

    id = serializers.UUIDField(source='pk', read_only=True)

    class Meta:
        model = Patient
        fields = ['id', 'first_name', 'last_name', 'cedula']


class DoctorLookupSerializer(serializers.ModelSerializer):
    """Minimal doctor lookup for nested display."""

    id = serializers.UUIDField(source='pk', read_only=True)

    class Meta:
        model = Doctor
        fields = ['id', 'first_name', 'last_name', 'cedula']


class AppointmentLookupSerializer(serializers.ModelSerializer):
    """Minimal appointment lookup for nested display."""

    id = serializers.UUIDField(source='pk', read_only=True)

    class Meta:
        model = Appointment
        fields = ['id', 'start_at', 'end_at', 'reason']


class EncounterSerializer(serializers.ModelSerializer):
    """Full encounter serializer with nested patient/doctor/appointment lookups."""

    id = serializers.UUIDField(source='pk', read_only=True)
    patient = PatientLookupSerializer(read_only=True)
    doctor = DoctorLookupSerializer(read_only=True)
    appointment = AppointmentLookupSerializer(read_only=True)

    # Write-only IDs for FK relationships
    patient_id = serializers.UUIDField(write_only=True, required=True)
    doctor_id = serializers.UUIDField(write_only=True, required=True)
    appointment_id = serializers.UUIDField(
        write_only=True, required=False, allow_null=True, default=None
    )

    # Read-only computed fields
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Encounter
        fields = [
            'id',
            'organization',
            'patient',
            'doctor',
            'appointment',
            'patient_id',
            'doctor_id',
            'appointment_id',
            'encounter_type',
            'status',
            'start_at',
            'end_at',
            'chief_complaint',
            'room_number',
            'bed_number',
            'admission_source',
            'discharge_reason',
            'created_by_name',
            'updated_by_name',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'organization',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        ]

    def get_created_by_name(self, obj: Encounter) -> str | None:
        if obj.created_by:
            return f'{obj.created_by.first_name} {obj.created_by.last_name}'
        return None

    def get_updated_by_name(self, obj: Encounter) -> str | None:
        if obj.updated_by:
            return f'{obj.updated_by.first_name} {obj.updated_by.last_name}'
        return None

    def validate(self, attrs: dict) -> dict:
        """Validate end_at > start_at when both are present."""
        if (
            attrs.get('end_at')
            and attrs.get('start_at')
            and attrs['end_at'] <= attrs['start_at']
        ):
            raise serializers.ValidationError({
                'end_at': 'La hora de finalización debe ser posterior a la de inicio',
            })
        return super().validate(attrs)

    def create(self, validated_data: dict) -> Encounter:
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
            validated_data['updated_by'] = request.user
        return super().create(validated_data)

    def update(self, instance: Encounter, validated_data: dict) -> Encounter:
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['updated_by'] = request.user
        return super().update(instance, validated_data)


class VitalSignSerializer(serializers.ModelSerializer):
    """Serializer for vital signs linked to an encounter."""

    id = serializers.UUIDField(source='pk', read_only=True)
    recorded_by_name = serializers.SerializerMethodField()
    encounter_display = serializers.CharField(
        source='encounter.__str__', read_only=True
    )

    class Meta:
        model = VitalSign
        fields = [
            'id',
            'encounter',
            'recorded_by',
            'recorded_by_name',
            'recorded_at',
            'temperature_c',
            'bp_systolic',
            'bp_diastolic',
            'heart_rate',
            'respiratory_rate',
            'oxygen_saturation',
            'weight_kg',
            'height_cm',
            'bmi',
            'glucose_mg_dl',
            'notes',
            'encounter_display',
        ]
        read_only_fields = ['id', 'recorded_at']

    def get_recorded_by_name(self, obj: VitalSign) -> str | None:
        if obj.recorded_by:
            return f'{obj.recorded_by.first_name} {obj.recorded_by.last_name}'
        return None

    def validate(self, attrs: dict) -> dict:
        """Auto-calculate BMI from weight and height when both are present."""
        weight = attrs.get('weight_kg')
        height = attrs.get('height_cm')
        if weight is not None and height is not None and height > 0:
            height_m = height / 100.0
            attrs['bmi'] = round(weight / (height_m ** 2), 2)
        return super().validate(attrs)

    def create(self, validated_data: dict) -> VitalSign:
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['recorded_by'] = request.user
        return super().create(validated_data)
