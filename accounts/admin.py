from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# ---------------- SANJANA MODELS ----------------
from .models import (
    Patients,  # Sanjana
    Clinicians,  # Sanjana
    CVD_risk_Clinician_Patient,  # Sanjana
    Users,  # Sanjana
    CVD_risk_Questionnaire,  # Sanjana
    CVD_risk_QuestionResponseOptions,  # Sanjana
    CVD_risk_Responses,  # Sanjana
    CVD_risk_Patient_Outcomes,  # Sanjana
    Risk_Stratification,  # Sanjana
    ML_Models,  # Sanjana
    batch_CVD_Risk_Features,  # Sanjana
    batch_CVD_Risk_Model_Features,  # Sanjana
    batch_CVD_Risk_Risk,  # Sanjana
    batch_CVD_Risk_Output,  # Sanjana
)

# ---------------- MOHAMMED MODELS ----------------
from .models import (
    User,  # Mohammed
    AccessRequest,  # Mohammed
    Patient,  # Mohammed
    PatientRecord,  # Mohammed
    MLModel,  # Mohammed
    BatchPredictionRun,  # Mohammed
    BatchPredictionResultDetail,  # Mohammed
)

# ---------- CUSTOM ADMIN CLASSES ----------

# Mohammed's Custom User Admin
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'full_name', 'role', 'is_approved', 'is_staff', 'nhs_number')
    search_fields = ('email', 'full_name', 'nhs_number')
    list_filter = ('role', 'is_approved', 'is_staff')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('full_name', 'affiliation', 'nhs_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Roles and Access', {'fields': ('role', 'is_approved', 'reason_for_access')}),
    )
    ordering = ('email',)

admin.site.register(User, UserAdmin)  # Mohammed

# Mohammed's AccessRequest Admin
class AccessRequestAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'affiliation', 'status', 'created_at')
    search_fields = ('full_name', 'email', 'affiliation')
    list_filter = ('status', 'created_at')
    ordering = ('-created_at',)

admin.site.register(AccessRequest, AccessRequestAdmin)

# Mohammed's Patient Admin
class PatientAdmin(admin.ModelAdmin):
    list_display = ('nhs_number', 'first_name', 'last_name', 'age', 'gender', 'ethnicity')
    search_fields = ('nhs_number', 'first_name', 'last_name', 'ethnicity')
    list_filter = ('gender', 'ethnicity', 'age')
    ordering = ('last_name', 'first_name')

admin.site.register(Patient, PatientAdmin)

# Mohammed's PatientRecord Admin
class PatientRecordAdmin(admin.ModelAdmin):
    list_display = ('patient', 'timestamp', 'age', 'gender', 'predicted_risk', 'risk_category')
    search_fields = ('patient__nhs_number', 'patient__first_name', 'patient__last_name')
    list_filter = ('timestamp', 'gender', 'risk_category')
    ordering = ('-timestamp',)

admin.site.register(PatientRecord, PatientRecordAdmin)

# ---------- DEFAULT REGISTRATIONS (No Custom Admin Classes) ----------

# Sanjana's core models
admin.site.register(Patients)
admin.site.register(Clinicians)
admin.site.register(CVD_risk_Clinician_Patient)
admin.site.register(Users)
admin.site.register(CVD_risk_Questionnaire)
admin.site.register(CVD_risk_QuestionResponseOptions)
admin.site.register(CVD_risk_Responses)
admin.site.register(CVD_risk_Patient_Outcomes)
admin.site.register(Risk_Stratification)
admin.site.register(ML_Models)  # Sanjana
admin.site.register(batch_CVD_Risk_Features)
admin.site.register(batch_CVD_Risk_Model_Features)
admin.site.register(batch_CVD_Risk_Risk)
admin.site.register(batch_CVD_Risk_Output)

# Mohammed's remaining models
admin.site.register(MLModel)
admin.site.register(BatchPredictionRun)
admin.site.register(BatchPredictionResultDetail)
