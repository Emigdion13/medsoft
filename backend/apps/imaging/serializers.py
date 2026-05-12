from typing import Optional

from rest_framework import serializers

from .models import ImagingTypeCatalog, ImagingOrder, ImagingReport, ImagingFile


class ImagingTypeCatalogSerializer(serializers.ModelSerializer):
    """Serializer for imaging type catalog."""

    id = serializers.UUIDField(source='pk', read_only=True)

    class Meta:
        model = ImagingTypeCatalog
        fields = [
            'id',
            'code',
            'name',
            'modality',
            'is_active',
        ]
        read_only_fields = ['id']


class ImagingOrderSerializer(serializers.ModelSerializer):
    """Serializer for imaging orders."""

    id = serializers.UUIDField(source='pk', read_only=True)
    patient_display = serializers.CharField(
        source='patient.__str__', read_only=True
    )
    doctor_display = serializers.CharField(
        source='doctor.__str__', read_only=True
    )
    imaging_type_name = serializers.CharField(
        source='imaging_type.name', read_only=True
    )
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ImagingOrder
        fields = [
            'id',
            'organization',
            'encounter',
            'patient',
            'doctor',
            'patient_display',
            'doctor_display',
            'imaging_type',
            'imaging_type_name',
            'order_number',
            'priority',
            'status',
            'clinical_indication',
            'ordered_at',
            'expected_date',
            'notes',
            'created_by',
            'created_by_name',
            'updated_by',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'organization',
            'created_by',
            'updated_by',
            'ordered_at',
            'created_at',
            'updated_at',
        ]

    def get_created_by_name(self, obj: ImagingOrder) -> Optional[str]:
        if obj.created_by:
            return f'{obj.created_by.first_name} {obj.created_by.last_name}'
        return None

    def validate_order_number(self, value: str) -> str:
        """Validate order number format."""
        if value and len(value.strip()) < 6:
            raise serializers.ValidationError(
                'El número de orden debe tener al menos 6 caracteres'
            )
        return value.strip()

    def create(self, validated_data: dict) -> ImagingOrder:
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
        return super().create(validated_data)

    def update(self, instance: ImagingOrder, validated_data: dict) -> ImagingOrder:
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['updated_by'] = request.user
        return super().update(instance, validated_data)


class ImagingReportSerializer(serializers.ModelSerializer):
    """Serializer for imaging reports."""

    id = serializers.UUIDField(source='pk', read_only=True)
    imaging_order_display = serializers.CharField(
        source='imaging_order.__str__', read_only=True
    )
    technician_name = serializers.SerializerMethodField()
    radiologist_name = serializers.SerializerMethodField()

    class Meta:
        model = ImagingReport
        fields = [
            'id',
            'imaging_order',
            'imaging_order_display',
            'technician_user',
            'technician_name',
            'radiologist_user',
            'radiologist_name',
            'performed_at',
            'findings',
            'impression',
            'recommendations',
            'status',
            'signed_at',
            'content_hash',
            'signature_blob',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'technician_user',
            'radiologist_user',
            'performed_at',
            'signed_at',
            'content_hash',
            'signature_blob',
            'created_at',
            'updated_at',
        ]

    def get_technician_name(self, obj: ImagingReport) -> Optional[str]:
        if obj.technician_user:
            return f'{obj.technician_user.first_name} {obj.technician_user.last_name}'
        return None

    def get_radiologist_name(self, obj: ImagingReport) -> Optional[str]:
        if obj.radiologist_user:
            return f'{obj.radiologist_user.first_name} {obj.radiologist_user.last_name}'
        return None

    def validate(self, attrs: dict) -> dict:
        """Validate report status requires signature."""
        status = attrs.get('status')
        radiologist_user = attrs.get('radiologist_user')

        if status == 'FIRMADA' and not radiologist_user:
            raise serializers.ValidationError({
                'radiologist_user': 'El informe debe tener un radiólogo firmante cuando está marcado como Firmada',
            })

        return super().validate(attrs)

    def create(self, validated_data: dict) -> ImagingReport:
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['technician_user'] = request.user
        return super().create(validated_data)


class ImagingFileSerializer(serializers.ModelSerializer):
    """Serializer for imaging files (DICOM/PDF/JPG)."""

    id = serializers.UUIDField(source='pk', read_only=True)
    imaging_order_display = serializers.CharField(
        source='imaging_order.__str__', read_only=True
    )
    uploaded_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ImagingFile
        fields = [
            'id',
            'imaging_order',
            'imaging_order_display',
            'file_name',
            'file_type',
            'storage_uri',
            'size_bytes',
            'sha256',
            'uploaded_by',
            'uploaded_by_name',
            'uploaded_at',
        ]
        read_only_fields = [
            'id',
            'uploaded_by',
            'uploaded_at',
        ]

    def get_uploaded_by_name(self, obj: ImagingFile) -> Optional[str]:
        if obj.uploaded_by:
            return f'{obj.uploaded_by.first_name} {obj.uploaded_by.last_name}'
        return None

    def create(self, validated_data: dict) -> ImagingFile:
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['uploaded_by'] = request.user
        return super().create(validated_data)


class ImagingOrderLookupSerializer(serializers.ModelSerializer):
    """Minimal imaging order lookup for nested display."""

    id = serializers.UUIDField(source='pk', read_only=True)
    imaging_type_name = serializers.CharField(
        source='imaging_type.name', read_only=True
    )

    class Meta:
        model = ImagingOrder
        fields = ['id', 'order_number', 'imaging_type', 'imaging_type_name', 'status']


class ImagingReportLookupSerializer(serializers.ModelSerializer):
    """Minimal imaging report lookup for nested display."""

    id = serializers.UUIDField(source='pk', read_only=True)

    class Meta:
        model = ImagingReport
        fields = ['id', 'status', 'signed_at']
