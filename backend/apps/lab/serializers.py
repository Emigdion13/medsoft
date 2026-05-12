from typing import Optional

from rest_framework import serializers

from .models import LabTestCatalog, LabOrder, LabOrderItem, LabResult


class LabTestCatalogSerializer(serializers.ModelSerializer):
    """Serializer for lab test catalog items."""

    id = serializers.UUIDField(source='pk', read_only=True)

    class Meta:
        model = LabTestCatalog
        fields = [
            'id',
            'code',
            'name',
            'sample_type',
            'unit',
            'reference_min',
            'reference_max',
            'is_active',
        ]
        read_only_fields = ['id']


class LabOrderItemSerializer(serializers.ModelSerializer):
    """Serializer for lab order items."""

    id = serializers.UUIDField(source='pk', read_only=True)
    lab_test_name = serializers.CharField(
        source='lab_test.name', read_only=True
    )
    lab_test_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = LabOrderItem
        fields = [
            'id',
            'lab_order',
            'lab_test',
            'lab_test_id',
            'lab_test_name',
            'status',
        ]
        read_only_fields = ['id']

    def create(self, validated_data: dict) -> LabOrderItem:
        """Create lab order item with lab_test from UUID."""
        lab_test_id = validated_data.pop('lab_test_id', None)
        if lab_test_id:
            try:
                from .models import LabTestCatalog
                lab_test = LabTestCatalog.objects.get(pk=lab_test_id)
                validated_data['lab_test'] = lab_test
            except LabTestCatalog.DoesNotExist:
                raise serializers.ValidationError(
                    {'lab_test_id': 'Invalid lab test ID'}
                )
        return super().create(validated_data)

    def update(self, instance: LabOrderItem, validated_data: dict) -> LabOrderItem:
        """Update lab order item with lab_test from UUID."""
        lab_test_id = validated_data.pop('lab_test_id', None)
        if lab_test_id:
            try:
                from .models import LabTestCatalog
                lab_test = LabTestCatalog.objects.get(pk=lab_test_id)
                validated_data['lab_test'] = lab_test
            except LabTestCatalog.DoesNotExist:
                raise serializers.ValidationError(
                    {'lab_test_id': 'Invalid lab test ID'}
                )
        return super().update(instance, validated_data)


class LabOrderSerializer(serializers.ModelSerializer):
    """Serializer for lab orders."""

    id = serializers.UUIDField(source='pk', read_only=True)
    patient_display = serializers.CharField(
        source='patient.__str__', read_only=True
    )
    doctor_display = serializers.CharField(
        source='doctor.__str__', read_only=True
    )
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = LabOrder
        fields = [
            'id',
            'organization',
            'encounter',
            'patient',
            'doctor',
            'patient_display',
            'doctor_display',
            'order_number',
            'priority',
            'status',
            'ordered_at',
            'expected_collection_date',
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

    def get_created_by_name(self, obj: LabOrder) -> Optional[str]:
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

    def create(self, validated_data: dict) -> LabOrder:
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
        return super().create(validated_data)

    def update(self, instance: LabOrder, validated_data: dict) -> LabOrder:
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['updated_by'] = request.user
        return super().update(instance, validated_data)


class LabResultSerializer(serializers.ModelSerializer):
    """Serializer for lab results."""

    id = serializers.UUIDField(source='pk', read_only=True)
    lab_order_item_display = serializers.CharField(
        source='lab_order_item.__str__', read_only=True
    )
    processed_by_name = serializers.SerializerMethodField()
    reviewed_by_name = serializers.SerializerMethodField()

    # Write-only fields for creating/updating
    processed_by_id = serializers.UUIDField(write_only=True, required=False)
    reviewed_by_id = serializers.UUIDField(write_only=True, required=False)
    lab_order_item_id = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = LabResult
        fields = [
            'id',
            'lab_order_item',
            'lab_order_item_display',
            'result_text',
            'result_numeric',
            'unit',
            'ref_min',
            'ref_max',
            'result_flag',
            'processed_by',
            'processed_by_name',
            'reviewed_by',
            'reviewed_by_name',
            'processed_at',
            'reviewed_at',
            'notes',
            'processed_by_id',
            'reviewed_by_id',
            'lab_order_item_id',
        ]
        read_only_fields = [
            'id',
            'processed_by',
            'reviewed_by',
            'processed_at',
            'reviewed_at',
        ]

    def get_processed_by_name(self, obj: LabResult) -> Optional[str]:
        if obj.processed_by:
            return f'{obj.processed_by.first_name} {obj.processed_by.last_name}'
        return None

    def get_reviewed_by_name(self, obj: LabResult) -> Optional[str]:
        if obj.reviewed_by:
            return f'{obj.reviewed_by.first_name} {obj.reviewed_by.last_name}'
        return None

    def validate_result_numeric(self, value) -> str:
        """Validate numeric result."""
        if value is not None and value < 0:
            raise serializers.ValidationError(
                'El valor numérico no puede ser negativo'
            )
        return str(value)

    def create(self, validated_data: dict) -> LabResult:
        request = self.context.get('request')
        
        # Handle lab_order_item_id from write_only field
        lab_order_item_id = validated_data.pop('lab_order_item_id', None)
        if lab_order_item_id:
            try:
                from .models import LabOrderItem
                item = LabOrderItem.objects.get(pk=lab_order_item_id)
                validated_data['lab_order_item'] = item
            except LabOrderItem.DoesNotExist:
                raise serializers.ValidationError(
                    {'lab_order_item_id': 'Invalid lab order item ID'}
                )
        
        # Handle processed_by_id from write_only field
        processed_by_id = validated_data.pop('processed_by_id', None)
        if processed_by_id:
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.get(pk=processed_by_id)
                validated_data['processed_by'] = user
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    {'processed_by_id': 'Invalid user ID'}
                )
        elif request and hasattr(request, 'user'):
            validated_data['processed_by'] = request.user
        
        # Handle reviewed_by_id from write_only field (for updates)
        reviewed_by_id = validated_data.pop('reviewed_by_id', None)
        if reviewed_by_id:
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.get(pk=reviewed_by_id)
                validated_data['reviewed_by'] = user
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    {'reviewed_by_id': 'Invalid user ID'}
                )
        
        return super().create(validated_data)

    def update(self, instance: LabResult, validated_data: dict) -> LabResult:
        """Handle reviewed_by_id for updating the reviewed_by field."""
        # Handle reviewed_by_id from write_only field (for updates)
        reviewed_by_id = validated_data.pop('reviewed_by_id', None)
        if reviewed_by_id:
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.get(pk=reviewed_by_id)
                validated_data['reviewed_by'] = user
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    {'reviewed_by_id': 'Invalid user ID'}
                )
        
        return super().update(instance, validated_data)


class LabOrderItemLookupSerializer(serializers.ModelSerializer):
    """Minimal lab order item lookup for nested display."""

    id = serializers.UUIDField(source='pk', read_only=True)
    lab_test_name = serializers.CharField(
        source='lab_test.name', read_only=True
    )

    class Meta:
        model = LabOrderItem
        fields = ['id', 'lab_test', 'lab_test_name', 'status']


class LabResultLookupSerializer(serializers.ModelSerializer):
    """Minimal lab result lookup for nested display."""

    id = serializers.UUIDField(source='pk', read_only=True)

    class Meta:
        model = LabResult
        fields = [
            'id',
            'result_text',
            'result_numeric',
            'result_flag',
        ]
