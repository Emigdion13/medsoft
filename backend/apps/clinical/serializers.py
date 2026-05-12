from typing import Optional

from rest_framework import serializers

from .models import ClinicalNote, Diagnosis, Prescription


class ClinicalNoteSerializer(serializers.ModelSerializer):
    """Serializer for clinical notes."""

    id = serializers.UUIDField(source='pk', read_only=True)
    encounter_display = serializers.CharField(
        source='encounter.__str__', read_only=True
    )
    doctor_display = serializers.CharField(
        source='doctor.__str__', read_only=True
    )
    signed_by_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ClinicalNote
        fields = [
            'id',
            'encounter',
            'doctor',
            'encounter_display',
            'doctor_display',
            'note_type',
            'content',
            'status',
            'signed_by',
            'signed_by_name',
            'signed_at',
            'content_hash',
            'signature_blob',
            'created_by',
            'created_by_name',
            'updated_by',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'signed_by',
            'signed_at',
            'content_hash',
            'signature_blob',
            'created_by',
            'created_at',
            'updated_at',
        ]

    def get_signed_by_name(self, obj: ClinicalNote) -> Optional[str]:
        if obj.signed_by:
            return f'{obj.signed_by.first_name} {obj.signed_by.last_name}'
        return None

    def get_created_by_name(self, obj: ClinicalNote) -> Optional[str]:
        if obj.created_by:
            return f'{obj.created_by.first_name} {obj.created_by.last_name}'
        return None

    def validate(self, attrs: dict) -> dict:
        """Validate note status requires signature."""
        status = attrs.get('status')
        signed_by = attrs.get('signed_by')

        if status == 'FIRMADA' and not signed_by:
            raise serializers.ValidationError({
                'signed_by': 'La nota debe tener un firmante cuando está marcada como Firmada',
            })

        return super().validate(attrs)

    def create(self, validated_data: dict) -> ClinicalNote:
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
        return super().create(validated_data)


class ClinicalNoteLookupSerializer(serializers.ModelSerializer):
    """Minimal clinical note lookup for nested display."""

    id = serializers.UUIDField(source='pk', read_only=True)

    class Meta:
        model = ClinicalNote
        fields = ['id', 'note_type', 'status', 'content_hash', 'signed_at']


class DiagnosisSerializer(serializers.ModelSerializer):
    """Serializer for diagnosis records (ICD-10)."""

    id = serializers.UUIDField(source='pk', read_only=True)
    encounter_display = serializers.CharField(
        source='encounter.__str__', read_only=True
    )
    recorded_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Diagnosis
        fields = [
            'id',
            'encounter',
            'encounter_display',
            'icd10_code',
            'description',
            'diagnosis_type',
            'is_primary',
            'status',
            'recorded_by',
            'recorded_by_name',
            'recorded_at',
        ]
        read_only_fields = ['id', 'recorded_by', 'recorded_at']

    def get_recorded_by_name(self, obj: Diagnosis) -> Optional[str]:
        if obj.recorded_by:
            return f'{obj.recorded_by.first_name} {obj.recorded_by.last_name}'
        return None

    def validate_is_primary(self, value: bool) -> bool:
        """Ensure only one primary diagnosis per encounter."""
        return value

    def create(self, validated_data: dict) -> Diagnosis:
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['recorded_by'] = request.user
        return super().create(validated_data)


class DiagnosisLookupSerializer(serializers.ModelSerializer):
    """Minimal diagnosis lookup for nested display."""

    id = serializers.UUIDField(source='pk', read_only=True)

    class Meta:
        model = Diagnosis
        fields = ['id', 'icd10_code', 'description', 'diagnosis_type']


class PrescriptionSerializer(serializers.ModelSerializer):
    """Serializer for prescription records."""

    id = serializers.UUIDField(source='pk', read_only=True)
    encounter_display = serializers.CharField(
        source='encounter.__str__', read_only=True
    )
    prescribed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Prescription
        fields = [
            'id',
            'encounter',
            'encounter_display',
            'prescribed_by',
            'prescribed_by_name',
            'medication_name',
            'medication_code',
            'dose',
            'frequency',
            'route',
            'duration_days',
            'quantity',
            'instructions',
            'status',
            'prescribed_at',
        ]
        read_only_fields = ['id', 'prescribed_by', 'prescribed_at']

    def get_prescribed_by_name(self, obj: Prescription) -> Optional[str]:
        if obj.prescribed_by:
            return f'{obj.prescribed_by.first_name} {obj.prescribed_by.last_name}'
        return None

    def validate_duration_days(self, value: int) -> int:
        """Ensure duration is positive when provided."""
        if value is not None and value <= 0:
            raise serializers.ValidationError(
                'La duración debe ser mayor a 0 días'
            )
        return value

    def create(self, validated_data: dict) -> Prescription:
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['prescribed_by'] = request.user
        return super().create(validated_data)


class PrescriptionLookupSerializer(serializers.ModelSerializer):
    """Minimal prescription lookup for nested display."""

    id = serializers.UUIDField(source='pk', read_only=True)

    class Meta:
        model = Prescription
        fields = ['id', 'medication_name', 'dose', 'frequency', 'route', 'status']
