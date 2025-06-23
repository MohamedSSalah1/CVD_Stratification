from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
    
    #  Important: This ensures MySQL ENUM doesn't complain
        extra_fields.setdefault('role', 'clinician_approved')

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class Users(AbstractUser):
    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)  # Required for access to admin
    is_superuser = models.BooleanField(default=True)  # Required for superuser privileges
    def get_username(self):
        return self.email
    role = models.CharField(
        max_length=20,
        choices=[
            ('patient', 'Patient'),
            ('clinician_pending', 'Clinician Pending'),
            ('clinician_approved', 'Clinician Approved')
        ]
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    #  Plug in the custom manager here
    objects = CustomUserManager()

    class Meta:
        db_table = 'Users'
        verbose_name_plural = 'Users'


class Patients(models.Model):
    patient_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(Users, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True)
    sex = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], null = True, blank = True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Patients'
        verbose_name_plural = 'Patients'


class Clinicians(models.Model):
    clinician_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(Users, on_delete=models.CASCADE)
    specialty = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Clinicians'
        verbose_name_plural = 'Clinicians'


class CVD_risk_Questionnaire(models.Model):
    question_id = models.AutoField(primary_key=True)
    question_text = models.TextField()
    category = models.CharField(max_length=100, null=True, blank=True)
    subcategory = models.CharField(max_length=100, null=True, blank=True)
    question_order = models.IntegerField(default=0)
    answer_type = models.CharField(max_length=50, null=True, blank=True)    

    class Meta:
        db_table = 'CVD_risk_Questionnaire'
        verbose_name_plural = 'CVD Risk Questionnaire'
        

class CVD_risk_QuestionnaireDependency(models.Model):
    triggering_question = models.ForeignKey(
        'CVD_risk_Questionnaire', related_name='dependent_questions', on_delete=models.CASCADE
    )
    conditional_question = models.ForeignKey(
        'CVD_risk_Questionnaire', related_name='trigger_questions', on_delete=models.CASCADE
    )
    trigger_values = models.CharField(max_length=255, blank=True, null=True)
    def __str__(self):
        return f"If Q{self.triggering_question.question_id} in {self.trigger_values} ⇒ show Q{self.conditional_question.question_id}"

    class Meta:
        db_table = 'CVD_risk_Questionnaire_dependency_values'
        verbose_name = "Question Dependency"
        verbose_name_plural = "Question Dependencies"
        unique_together = ('triggering_question', 'conditional_question')  # Optional constraint


class CVD_risk_QuestionResponseOptions(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.ForeignKey(CVD_risk_Questionnaire, on_delete=models.CASCADE)
    option_text = models.TextField()
    encoded_value = models.FloatField(null=True, blank=True)
    option_label = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'CVD_risk_QuestionResponseOptions'
        verbose_name_plural = 'Questionnaire Response Options'


class CVD_risk_Responses(models.Model):
    response_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE)
    question = models.ForeignKey(CVD_risk_Questionnaire, on_delete=models.CASCADE)
    response_type = models.CharField(max_length=50)
    numeric_response = models.FloatField(null=True, blank=True)
    boolean_response = models.BooleanField(null=True, blank=True)
    option_selected = models.ForeignKey(CVD_risk_QuestionResponseOptions, on_delete=models.SET_NULL, null=True, blank=True)
    multi_selected_options = models.ManyToManyField(CVD_risk_QuestionResponseOptions, related_name="multi_responses", blank=True)
    response_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    submission_id = models.CharField(max_length=100, null=True, blank=True)

    @property
    def encoded_single_option(self):
        """Returns encoded value of selected option if applicable."""
        return self.option_selected.encoded_value if self.option_selected else None
    @property
    def encoded_multi_options(self):
        """Returns list of encoded values from multi-selected options."""
        return [opt.encoded_value for opt in self.multi_selected_options.all()]

    class Meta:
        db_table = 'CVD_risk_Responses'
        verbose_name_plural = 'CVD Risk Responses'

class FeatureOptionMapping(models.Model):
    feature_name = models.CharField(max_length=300)
    question = models.ForeignKey(CVD_risk_Questionnaire, on_delete=models.CASCADE)
    option = models.ForeignKey(CVD_risk_QuestionResponseOptions, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('feature_name', 'question')
        verbose_name_plural = "Feature Option Mappings"

    def __str__(self):
        return f"{self.feature_name} → {self.option.option_text}"



class CVD_risk_Clinician_Patient(models.Model):
    id = models.AutoField(primary_key=True)
    clinician = models.ForeignKey(Clinicians, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE)
    assigned_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'CVD_risk_Clinician_Patient'
        verbose_name_plural = 'Clinician Patients'


class ML_Models(models.Model):
    model_id = models.AutoField(primary_key=True)
    model_name = models.CharField(max_length=255)
    model_type = models.CharField(max_length=100)

    class Meta:
        db_table = 'ML_Models'
        verbose_name_plural = 'ML Models'


class CVD_Risk_Model_InputFeatures(models.Model):
    feature_id = models.AutoField(primary_key=True)
    question = models.ForeignKey(CVD_risk_Questionnaire, on_delete=models.CASCADE)
    feature_name = models.CharField(max_length=255)  # e.g., 'years_at_address_Upper.third'
    # Only for categorical features
    encoded_option = models.ForeignKey(
        CVD_risk_QuestionResponseOptions,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        help_text="For categorical features: which specific option this feature checks"
    )

    class Meta:
        db_table = 'CVD_Risk_Model_InputFeatures'
        verbose_name_plural = 'CVD Risk Model Input Features'
        unique_together = ('question', 'feature_name')


class CVD_Risk_CalculatedFeatures(models.Model):
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE)
    model = models.ForeignKey(ML_Models, on_delete=models.CASCADE)
    feature = models.ForeignKey(CVD_Risk_Model_InputFeatures, on_delete=models.CASCADE)
    value = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'CVD_Risk_CalculatedFeatures'
        verbose_name_plural = 'CVD Risk Calculated Features'
        unique_together = ('patient', 'model', 'feature')

        

class CVD_ModelFeatureMappings(models.Model):
    model = models.ForeignKey(ML_Models, on_delete=models.CASCADE)
    input_feature = models.ForeignKey(CVD_Risk_Model_InputFeatures, on_delete=models.CASCADE)

    class Meta:
        db_table = 'CVD_ModelFeatureMappings'
        verbose_name_plural = 'Model Feature Mappings'
        unique_together = (('model', 'input_feature'),)
        

class CVD_Risk_FeatureThresholds(models.Model):
    feature = models.ForeignKey(CVD_Risk_Model_InputFeatures, on_delete=models.CASCADE)
    threshold_value = models.FloatField()

    class Meta:
        db_table = 'CVD_Risk_FeatureThresholds'
        verbose_name_plural = 'CVD Risk Feature Thresholds'
        unique_together = (('feature',),)


class batch_CVD_Risk_Features(models.Model):
    feature_id = models.AutoField(primary_key=True)
    feature_name = models.CharField(max_length=255)
    feature_description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'batch_CVD_Risk_Features'
        verbose_name_plural = 'Batch CVD Risk Features'


class batch_CVD_Risk_Model_Features(models.Model):
    model = models.ForeignKey(ML_Models, on_delete=models.CASCADE)
    feature = models.ForeignKey(batch_CVD_Risk_Features, on_delete=models.CASCADE)

    class Meta:
        db_table = 'batch_CVD_Risk_Model_Features'
        unique_together = (('model', 'feature'),)
        verbose_name_plural = 'Batch CVD Risk Model Features'


class Risk_Stratification(models.Model):
    stratification_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE)
    risk_score = models.DecimalField(max_digits=5, decimal_places=2)
    recommendation = models.TextField()
    assessed_at = models.DateTimeField(auto_now_add=True)
    model = models.ForeignKey(ML_Models, on_delete=models.SET_NULL, null=True)
    submission_id = models.CharField(max_length=100, null=True, blank=True)  # NEW
    alert_sent = models.BooleanField(default=False)

    class Meta:
        db_table = 'Risk_Stratification'
        verbose_name_plural = 'Risk Stratification'


class CVD_risk_Patient_Outcomes(models.Model):
    outcome_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE)
    outcome_description = models.TextField()
    reported_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'CVD_risk_Patient_Outcomes'
        verbose_name_plural = 'CVD Risk Patient Outcomes'


class batch_CVD_Risk_Risk(models.Model):
    risk_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE)
    model = models.ForeignKey(ML_Models, on_delete=models.CASCADE)
    risk_score = models.DecimalField(max_digits=5, decimal_places=2)
    prediction_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'batch_CVD_Risk_Risk'
        verbose_name_plural = 'Batch CVD Risk Risk'


class batch_CVD_Risk_Output(models.Model):
    output_id = models.AutoField(primary_key=True)
    risk = models.ForeignKey(batch_CVD_Risk_Risk, on_delete=models.CASCADE)
    plot_type = models.CharField(max_length=100)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'batch_CVD_Risk_Output'
        verbose_name_plural = 'Batch CVD Risk Output'

