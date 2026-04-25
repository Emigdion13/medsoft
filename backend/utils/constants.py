"""
Dominican Republic Medical Catalogs and Constants
"""

# Sex choices (from plan.md)
SEX_CHOICES = (
    ('M', 'Masculino'),
    ('F', 'Femenino'),
    ('O', 'Otro'),
)

# Identity types
IDENTITY_TYPES = (
    ('CEDULA', 'Cédula Dominicana'),
    ('PASAPORTE', 'Pasaporte'),
    ('OTRO', 'Otros'),
)

# Patient status
PATIENT_STATUS = (
    ('ACTIVO', 'Activo'),
    ('INACTIVO', 'Inactivo'),
    ('FALLECIDO', 'Fallecido'),
)

# Nationality (default)
DEFAULT_NATIONALITY = 'DOMINICANA'

# Appointment types
APPOINTMENT_TYPES = (
    ('CONSULTA', 'Consulta General'),
    ('CONTROL', 'Control Médico'),
    ('EMERGENCIA', 'Emergencia'),
    ('SEGUIMIENTO', 'Seguimiento'),
)

# Appointment status
APPOINTMENT_STATUS = (
    ('PROGRAMADA', 'Programada'),
    ('CONFIRMADA', 'Confirmada'),
    ('EN_CURSO', 'En curso'),
    ('COMPLETADA', 'Completada'),
    ('CANCELADA', 'Cancelada'),
    ('NO_ASISTIO', 'No asistió'),
)

# Encounter types
ENCOUNTER_TYPES = (
    ('AMBULATORIO', 'Ambulatorio'),
    ('INTERNAMIENTO', 'Internamiento'),
    ('EMERGENCIA', 'Emergencia'),
    ('TELECONSULTA', 'Teleconsulta'),
)

# Encounter status
ENCOUNTER_STATUS = (
    ('ABIERTO', 'Abierto'),
    ('CERRADO', 'Cerrado'),
    ('CANCELADO', 'Cancelado'),
)

# Clinical note types and status
NOTE_TYPES = (
    ('EVOLUCION', 'Evolución Clínica'),
    ('HISTORIA', 'Historia Clínica'),
    ('NOTA_ENFERMERIA', 'Nota de Enfermería'),
    ('NOTA_MEDICA', 'Nota Médica'),
)

CLINICAL_NOTE_STATUS = (
    ('BORRADOR', 'Borrador'),
    ('FIRMADA', 'Firmada'),
    ('ANULADA', 'Anulada'),
)

# Diagnosis types
DIAGNOSIS_TYPES = (
    ('PRINCIPAL', 'Principal'),
    ('SECUNDARIO', 'Secundario'),
    ('COMORBILIDAD', 'Comorbilidad'),
)

DIAGNOSIS_STATUS = (
    ('ACTIVO', 'Activo'),
    ('RESUELTO', 'Resuelto'),
    ('CANCELADO', 'Cancelado'),
)

# Prescription route
PRESCRIPTION_ROUTES = (
    ('ORAL', 'Oral'),
    ('IV', 'Intravenoso'),
    ('IM', 'Intramuscular'),
    ('TOPICA', 'Tópica'),
    ('INHALADA', 'Inhalada'),
    ('NASAL', 'Nasal'),
    ('OTICO', 'Ótico'),
    ('OCULAR', 'Ocular'),
)

# Prescription frequency patterns
PRESCRIPTION_FREQUENCIES = (
    ('CADA_4H', 'Cada 4 horas'),
    ('CADA_6H', 'Cada 6 horas'),
    ('CADA_8H', 'Cada 8 horas'),
    ('CADA_12H', 'Cada 12 horas'),
    ('CADA_24H', 'Cada 24 horas'),
    ('DIA_LABORABLE', 'Días laborables'),
    ('NOCHE', 'Noche'),
    ('TARDE', 'Tarde'),
    ('MANANA', 'Mañana'),
)

# Prescription status
PRESCRIPTION_STATUS = (
    ('ACTIVA', 'Activa'),
    ('SUSPENDIDA', 'Suspendida'),
    ('COMPLETADA', 'Completada'),
    ('CANCELADA', 'Cancelada'),
)

# Lab order priority
LAB_ORDER_PRIORITY = (
    ('NORMAL', 'Normal'),
    ('URGENTE', 'Urgente'),
)

# Lab order status
LAB_ORDER_STATUS = (
    ('PENDIENTE', 'Pendiente'),
    ('RECOLECTADA', 'Recolectada'),
    ('EN_PROCESO', 'En proceso'),
    ('COMPLETADA', 'Completada'),
    ('CANCELADA', 'Cancelada'),
)

# Lab result flags
LAB_RESULT_FLAGS = (
    ('NORMAL', 'Normal'),
    ('ANORMAL', 'Anormal'),
    ('CRITICO', 'Crítico'),
)

# Imaging order priority
IMAGING_ORDER_PRIORITY = (
    ('NORMAL', 'Normal'),
    ('URGENTE', 'Urgente'),
)

# Imaging order status
IMAGING_ORDER_STATUS = (
    ('PENDIENTE', 'Pendiente'),
    ('REALIZADA', 'Realizada'),
    ('EN_PROCESO', 'En proceso'),
    ('COMPLETADA', 'Completada'),
    ('CANCELADA', 'Cancelada'),
)

# Imaging report status
IMAGING_REPORT_STATUS = (
    ('BORRADOR', 'Borrador'),
    ('FIRMADA', 'Firmada'),
    ('ANULADA', 'Anulada'),
)

# Billing status
BILLING_STATUS = (
    ('PENDIENTE', 'Pendiente'),
    ('FACTURADO', 'Facturado'),
    ('PARCIAL', 'Parcial'),
    ('CANCELADO', 'Cancelado'),
)

# Service categories for billing
SERVICE_CATEGORIES = (
    ('CONSULTA', 'Consulta'),
    ('PROCEDIMIENTO', 'Procedimiento'),
    ('LAB', 'Laboratorio'),
    ('IMAGEN', 'Imagen'),
    ('INTERNAMIENTO', 'Internamiento'),
)

# Dominican Republic timezone
DOMINICAN_REPUBLIC_TZ = 'America/Santo_Domingo'

# Default language for DR
DEFAULT_LANGUAGE_CODE = 'es-DO'
