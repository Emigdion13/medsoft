# Plan de Esquema de Base de Datos — MediSoft (República Dominicana)

## Contexto
Se definirá un esquema **DB-first** para que el coder implemente MediSoft con una base sólida, auditada y escalable.

Requisitos confirmados:
- Una sola clínica/sede por ahora (single-tenant práctico, multi-tenant ready).
- Facturación/fiscal completa se hace después, pero dejar estructura preparada.
- Laboratorio e imágenes incluidos en v1.
- Soporte de ambulatorio e internamiento.
- Diseño en español (es-DO).

Estado del repositorio:
- Solo existen `README.md`, `LICENSE`, `.gitignore`, `plan.md`.

---

## Convenciones globales del esquema

### Tipos y convenciones
- Motor: PostgreSQL 15.
- PK: `uuid` con `gen_random_uuid()`.
- Fechas: `timestamptz`.
- Trazabilidad: `created_at`, `updated_at` en tablas operativas.
- Soft delete: `deleted_at` nullable (en tablas operativas).
- FKs con `on delete restrict` por defecto para proteger historia clínica.

### Reglas de seguridad e integridad
- Todo acceso clínico sensible debe generar evento en `audit_logs` y/o `access_logs`.
- Entidades firmables (nota clínica, reporte de imagen) son inmutables tras firma.
- Índices parciales para registros activos (`deleted_at is null`).

### Catálogos/enum recomendados
- `sexo`: `M`, `F`, `O`.
- `tipo_identidad`: `CEDULA`, `PASAPORTE`, `OTRO`.
- `tipo_encuentro`: `AMBULATORIO`, `INTERNAMIENTO`, `EMERGENCIA`, `TELECONSULTA`.
- `estado_cita`: `PROGRAMADA`, `CONFIRMADA`, `EN_CURSO`, `COMPLETADA`, `CANCELADA`, `NO_ASISTIO`.
- `estado_encuentro`: `ABIERTO`, `CERRADO`, `CANCELADO`.
- `estado_firma`: `BORRADOR`, `FIRMADA`, `ANULADA`.
- `prioridad`: `NORMAL`, `URGENTE`.

---

## Esquema tabla por tabla

## 1) Núcleo organizacional y seguridad

### 1. `organizations`
**Propósito:** datos de la clínica (1 registro en v1).

**Columnas**
- `id uuid pk default gen_random_uuid()`
- `name varchar(160) not null`
- `trade_name varchar(160) null`
- `rnc varchar(20) null`
- `phone varchar(25) null`
- `email varchar(255) null`
- `address text null`
- `province varchar(120) null`
- `municipality varchar(120) null`
- `timezone varchar(64) not null default 'America/Santo_Domingo'`
- `language_code varchar(10) not null default 'es-DO'`
- `is_active boolean not null default true`
- `created_at timestamptz not null default now()`
- `updated_at timestamptz not null default now()`

**Restricciones/índices**
- `unique (rnc) where rnc is not null`
- Índice: `(is_active)`

---

### 2. `users`
**Propósito:** identidad de usuarios del sistema (auth).

**Columnas**
- `id uuid pk`
- `organization_id uuid not null fk -> organizations(id)`
- `username varchar(150) not null`
- `email varchar(255) not null`
- `full_name varchar(200) not null`
- `password_hash varchar(255) not null`
- `is_active boolean not null default true`
- `last_login_at timestamptz null`
- `created_at timestamptz not null default now()`
- `updated_at timestamptz not null default now()`
- `deleted_at timestamptz null`

**Restricciones/índices**
- `unique (organization_id, username) where deleted_at is null`
- `unique (organization_id, email) where deleted_at is null`
- Índices: `(organization_id)`, `(is_active)`, `(deleted_at)`

---

### 3. `roles`
**Propósito:** roles RBAC.

**Columnas**
- `id uuid pk`
- `organization_id uuid not null fk -> organizations(id)`
- `code varchar(50) not null` (DOCTOR, NURSE, SECRETARY, RECEPTIONIST, ADMIN, LAB_TECH, IMG_TECH)
- `name varchar(100) not null`
- `description text null`
- `is_active boolean not null default true`
- `created_at timestamptz not null default now()`

**Restricciones/índices**
- `unique (organization_id, code)`
- Índices: `(organization_id)`, `(is_active)`

---

### 4. `permissions`
**Propósito:** permisos granulares por módulo/recurso/acción.

**Columnas**
- `id uuid pk`
- `code varchar(120) not null unique` (ej. `patients.view`, `clinical.sign_note`)
- `module varchar(60) not null`
- `resource varchar(80) not null`
- `action varchar(40) not null`
- `description text null`

**Índices**
- `(module)`, `(resource, action)`

---

### 5. `user_roles`
**Propósito:** relación usuarios-roles.

**Columnas**
- `id uuid pk`
- `user_id uuid not null fk -> users(id)`
- `role_id uuid not null fk -> roles(id)`
- `assigned_at timestamptz not null default now()`
- `assigned_by uuid null fk -> users(id)`

**Restricciones**
- `unique (user_id, role_id)`

---

### 6. `role_permissions`
**Propósito:** relación roles-permisos.

**Columnas**
- `id uuid pk`
- `role_id uuid not null fk -> roles(id)`
- `permission_id uuid not null fk -> permissions(id)`
- `assigned_at timestamptz not null default now()`

**Restricciones**
- `unique (role_id, permission_id)`

---

### 7. `audit_logs`
**Propósito:** auditoría de cambios y eventos críticos.

**Columnas**
- `id uuid pk`
- `organization_id uuid not null fk -> organizations(id)`
- `user_id uuid null fk -> users(id)`
- `entity_type varchar(80) not null`
- `entity_id uuid not null`
- `action varchar(40) not null` (CREATE, UPDATE, DELETE, SIGN, etc.)
- `before_data jsonb null`
- `after_data jsonb null`
- `reason text null`
- `ip inet null`
- `user_agent text null`
- `created_at timestamptz not null default now()`

**Índices**
- `(organization_id, created_at desc)`
- `(entity_type, entity_id, created_at desc)`
- `(user_id, created_at desc)`

**Regla:** tabla append-only (no update/delete).

---

### 8. `access_logs`
**Propósito:** trazabilidad de acceso a recursos sensibles.

**Columnas**
- `id uuid pk`
- `organization_id uuid not null fk -> organizations(id)`
- `user_id uuid not null fk -> users(id)`
- `resource_type varchar(80) not null`
- `resource_id uuid not null`
- `access_type varchar(40) not null` (VIEW, EXPORT, PRINT, DOWNLOAD)
- `granted boolean not null default true`
- `denied_reason text null`
- `ip inet null`
- `created_at timestamptz not null default now()`

**Índices**
- `(organization_id, created_at desc)`
- `(resource_type, resource_id, created_at desc)`
- `(user_id, created_at desc)`

---

## 2) Identidad clínica (pacientes y doctores)

### 9. `patients`
**Propósito:** registro maestro de pacientes.

**Columnas**
- `id uuid pk`
- `organization_id uuid not null fk -> organizations(id)`
- `identity_type varchar(20) not null default 'CEDULA'`
- `cedula varchar(20) null`
- `passport_number varchar(40) null`
- `first_name varchar(120) not null`
- `last_name varchar(120) not null`
- `birth_date date not null`
- `sex varchar(1) not null`
- `nationality varchar(80) not null default 'DOMINICANA'`
- `phone_primary varchar(25) null`
- `phone_secondary varchar(25) null`
- `email varchar(255) null`
- `address text null`
- `province varchar(120) null`
- `municipality varchar(120) null`
- `blood_type varchar(5) null`
- `allergies text null`
- `chronic_conditions text null`
- `emergency_contact_name varchar(150) null`
- `emergency_contact_phone varchar(25) null`
- `emergency_contact_relation varchar(60) null`
- `ars_provider varchar(120) null` (placeholder v2)
- `ars_affiliation_number varchar(60) null` (placeholder v2)
- `status varchar(20) not null default 'ACTIVO'`
- `created_by uuid null fk -> users(id)`
- `updated_by uuid null fk -> users(id)`
- `created_at timestamptz not null default now()`
- `updated_at timestamptz not null default now()`
- `deleted_at timestamptz null`

**Restricciones/índices**
- `check (sex in ('M','F','O'))`
- `check (identity_type in ('CEDULA','PASAPORTE','OTRO'))`
- `check (status in ('ACTIVO','INACTIVO','FALLECIDO'))`
- `check (birth_date <= current_date)`
- `unique (organization_id, cedula) where cedula is not null and deleted_at is null`
- `unique (organization_id, passport_number) where passport_number is not null and deleted_at is null`
- Índices: `(organization_id)`, `(last_name, first_name)`, `(phone_primary)`, `(deleted_at)`

---

### 10. `specialties`
**Propósito:** catálogo de especialidades médicas.

**Columnas**
- `id uuid pk`
- `code varchar(40) not null unique`
- `name varchar(120) not null`
- `description text null`
- `is_active boolean not null default true`

**Índices**
- `(is_active)`

---

### 11. `doctors`
**Propósito:** profesionales médicos.

**Columnas**
- `id uuid pk`
- `organization_id uuid not null fk -> organizations(id)`
- `user_id uuid null fk -> users(id)`
- `cedula varchar(20) not null`
- `license_number varchar(60) not null`
- `medical_college_number varchar(60) null`
- `first_name varchar(120) not null`
- `last_name varchar(120) not null`
- `specialty_main_id uuid not null fk -> specialties(id)`
- `phone varchar(25) null`
- `email varchar(255) null`
- `office_room varchar(40) null`
- `is_active boolean not null default true`
- `created_at timestamptz not null default now()`
- `updated_at timestamptz not null default now()`
- `deleted_at timestamptz null`

**Restricciones/índices**
- `unique (organization_id, cedula) where deleted_at is null`
- `unique (organization_id, license_number) where deleted_at is null`
- Índices: `(organization_id)`, `(specialty_main_id)`, `(is_active)`, `(deleted_at)`

---

### 12. `doctor_specialties`
**Propósito:** N:M doctor-especialidad.

**Columnas**
- `id uuid pk`
- `doctor_id uuid not null fk -> doctors(id)`
- `specialty_id uuid not null fk -> specialties(id)`
- `is_primary boolean not null default false`

**Restricciones**
- `unique (doctor_id, specialty_id)`

---

## 3) Agenda y encuentros clínicos

### 13. `appointments`
**Propósito:** agenda médica.

**Columnas**
- `id uuid pk`
- `organization_id uuid not null fk -> organizations(id)`
- `patient_id uuid not null fk -> patients(id)`
- `doctor_id uuid not null fk -> doctors(id)`
- `start_at timestamptz not null`
- `end_at timestamptz not null`
- `appointment_type varchar(40) not null default 'CONSULTA'`
- `reason text null`
- `status varchar(20) not null default 'PROGRAMADA'`
- `notes text null`
- `created_by uuid null fk -> users(id)`
- `updated_by uuid null fk -> users(id)`
- `created_at timestamptz not null default now()`
- `updated_at timestamptz not null default now()`
- `deleted_at timestamptz null`

**Restricciones/índices**
- `check (end_at > start_at)`
- `check (status in ('PROGRAMADA','CONFIRMADA','EN_CURSO','COMPLETADA','CANCELADA','NO_ASISTIO'))`
- Índices: `(doctor_id, start_at)`, `(patient_id, start_at)`, `(status)`, `(deleted_at)`
- Regla recomendada app-level: evitar solape para mismo doctor.

---

### 14. `encounters`
**Propósito:** episodio clínico (ambulatorio/internamiento/emergencia/teleconsulta).

**Columnas**
- `id uuid pk`
- `organization_id uuid not null fk -> organizations(id)`
- `patient_id uuid not null fk -> patients(id)`
- `doctor_id uuid not null fk -> doctors(id)`
- `appointment_id uuid null fk -> appointments(id)`
- `encounter_type varchar(20) not null`
- `status varchar(20) not null default 'ABIERTO'`
- `start_at timestamptz not null`
- `end_at timestamptz null`
- `chief_complaint text null`
- `room_number varchar(40) null`
- `bed_number varchar(40) null`
- `admission_source varchar(80) null`
- `discharge_reason text null`
- `created_by uuid null fk -> users(id)`
- `updated_by uuid null fk -> users(id)`
- `created_at timestamptz not null default now()`
- `updated_at timestamptz not null default now()`
- `deleted_at timestamptz null`

**Restricciones/índices**
- `check (encounter_type in ('AMBULATORIO','INTERNAMIENTO','EMERGENCIA','TELECONSULTA'))`
- `check (status in ('ABIERTO','CERRADO','CANCELADO'))`
- `check (end_at is null or end_at > start_at)`
- Índices: `(patient_id, start_at desc)`, `(doctor_id, start_at desc)`, `(status)`, `(encounter_type)`

---

### 15. `vital_signs`
**Propósito:** mediciones de enfermería por encuentro.

**Columnas**
- `id uuid pk`
- `encounter_id uuid not null fk -> encounters(id)`
- `recorded_by uuid not null fk -> users(id)`
- `recorded_at timestamptz not null default now()`
- `temperature_c numeric(5,2) null`
- `bp_systolic int null`
- `bp_diastolic int null`
- `heart_rate int null`
- `respiratory_rate int null`
- `oxygen_saturation numeric(5,2) null`
- `weight_kg numeric(6,2) null`
- `height_cm numeric(6,2) null`
- `bmi numeric(6,2) null`
- `glucose_mg_dl numeric(8,2) null`
- `notes text null`

**Restricciones/índices**
- checks de rangos fisiológicos razonables (implementables con `check`)
- Índices: `(encounter_id, recorded_at desc)`, `(recorded_by)`

---

## 4) Historia clínica

### 16. `clinical_notes`
**Propósito:** notas médicas con firma e inmutabilidad.

**Columnas**
- `id uuid pk`
- `encounter_id uuid not null fk -> encounters(id)`
- `doctor_id uuid not null fk -> doctors(id)`
- `note_type varchar(40) not null default 'EVOLUCION'`
- `content text not null`
- `status varchar(20) not null default 'BORRADOR'`
- `signed_by uuid null fk -> users(id)`
- `signed_at timestamptz null`
- `content_hash varchar(64) null`
- `signature_blob text null`
- `created_by uuid not null fk -> users(id)`
- `updated_by uuid null fk -> users(id)`
- `created_at timestamptz not null default now()`
- `updated_at timestamptz not null default now()`

**Restricciones/índices**
- `check (status in ('BORRADOR','FIRMADA','ANULADA'))`
- `check ((status='FIRMADA' and signed_by is not null and signed_at is not null) or status<>'FIRMADA')`
- Índices: `(encounter_id, created_at desc)`, `(doctor_id, created_at desc)`, `(status)`

**Regla de integridad crítica**
- Si `status='FIRMADA'`, no permitir update de `content` (en app/service + trigger opcional).

---

### 17. `diagnoses`
**Propósito:** diagnósticos por encuentro (ICD-10).

**Columnas**
- `id uuid pk`
- `encounter_id uuid not null fk -> encounters(id)`
- `icd10_code varchar(10) not null`
- `description varchar(255) not null`
- `diagnosis_type varchar(20) not null default 'PRINCIPAL'`
- `is_primary boolean not null default false`
- `status varchar(20) not null default 'ACTIVO'`
- `recorded_by uuid not null fk -> users(id)`
- `recorded_at timestamptz not null default now()`

**Restricciones/índices**
- `check (diagnosis_type in ('PRINCIPAL','SECUNDARIO','COMORBILIDAD'))`
- `check (status in ('ACTIVO','RESUELTO','CANCELADO'))`
- Índices: `(encounter_id)`, `(icd10_code)`, `(status)`

---

### 18. `prescriptions`
**Propósito:** indicaciones farmacológicas por encuentro.

**Columnas**
- `id uuid pk`
- `encounter_id uuid not null fk -> encounters(id)`
- `prescribed_by uuid not null fk -> users(id)`
- `medication_name varchar(255) not null`
- `medication_code varchar(60) null`
- `dose varchar(80) not null`
- `frequency varchar(120) not null`
- `route varchar(30) not null` (ORAL, IV, IM, TOPICA, INHALADA)
- `duration_days int null`
- `quantity int null`
- `instructions text null`
- `status varchar(20) not null default 'ACTIVA'`
- `prescribed_at timestamptz not null default now()`

**Restricciones/índices**
- `check (status in ('ACTIVA','SUSPENDIDA','COMPLETADA','CANCELADA'))`
- `check (duration_days is null or duration_days > 0)`
- Índices: `(encounter_id, prescribed_at desc)`, `(status)`

---

## 5) Laboratorio

### 19. `lab_tests_catalog`
**Propósito:** catálogo de pruebas de laboratorio.

**Columnas**
- `id uuid pk`
- `code varchar(50) not null unique`
- `name varchar(200) not null`
- `sample_type varchar(40) not null`
- `unit varchar(30) null`
- `reference_min numeric(12,4) null`
- `reference_max numeric(12,4) null`
- `is_active boolean not null default true`

---

### 20. `lab_orders`
**Propósito:** orden de laboratorio emitida por médico.

**Columnas**
- `id uuid pk`
- `organization_id uuid not null fk -> organizations(id)`
- `encounter_id uuid not null fk -> encounters(id)`
- `patient_id uuid not null fk -> patients(id)`
- `doctor_id uuid not null fk -> doctors(id)`
- `order_number varchar(50) not null`
- `priority varchar(20) not null default 'NORMAL'`
- `status varchar(20) not null default 'PENDIENTE'`
- `ordered_at timestamptz not null default now()`
- `expected_collection_date date null`
- `notes text null`
- `created_by uuid not null fk -> users(id)`
- `updated_by uuid null fk -> users(id)`
- `created_at timestamptz not null default now()`
- `updated_at timestamptz not null default now()`
- `deleted_at timestamptz null`

**Restricciones/índices**
- `unique (organization_id, order_number) where deleted_at is null`
- `check (priority in ('NORMAL','URGENTE'))`
- `check (status in ('PENDIENTE','RECOLECTADA','EN_PROCESO','COMPLETADA','CANCELADA'))`
- Índices: `(encounter_id)`, `(patient_id)`, `(status)`, `(ordered_at desc)`

---

### 21. `lab_order_items`
**Propósito:** pruebas incluidas en una orden.

**Columnas**
- `id uuid pk`
- `lab_order_id uuid not null fk -> lab_orders(id)`
- `lab_test_id uuid not null fk -> lab_tests_catalog(id)`
- `status varchar(20) not null default 'PENDIENTE'`

**Restricciones**
- `unique (lab_order_id, lab_test_id)`

---

### 22. `lab_results`
**Propósito:** resultados de laboratorio por item.

**Columnas**
- `id uuid pk`
- `lab_order_item_id uuid not null fk -> lab_order_items(id)`
- `result_text varchar(255) null`
- `result_numeric numeric(14,4) null`
- `unit varchar(30) null`
- `ref_min numeric(14,4) null`
- `ref_max numeric(14,4) null`
- `result_flag varchar(20) not null default 'NORMAL'` (NORMAL, ANORMAL, CRITICO)
- `processed_by uuid not null fk -> users(id)`
- `reviewed_by uuid null fk -> users(id)`
- `processed_at timestamptz not null default now()`
- `reviewed_at timestamptz null`
- `notes text null`

**Índices**
- `(lab_order_item_id)`, `(processed_at desc)`, `(result_flag)`

---

## 6) Imágenes médicas

### 23. `imaging_types_catalog`
**Propósito:** catálogo de estudios de imagen.

**Columnas**
- `id uuid pk`
- `code varchar(40) not null unique`
- `name varchar(180) not null`
- `modality varchar(40) not null` (RX, US, CT, MRI, etc.)
- `is_active boolean not null default true`

---

### 24. `imaging_orders`
**Propósito:** órdenes de imágenes.

**Columnas**
- `id uuid pk`
- `organization_id uuid not null fk -> organizations(id)`
- `encounter_id uuid not null fk -> encounters(id)`
- `patient_id uuid not null fk -> patients(id)`
- `doctor_id uuid not null fk -> doctors(id)`
- `imaging_type_id uuid not null fk -> imaging_types_catalog(id)`
- `order_number varchar(50) not null`
- `priority varchar(20) not null default 'NORMAL'`
- `status varchar(20) not null default 'PENDIENTE'`
- `clinical_indication text not null`
- `ordered_at timestamptz not null default now()`
- `expected_date date null`
- `notes text null`
- `created_by uuid not null fk -> users(id)`
- `updated_by uuid null fk -> users(id)`
- `created_at timestamptz not null default now()`
- `updated_at timestamptz not null default now()`
- `deleted_at timestamptz null`

**Restricciones/índices**
- `unique (organization_id, order_number) where deleted_at is null`
- `check (priority in ('NORMAL','URGENTE'))`
- `check (status in ('PENDIENTE','REALIZADA','EN_PROCESO','COMPLETADA','CANCELADA'))`
- Índices: `(encounter_id)`, `(patient_id)`, `(status)`, `(ordered_at desc)`

---

### 25. `imaging_reports`
**Propósito:** informe de estudio de imagen (firmable).

**Columnas**
- `id uuid pk`
- `imaging_order_id uuid not null fk -> imaging_orders(id)`
- `technician_user_id uuid not null fk -> users(id)`
- `radiologist_user_id uuid null fk -> users(id)`
- `performed_at timestamptz not null default now()`
- `findings text not null`
- `impression text not null`
- `recommendations text null`
- `status varchar(20) not null default 'BORRADOR'`
- `signed_at timestamptz null`
- `content_hash varchar(64) null`
- `signature_blob text null`
- `created_at timestamptz not null default now()`
- `updated_at timestamptz not null default now()`

**Restricciones/índices**
- `check (status in ('BORRADOR','FIRMADA','ANULADA'))`
- `check ((status='FIRMADA' and signed_at is not null and radiologist_user_id is not null) or status<>'FIRMADA')`
- Índices: `(imaging_order_id)`, `(status)`, `(performed_at desc)`

**Regla crítica**
- Inmutable tras firma (misma regla que `clinical_notes`).

---

### 26. `imaging_files`
**Propósito:** metadatos de archivos (DICOM/PDF/JPG).

**Columnas**
- `id uuid pk`
- `imaging_order_id uuid not null fk -> imaging_orders(id)`
- `file_name varchar(255) not null`
- `file_type varchar(30) not null`
- `storage_uri text not null`
- `size_bytes bigint not null`
- `sha256 varchar(64) not null`
- `uploaded_by uuid not null fk -> users(id)`
- `uploaded_at timestamptz not null default now()`

**Índices**
- `(imaging_order_id)`, `(uploaded_at desc)`

---

## 7) Facturación futura (placeholders v1)

### 27. `service_codes`
**Propósito:** catálogo de servicios para v2.

**Columnas**
- `id uuid pk`
- `code varchar(50) not null unique`
- `name varchar(200) not null`
- `category varchar(40) not null` (CONSULTA, PROCEDIMIENTO, LAB, IMAGEN, INTERNAMIENTO)
- `base_price numeric(12,2) not null`
- `ars_code varchar(60) null`
- `is_active boolean not null default true`

---

### 28. `encounter_billing_placeholders`
**Propósito:** preparación de facturación por encuentro.

**Columnas**
- `id uuid pk`
- `encounter_id uuid not null fk -> encounters(id)`
- `ncf_number varchar(50) null`
- `ars_provider varchar(120) null`
- `ars_affiliation_number varchar(60) null`
- `billing_status varchar(20) not null default 'PENDIENTE'`
- `total_amount numeric(12,2) null`
- `billed_at timestamptz null`
- `created_at timestamptz not null default now()`

**Restricciones/índices**
- `unique (ncf_number) where ncf_number is not null`
- Índices: `(encounter_id)`, `(billing_status)`

---

## Orden recomendado de migraciones
1. `organizations`, `users`, `roles`, `permissions`, `user_roles`, `role_permissions`, `audit_logs`, `access_logs`.
2. `specialties`, `doctors`, `doctor_specialties`.
3. `patients`.
4. `appointments`.
5. `encounters`, `vital_signs`.
6. `clinical_notes`, `diagnoses`, `prescriptions`.
7. `lab_tests_catalog`, `lab_orders`, `lab_order_items`, `lab_results`.
8. `imaging_types_catalog`, `imaging_orders`, `imaging_reports`, `imaging_files`.
9. `service_codes`, `encounter_billing_placeholders`.
10. Índices finales de performance y constraints adicionales.

---

## Reglas de negocio críticas para el coder

1. **Inmutabilidad por firma**
- `clinical_notes` y `imaging_reports` no se editan tras `status='FIRMADA'`.
- Implementar validación en servicio y opcionalmente trigger DB.

2. **Soft delete consistente**
- Nunca borrar pacientes/doctores/citas/encuentros/órdenes físicamente.
- Consultas siempre con `deleted_at is null`.

3. **Auditoría obligatoria**
- Crear evento auditado en create/update/delete lógico/sign.
- Registrar accesos de lectura sensibles en `access_logs`.

4. **Alcance por rol (RBAC)**
- Doctor: su panel clínico y pacientes bajo su atención.
- Enfermería: signos vitales y lectura clínica según permisos.
- Secretaría/Recepción: agenda y registro administrativo.
- Admin: control total.

---

## Verificación (para ejecución del coder)

### Validación técnica
- Migraciones corren de cero sin errores.
- Constraints/índices creados correctamente.
- Pruebas de inmutabilidad de firma pasan.
- Pruebas de soft delete pasan.
- Pruebas de RBAC por rol pasan.

### Validación funcional mínima
- Registro de paciente (con cédula o pasaporte).
- Agenda de cita y apertura de encuentro.
- Registro de signos vitales.
- Nota clínica firmada e inmutable.
- Orden + resultado de laboratorio.
- Orden + reporte de imágenes.
- Auditoría generada en operaciones sensibles.

---

## Archivos críticos que el coder deberá crear/modificar
- `backend/apps/core/models.py` (organizations/users/rbac/auditoría)
- `backend/apps/patients/models.py`
- `backend/apps/doctors/models.py`
- `backend/apps/appointments/models.py`
- `backend/apps/encounters/models.py`
- `backend/apps/clinical/models.py`
- `backend/apps/lab/models.py`
- `backend/apps/imaging/models.py`
- `backend/apps/billing/models.py` (placeholders)
- `backend/utils/constants.py` (catálogos RD)
- `backend/utils/validators.py` (cédula, pasaporte, etc.)

Este plan define una base robusta y realista para iniciar implementación inmediata del MVP clínico en español, con expansión controlada a facturación/fiscal en la siguiente fase.