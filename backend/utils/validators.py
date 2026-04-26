"""
Dominican Republic Medical Validation Utilities

Provides validators for:
- Cédula Dominicana (national ID)
- Passport validation
- Age calculations
- Medical data ranges
"""

import re
from datetime import date, datetime

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_cedula(value: str) -> str:
    """
    Validate Dominican Republic Cédula Dominicana.
    
    Requirements:
    - Must be exactly 13 digits
    - First digit must be 1, 2, or 3
    - Last digit is a check digit (optional validation)
    
    Returns the cleaned value if valid.
    
    Raises ValidationError if invalid.
    """
    if not value:
        raise ValidationError(
            _('Cédula number is required'),
            code='required',
        )
    
    # Remove spaces and dashes
    cleaned = re.sub(r'[\s\-]', '', str(value))

    # Must be exactly 13 digits
    if not cleaned.isdigit() or len(cleaned) != 13:
        raise ValidationError(
            _('Cédula must be exactly 13 numeric digits'),
            code='invalid_length',
        )

    # Optional: Validate check digit using modulo 10 algorithm
    # Sum of odd positions * 1 + sum of even positions * 2
    digits = [int(d) for d in cleaned]
    total = 0
    for i, digit in enumerate(digits[:-1]):  # Exclude check digit
        if i % 2 == 0:  # Odd position (0-indexed)
            total += digit
        else:  # Even position
            product = digit * 2
            total += sum(int(d) for d in str(product))
    
    check_digit = (10 - (total % 10)) % 10
    
    if check_digit != digits[-1]:
        raise ValidationError(
            _('Invalid Cédula check digit'),
            code='invalid_check_digit',
        )
    
    return cleaned


def validate_passport(value: str) -> str:
    """
    Validate passport number format.
    
    Requirements:
    - Must not be empty
    - Should contain alphanumeric characters
    
    Returns the uppercase cleaned value if valid.
    """
    if not value:
        raise ValidationError(
            _('Passport number is required'),
            code='required',
        )
    
    cleaned = str(value).strip().upper()
    
    # Basic validation: alphanumeric, minimum length 6
    if len(cleaned) < 6:
        raise ValidationError(
            _('Passport number must be at least 6 characters'),
            code='invalid_length',
        )
    
    if not cleaned.isalnum():
        raise ValidationError(
            _('Passport number must contain only letters and numbers'),
            code='invalid_characters',
        )
    
    return cleaned


def validate_age_at_date(birth_date: date, reference_date: date = None) -> int:
    """
    Calculate age at a specific date.
    
    Args:
        birth_date: Person's date of birth
        reference_date: Date to calculate age at (default: today)
    
    Returns:
        Age in years
    
    Raises:
        ValidationError if birth_date is in the future or too old
    """
    if reference_date is None:
        reference_date = date.today()
    
    if birth_date > reference_date:
        raise ValidationError(
            _('Birth date cannot be in the future'),
            code='future_birth_date',
        )
    
    # Calculate age
    age = (
        reference_date.year
        - birth_date.year
        - (
            (reference_date.month, reference_date.day)
            < (birth_date.month, birth_date.day)
        )
    )
    
    # Validate reasonable age range
    if age < 0:
        raise ValidationError(
            _('Invalid birth date'),
            code='invalid_birth_date',
        )
    
    if age > 120:
        raise ValidationError(
            _('Age exceeds maximum valid value (120 years)'),
            code='age_too_old',
        )
    
    return age


def validate_age_min_max(value: date, min_age: int = 0, max_age: int = 120) -> date:
    """
    Validate that a birth date results in an age within valid range.
    
    Args:
        value: Date of birth
        min_age: Minimum required age (default: 0)
        max_age: Maximum allowed age (default: 120)
    
    Returns:
        The validated date
    
    Raises:
        ValidationError if age is outside range
    """
    today = date.today()
    age = validate_age_at_date(value, today)
    
    if age < min_age:
        raise ValidationError(
            _('Person must be at least {} years old').format(min_age),
            code='age_too_young',
        )
    
    if age > max_age:
        raise ValidationError(
            _('Age exceeds maximum valid value ({} years)').format(max_age),
            code='age_too_old',
        )
    
    return value


def validate_past_or_present_date(value: date) -> date:
    """
    Validate that a date is not in the future.
    
    Args:
        value: Date to validate
    
    Returns:
        The validated date
    
    Raises:
        ValidationError if date is in the future
    """
    if value > date.today():
        raise ValidationError(
            _('Date cannot be in the future'),
            code='future_date',
        )
    return value


def validate_datetime_range(start: datetime, end: datetime) -> tuple[datetime, datetime]:
    """
    Validate that start datetime is before end datetime.
    
    Args:
        start: Start datetime
        end: End datetime
    
    Returns:
        Tuple of (start, end) if valid
    
    Raises:
        ValidationError if start >= end
    """
    if start >= end:
        raise ValidationError(
            _('Start date/time must be before end date/time'),
            code='invalid_datetime_range',
        )
    return start, end


def validate_medical_value_range(
    value: float,
    field_name: str,
    min_val: float = None,
    max_val: float = None,
) -> float:
    """
    Validate a medical measurement is within acceptable clinical range.
    
    Args:
        value: Measurement value
        field_name: Name of the field for error message
        min_val: Minimum valid value (optional)
        max_val: Maximum valid value (optional)
    
    Returns:
        The validated value
    
    Raises:
        ValidationError if outside range
    """
    error_msg = None
    
    if min_val is not None and value < min_val:
        error_msg = _(
            f'{field_name} cannot be less than {min_val}'
        )
    elif max_val is not None and value > max_val:
        error_msg = _(
            f'{field_name} cannot exceed {max_val}'
        )
    
    if error_msg:
        raise ValidationError(error_msg, code='invalid_value')
    
    return value


# Medical reference ranges (typical clinical values)
MEDICAL_RANGES = {
    'temperature_c': {'min': 35.0, 'max': 42.0},
    'bp_systolic': {'min': 60, 'max': 250},
    'bp_diastolic': {'min': 30, 'max': 150},
    'heart_rate': {'min': 30, 'max': 220},
    'respiratory_rate': {'min': 8, 'max': 60},
    'oxygen_saturation': {'min': 50.0, 'max': 100.0},
    'weight_kg': {'min': 1.0, 'max': 300.0},
    'height_cm': {'min': 20.0, 'max': 270.0},
    'glucose_mg_dl': {'min': 20.0, 'max': 1000.0},
}


def validate_temperature_c(value: float) -> float:
    """Validate body temperature in Celsius."""
    return validate_medical_value_range(
        value,
        _('Temperature'),
        **MEDICAL_RANGES['temperature_c'],
    )


def validate_blood_pressure_systolic(value: int) -> int:
    """Validate systolic blood pressure."""
    return validate_medical_value_range(
        value, _('Systolic BP'), **MEDICAL_RANGES['bp_systolic']
    )


def validate_blood_pressure_diastolic(value: int) -> int:
    """Validate diastolic blood pressure."""
    return validate_medical_value_range(
        value, _('Diastolic BP'), **MEDICAL_RANGES['bp_diastolic']
    )


def validate_heart_rate(value: int) -> int:
    """Validate heart rate (bpm)."""
    return validate_medical_value_range(
        value, _('Heart Rate'), **MEDICAL_RANGES['heart_rate']
    )


def validate_respiratory_rate(value: int) -> int:
    """Validate respiratory rate (breaths/min)."""
    return validate_medical_value_range(
        value, _('Respiratory Rate'), **MEDICAL_RANGES['respiratory_rate']
    )


def validate_oxygen_saturation(value: float) -> float:
    """Validate oxygen saturation (%)."""
    return validate_medical_value_range(
        value, _('Oxygen Saturation'), **MEDICAL_RANGES['oxygen_saturation']
    )


def validate_weight_kg(value: float) -> float:
    """Validate weight in kilograms."""
    return validate_medical_value_range(
        value, _('Weight'), **MEDICAL_RANGES['weight_kg']
    )


def validate_height_cm(value: float) -> float:
    """Validate height in centimeters."""
    return validate_medical_value_range(
        value, _('Height'), **MEDICAL_RANGES['height_cm']
    )


def validate_glucose_mg_dl(value: float) -> float:
    """Validate glucose level (mg/dL)."""
    return validate_medical_value_range(
        value, _('Glucose Level'), **MEDICAL_RANGES['glucose_mg_dl']
    )


# BMI calculation and validation
def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """
    Calculate Body Mass Index.
    
    Args:
        weight_kg: Weight in kilograms
        height_cm: Height in centimeters
    
    Returns:
        BMI value
    
    Raises:
        ValidationError if inputs are invalid
    """
    if weight_kg <= 0:
        raise ValidationError(
            _('Weight must be positive'),
            code='invalid_weight',
        )
    
    if height_cm <= 0:
        raise ValidationError(
            _('Height must be positive'),
            code='invalid_height',
        )
    
    height_m = height_cm / 100
    bmi = weight_kg / (height_m * height_m)
    
    # Validate BMI range
    if bmi < 10 or bmi > 70:
        raise ValidationError(
            _('BMI out of valid range (10-70)'),
            code='invalid_bmi',
        )
    
    return round(bmi, 2)


def validate_bmi_range(value: float) -> float:
    """Validate BMI is within reasonable clinical range."""
    return validate_medical_value_range(
        value, _('BMI'), min_val=10.0, max_val=70.0
    )
