from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

# Model imports (adjust as per actual models.py)
from .models import Users, Patients  # Sanjana
from .models import User, AccessRequest  # Mohammed

# --------------------- Sanjana ---------------------
class CustomUserCreationForm(UserCreationForm):
    sex = forms.ChoiceField(choices=[('Male', 'Male'), ('Female', 'Female')], required=True)

    class Meta:
        model = Users  # ⚠️ Check if you are using `User` or `Users`
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'patient'
        if commit:
            user.save()
            # 🛡️ Check if patient already exists before creating
            if not hasattr(user, 'patients'):
                Patients.objects.create(user=user, sex=self.cleaned_data['sex'])
            else:
                user.patients.sex = self.cleaned_data['sex']
                user.patients.save()
        return user

# --------------------- Mohammed ---------------------
class UserSignUpForm(UserCreationForm):
    nhs_number = forms.CharField(
        max_length=10,
        required=False,
        help_text='Enter your 10-digit NHS number',
        widget=forms.TextInput(attrs={'pattern': '[0-9]{10}', 'title': 'Please enter a valid 10-digit NHS number'})
    )

    class Meta:
        model = User  # ⚠️ Replace with actual unified model if applicable
        fields = ('nhs_number', 'email', 'full_name', 'affiliation', 'password1', 'password2')

    def clean(self):
        cleaned_data = super().clean()
        nhs_number = cleaned_data.get('nhs_number')
        if not nhs_number or not nhs_number.isdigit() or len(nhs_number) != 10:
            self.add_error('nhs_number', 'Please enter a valid 10-digit NHS number')
        return cleaned_data

# class UserSignUpForm (alternative clean method by Mohammed - kept for backup)
# class UserSignUpForm(UserCreationForm):
#     nhs_number = forms.CharField(
#         max_length=10,
#         required=True,
#         help_text='Enter your 10-digit NHS number',
#         widget=forms.TextInput(attrs={'pattern': '[0-9]{10}', 'title': 'Please enter a valid 10-digit NHS number'})
#     )

#     class Meta:
#         model = User
#         fields = ('nhs_number', 'email', 'full_name', 'affiliation', 'password1', 'password2')

#     def clean_nhs_number(self):
#         nhs_number = self.cleaned_data.get('nhs_number')
#         if not nhs_number.isdigit() or len(nhs_number) != 10:
#             raise forms.ValidationError('Please enter a valid 10-digit NHS number')
#         return nhs_number

class AccessRequestForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = AccessRequest
        fields = ('full_name', 'email', 'affiliation', 'username', 'password', 'message')

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        email = cleaned_data.get('email')
        full_name = cleaned_data.get('full_name')

        if password and confirm_password:
            if password != confirm_password:
                self.add_error('confirm_password', "Passwords do not match.")

            try:
                validate_password(password, user=User(email=email, full_name=full_name))
            except ValidationError as e:
                self.add_error('password', e)

        return cleaned_data

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)
