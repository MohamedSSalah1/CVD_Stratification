
# SANJANA'S VIEWS
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect
from django.contrib import messages
from .models import Users
from .forms import CustomUserCreationForm
from .models import *
from django.shortcuts import get_object_or_404
import joblib
import pandas as pd
import numpy as np
from django.http import JsonResponse
from django.db import DatabaseError
from django.db import transaction, connection
from django.views.decorators.http import require_http_methods
from .utils import should_display_question
from datetime import datetime
import os
from django.shortcuts import render, redirect
from accounts.models import CVD_risk_Questionnaire, CVD_risk_QuestionResponseOptions, CVD_risk_Responses
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from uuid import uuid4
from feature_calculators import (
    model1_sociodemographic,
    model2_healthandmed,
    model3_SSF,
    model4_early_life,
    model5_family_history,
    model6_lifestyle,
    model7_biggestmodel
)
import joblib
from datetime import datetime
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import connection, DatabaseError
from uuid import uuid4
from datetime import datetime
import os
import joblib

from .models import (
    CVD_risk_Questionnaire,
    CVD_risk_QuestionResponseOptions,
    CVD_risk_Responses,
    Patients,
    ML_Models,
    Risk_Stratification
)
from .utils import should_display_question
from Questionnaire_data.utils import get_visible_questions_for_patient_in_category
## MOHAMMED'S VIEWS
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.http import HttpResponse, FileResponse, Http404
from django.db.models import Q # Import Q for complex lookups
import pandas as pd
import numpy as np
from io import StringIO
from .models import User, AccessRequest, Patient, PatientRecord
from .forms import UserSignUpForm, AccessRequestForm, ContactForm
from django.core.paginator import Paginator
import os


thresholds = pd.read_csv("model_files/FinalSolFront1 (1).csv").iloc[0]
CATEGORY_THRESHOLDS = {
    "Sociodemographics": (thresholds["Min_Threshold1"], thresholds["Max_Threshold1"]),
    "Health and medical history": (thresholds["Min_Threshold2"], thresholds["Max_Threshold2"]),
    "Sex-specific factors": (thresholds["Min_Threshold3"], thresholds["Max_Threshold3"]),
    # add others as needed
}
CATEGORY_ORDER = ["Sociodemographics", "Health and medical history", "Sex-specific factors",
                  "Early life factors", "Family history", "Lifestyle and environment",
                  "Psychosocial factors"]

def get_risk_category(score, category):
    """
    Determines patient's risk category based on the score and thresholds.
    """
    try:
        idx = CATEGORY_ORDER.index(category) + 1  # because threshold columns are 1-indexed
        min_t = thresholds[f"Min_Threshold{idx}"]
        max_t = thresholds[f"Max_Threshold{idx}"]

        if score < min_t:
            return "Low Risk"
        elif score > max_t:
            return "High Risk"
        else:
            return "Inconclusive"
    except Exception as e:
        print(f"❌ Failed to classify risk: {e}")
        return "Unknown"

MODEL_FILE_MAPPING = {
    "Sociodemographics": "model_files/ML_models/MRMR_COX_Sociodemographics.pkl",
    "Health and medical history": "model_files/ML_models/MRMR_COX_Sociodemographics_Health_and_medical_history.pkl",
    "Sex-specific factors": "model_files/ML_models/MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors.pkl",
    "Early life factors": "model_files/ML_models/MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors_Early_life_factors.pkl",
    "Family history": "model_files/ML_models/MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors_Early_life_factors_Family_history.pkl",
    "Lifestyle and environment": "model_files/ML_models/MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors_Early_life_factors_Family_history_Lifestyle_and_environment.pkl",
    "Psychosocial factors": "model_files/ML_models/MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors_Early_life_factors_Family_history_Lifestyle_and_environment_Psychosocial_factors.pkl",
}

MODEL_DB_NAME_MAPPING = {
    'model1_sociodemographic': 'MRMR_COX_Sociodemographics.pkl',
    'model2_healthandmed': 'MRMR_COX_Sociodemographics_Health_and_medical_history.pkl',
    'model3_SSF': 'MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors',
    'model4_early_life': 'MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors_Early_life_factors.pkl',
    'model5_family_history': 'MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors_Early_life_factors_Family_history.pkl',
    'model6_lifestyle': 'MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors_Early_life_factors_Family_history_Lifestyle_and_environment.pkl',
    'model7_biggestmodel': 'MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors_Early_life_factors_Family_history_Lifestyle_and_environment_Psychosocial_factors.pkl'
}


# Normalise this 
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            if user.role == 'patient':
                return redirect('patient_dashboard')
            elif user.role == 'clinician_approved':
                return redirect('clinician_dashboard')
            elif user.role == 'admin':
                return redirect('/admin/')  # built-in admin site
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'users/login.html')

# Shows a login page for admin, checks if the user is logged in with role = 'admin', and if so, takes them to the admin dashboard
#def admin_login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.role == 'admin':
            login(request, user)
            return redirect('admin_dashboard')
        else:
            return render(request, 'admin/login.html', {'error': 'Invalid credentials or not an admin'})
    return render(request, 'admin/login.html')

#Checks if the user is logged in and is an admin, and if so, shows them a list of all users, questionnaires and responses
def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

@login_required
@user_passes_test(is_admin)
#def admin_dashboard(request):
    users = CustomUser.objects.all()
    questionnaires = Questionnaire.objects.all()
    responses = Response.objects.all()
    return render(request, 'admin/dashboard.html', {
        'users': users,
        'questionnaires': questionnaires,
        'responses': responses
    })


@login_required
def patient_dashboard(request):
    if request.user.role != 'patient':
        return redirect('home')  # or show a 403
    # Fetch the patient profile for this user
    patient_profile = get_object_or_404(Patients, user=request.user)

    context = {
        'patient': patient_profile
    }
    return render(request, 'patients/dashboard.html')
	


# helper for message text
def get_final_message_text(risk_category):
    if risk_category == "Low Risk":
        return "✅ You are at low 10-year risk of CVD. Please maintain a healthy lifestyle."
    elif risk_category == "High Risk":
        return "⚠️ You are at high 10-year risk of CVD. Please contact your GP or clinician for further testing."
    else:
        return "❓ Risk inconclusive. Continue to next section."



@require_http_methods(["GET", "POST"])
@login_required
def assessment_view(request):
    from django.db import connection
    from django.db.models import Max

    category = request.GET.get('category')
    error_message = None

    # Ordered form category flow
    CATEGORY_ORDER = [
        "Sociodemographics",
        "Health and medical history",
        "Sex-specific factors",
        "Early life factors",
        "Family history",
        "Lifestyle and environment",
        "Psychosocial factors"
    ]

    # Category to function and model mapping
    CATEGORY_MODEL_MAPPING = {
        "Sociodemographics": model1_sociodemographic,
        "Health and medical history": model2_healthandmed,
        "Sex-specific factors": model3_SSF,
        "Early life factors": model4_early_life,
        "Family history": model5_family_history,
        "Lifestyle and environment": model6_lifestyle,
        "Psychosocial factors": model7_biggestmodel
    }

    MODEL_FILE_MAPPING = {
        "Sociodemographics": "model_files/ML_models/MRMR_COX_Sociodemographics.pkl",
        "Health and medical history": "model_files/ML_models/MRMR_COX_Sociodemographics_Health_and_medical_history.pkl",
        "Sex-specific factors": "model_files/ML_models/MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors.pkl",
        "Early life factors": "model_files/ML_models/MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors_Early_life_factors.pkl",
        "Family history": "model_files/ML_models/MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors_Early_life_factors_Family_history.pkl",
        "Lifestyle and environment": "model_files/ML_models/MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors_Early_life_factors_Family_history_Lifestyle_and_environment.pkl",
        "Psychosocial factors": "model_files/ML_models/MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors_Early_life_factors_Family_history_Lifestyle_and_environment_Psychosocial_factors.pkl",
    }

    raw_categories = CVD_risk_Questionnaire.objects.values_list('category', flat=True).distinct()
    all_categories = sorted(set(raw_categories), key=lambda x: CATEGORY_ORDER.index(x) if x in CATEGORY_ORDER else 999)

    # Redirect to first unanswered category
    if not category and all_categories:
        return redirect(f"{reverse('start_assessment')}?category={all_categories[0]}")

    try:
        current_index = all_categories.index(category)
        previous_category = all_categories[current_index - 1] if current_index > 0 else None
        next_category = all_categories[current_index + 1] if current_index + 1 < len(all_categories) else None
    except ValueError:
        previous_category = None
        next_category = None

    patient = Patients.objects.get(user=request.user)

    all_questions = CVD_risk_Questionnaire.objects.filter(category=category).order_by('question_order')
    visible_questions = get_visible_questions_for_patient_in_category(patient, category)

    # Load latest saved responses to prefill
    saved_responses = {
        r.question.question_id: (
            r.option_selected.encoded_value if r.option_selected else
            r.numeric_response if r.numeric_response is not None else
            r.boolean_response
        )
        for r in CVD_risk_Responses.objects.filter(patient=patient)
    }

    # ---------- Handle POST (Form Submission) ----------
    if request.method == 'POST':
        try:
            # Assign a new submission session if not yet set
            if 'submission_id' not in request.session:
                request.session['submission_id'] = str(uuid4())
            submission_id = request.session['submission_id']

            for q in visible_questions:
                key = f"question_{q.question_id}"
                options = CVD_risk_QuestionResponseOptions.objects.filter(question=q)

                # Multi-select handling
                if q.answer_type == "Toggle multiple answer":
                    values = request.POST.getlist(f"{key}_option")
                    if not values:
                        continue
                    selected_options = options.filter(id__in=values)
                    if not selected_options.exists():
                        continue
                    response_obj = CVD_risk_Responses.objects.create(
                        patient=patient, question=q, response_type=q.answer_type, submission_id=submission_id
                    )
                    response_obj.multi_selected_options.set(selected_options)
                    response_obj.save()
                    continue

                # Single/miscellaneous responses
                value = request.POST.get(key)
                if not value or value.lower() in ['select one answer', 'choose', '']:
                    continue

                response_obj = CVD_risk_Responses.objects.create(
                    patient=patient, question=q, response_type=q.answer_type, submission_id=submission_id
                )

                if options.exists():
                    try:
                        selected_option = options.get(id=int(value))
                        response_obj.option_selected = selected_option
                    except:
                        continue
                else:
                    try:
                        response_obj.numeric_response = float(value)
                    except:
                        response_obj.boolean_response = value.lower() in ['yes', 'true', '1']
                response_obj.save()

        except DatabaseError:
            connection.rollback()
            messages.error(request, "Database error occurred.")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            messages.error(request, "Unexpected error occurred.")

        # Proceed only if at least one response was saved
        if CVD_risk_Responses.objects.filter(patient=patient, question__category=category, submission_id=submission_id).exists():
            completed = request.session.get('completed_categories', [])
            if category not in completed:
                completed.append(category)
                request.session['completed_categories'] = completed

            # ---------- Model Evaluation ----------
            if category in CATEGORY_MODEL_MAPPING:
                model_module = CATEGORY_MODEL_MAPPING[category]
                try:
                    df_scaled = model_module.calculate_features(patient.patient_id, submission_id)
                    model_path = MODEL_FILE_MAPPING[category]
                    print(f"🧠 Looking for model: {model_path}")

                    if not os.path.exists(model_path):
                        raise FileNotFoundError(f"Model file not found for category: {category}")

                    model = joblib.load(model_path)
                    print("🧾 Final columns before prediction:", df_scaled.columns.tolist())

                    risk_score = float(model.predict(df_scaled)[0])
                    print(f"📈 Risk score = {risk_score:.2f}")

                    risk_category = get_risk_category(risk_score, category)
                    print(f"🧪 Risk classification: {risk_category}")

                    model_name_cleaned = os.path.basename(model_path).replace(".pkl", "")
                    model_obj = ML_Models.objects.get(model_name=model_name_cleaned)

                    # Save results with timestamp for grouping later
                    assessed_time = datetime.now()
                    Risk_Stratification.objects.create(
                        patient=patient,
                        model=model_obj,
                        assessed_at=assessed_time,
                        risk_score=risk_score,
                        recommendation=risk_category,
                        submission_id=submission_id
                    )

                    # Early stopping — render final message if conclusive result reached
                    if risk_category in ["Low Risk", "High Risk"]:
                        request.session.pop("submission_id", None)
                        return render(request, "patients/final_message.html", {
                            "risk_score": risk_score,
                            "recommendation": risk_category,
                            "message": get_final_message_text(risk_category)
                        })

                except Exception as e:
                    print(f"❌ Error during model execution for {category}: {e}")

            # Only clear submission_id at end of full or early-stopped run
            if risk_category in ["Low Risk", "High Risk"] or not next_category:
                request.session.pop("submission_id", None)

            if next_category:
                return redirect(f"{reverse('start_assessment')}?category={next_category}")
            else:
                request.session['completed_categories'] = []
                return redirect('patient_results')
        else:
            error_message = "Please answer at least one question before proceeding."

    # ---------- GET View ----------
    question_data = []
    for q in visible_questions:
        options = list(CVD_risk_QuestionResponseOptions.objects.filter(question=q))
        latest = CVD_risk_Responses.objects.filter(patient=patient, question=q).order_by('-last_updated').first()

        response_value = None
        response_id = None
        multi_ids = []
        if latest:
            if q.answer_type == "Enter integer answer":
                response_value = latest.numeric_response
            elif q.answer_type == "Select one answer":
                response_id = str(latest.option_selected_id) if latest.option_selected_id else None
            elif q.answer_type == "Toggle multiple answer":
                multi_ids = latest.multi_selected_options.values_list('id', flat=True)

        question_data.append({
            'question': q,
            'options': options,
            'response': response_value,
            'response_id': response_id,
            'multi_response_ids': multi_ids,
            'answer_type': q.answer_type
        })

    return render(request, 'patients/assessment.html', {
        'category': category,
        'question_data': question_data,
        'all_categories': all_categories,
        'completed_categories': request.session.get('completed_categories', []),
        'previous_category': previous_category,
        'next_category': next_category,
        'error_message': error_message
    })




def get_next_category(category_list, current):
    """Helper function to get the next category in the list"""
    try:
        idx = category_list.index(current)
        return category_list[idx + 1] if idx + 1 < len(category_list) else None
    except ValueError:
        return None


MODEL_METRICS = {
    "MRMR_COX_Sociodemographics": {
        "accuracy": "16.26%",
        "auroc": "0.6473",
        "precision": "16.26%",
        "recall": "100.00%"
    },
    "MRMR_COX_Sociodemographics_Health_and_medical_history": {
        "accuracy": "86.77%",
        "auroc": "0.7785",
        "precision": "91.49%",
        "recall": "24.94%"
    },
    "MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors": {
        "accuracy": "86.85%",
        "auroc": "0.7920",
        "precision": "96.19%",
        "recall": "17.93%"
    },
    "MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors_Early_life_factors": {
        "accuracy": "86.82%",
        "auroc": "0.7917",
        "precision": "96.12%",
        "recall": "18.51%"
    },
    "MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors_Early_life_factors_Family_history": {
        "accuracy": "86.56%",
        "auroc": "0.7862",
        "precision": "87.13%",
        "recall": "26.86%"
    },
    "MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors_Early_life_factors_Family_history_Lifestyle_and_environment": {
        "accuracy": "86.59%",
        "auroc": "0.7946",
        "precision": "97.31%",
        "recall": "12.39%"
    },
    "MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors_Early_life_factors_Family_history_Lifestyle_and_environment_Psychosocial_factors": {
        "accuracy": "86.59%",
        "auroc": "0.7942",
        "precision": "97.25%",
        "recall": "12.90%"
    }
}




@login_required
def patient_self_results(request):
    if request.user.role != 'patient':
        return redirect('home')

    patient = get_object_or_404(Patients, user=request.user)

    # STEP 1: Find the latest submission ID used by this patient
    latest_strat = Risk_Stratification.objects.filter(patient=patient).exclude(submission_id__isnull=True).order_by('-assessed_at').first()

    if not latest_strat:
        return render(request, 'patients/results.html', {
            'patient': patient,
            'model_results': [],
            'all_models_inconclusive': True,
            'all_categories_completed': False,
            'assessment_date': None
        })

    latest_submission_id = latest_strat.submission_id
    assessment_date = latest_strat.assessed_at

    # STEP 2: Fetch only results for models evaluated in this session
    strat_results = Risk_Stratification.objects.filter(
        patient=patient,
        submission_id=latest_submission_id
    ).select_related('model').order_by('assessed_at')

    model_results = []
    all_models_inconclusive = True

    for strat in strat_results:
        category_guess = strat.model.model_name.replace("MRMR_COX_", "").replace("_", " ").strip().title()
        if strat.recommendation in ['Low Risk', 'High Risk']:
            all_models_inconclusive = False

        model_results.append({
            'category': category_guess,
            'prediction_score': round(strat.risk_score, 2),
            'risk_category': strat.recommendation,
            'plot_path': f"patient_plots/patient_{patient.patient_id}_{strat.model.model_name}.png",
            **MODEL_METRICS.get(strat.model.model_name, {
                "accuracy": "N/A",
                "auroc": "N/A",
                "precision": "N/A",
                "recall": "N/A"
                })
            })

    return render(request, 'patients/results.html', {
        'patient': patient,
        'model_results': model_results,
        'all_models_inconclusive': all_models_inconclusive,
        'all_categories_completed': len(model_results) == len(CATEGORY_ORDER),
        'assessment_date': assessment_date,
    })




@login_required
def clinician_patient_results(request, patient_id=None):
    # Step 1: Determine the patient based on role
    if request.user.role == 'patient':
        patient = get_object_or_404(Patients, user=request.user)
    elif request.user.role == 'clinician_approved':
        if not patient_id:
            return redirect('clinician_dashboard')
        patient = get_object_or_404(Patients, id=patient_id)
    else:
        return redirect('home')

    # Step 2: Fetch only the completed models (not all 7)
    results = []
    try:
        # Get all stratification results for this patient, ordered latest first
        strat_results = (
            Risk_Stratification.objects.filter(patient=patient)
            .select_related("model")
            .order_by("-assessed_at")
        )

        # Track the models already included
        seen_model_names = set()

        for strat in strat_results:
            model = strat.model
            model_name = model.model_name
            if model_name in seen_model_names:
                continue  # Avoid duplicates if multiple entries exist
            seen_model_names.add(model_name)

            # Derive category name from mapping
            category = None
            for k, v in MODEL_FILE_MAPPING.items():
                if os.path.basename(v).replace(".pkl", "") == model_name:
                    category = k
                    break

            if not category:
                continue  # Skip if mapping fails

            results.append({
                'category': category,
                'score': round(strat.risk_score, 2),
                'risk': strat.recommendation,
                'plot_path': f"/static/patient_plots/patient_{patient.id}_{model_name}.png",
                **MODEL_METRICS.get(model_name, {
                    "accuracy": "N/A",
                    "auroc": "N/A",
                    "precision": "N/A",
                    "recall": "N/A"
                    })
                })

    except Exception as e:
        print(f"⚠️ Error processing results: {e}")

    return render(request, 'patients/results.html', {
        'patient': patient,
        'model_results': results
    })



@login_required
def assessment_history(request):
    if request.user.role != 'patient':
        return redirect('home')
    return render(request, 'patients/history.html')

@login_required
def patient_learn(request):
    return render(request, 'learn.html')


@login_required
def clinician_dashboard(request):
    if request.user.role != 'clinician_approved':
        return redirect('home')

    clinician = Clinicians.objects.get(user=request.user)
    assignments = CVD_risk_Clinician_Patient.objects.filter(clinician=clinician).select_related('patient')

    patient_data = []
    high_risk_patients = []
    
    for assign in assignments:
        patient = assign.patient
        latest_risk = Risk_Stratification.objects.filter(patient=patient).order_by('-assessed_at').first()
        
        is_high_risk = latest_risk and latest_risk.recommendation == 'High Risk'
        
        patient_info = {
            'patient_id': patient.patient_id,  # Add this for URL routing
            'name': f"{patient.user.first_name} {patient.user.last_name}",
            'dob': patient.date_of_birth,
            'email': patient.user.email,
            'risk_score': latest_risk.risk_score if latest_risk else None,
            'recommendation': latest_risk.recommendation if latest_risk else None,
            'assessed_at': latest_risk.assessed_at if latest_risk else None,
            'is_high_risk': is_high_risk,
        }
        
        patient_data.append(patient_info)
        if is_high_risk:
            high_risk_patients.append(patient_info)

    # Calculate statistics
    total_patients = len(patient_data)
    high_risk_count = len([p for p in patient_data if p.get('recommendation') == 'High Risk'])
    intermediate_risk_count = len([p for p in patient_data if p.get('recommendation') == 'Intermediate Risk'])
    low_risk_count = len([p for p in patient_data if p.get('recommendation') == 'Low Risk'])

    return render(request, 'clinicians/clinician_dashboard.html', {
        'patient_data': patient_data,
        'high_risk_patients': high_risk_patients,
        'total_patients': total_patients,
        'high_risk_count': high_risk_count,
        'intermediate_risk_count': intermediate_risk_count,
        'low_risk_count': low_risk_count,
    })



def logout_view(request):
    logout(request)
    return redirect('login')

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            sex = form.cleaned_data.get('sex')
            login(request, user)
            return redirect('patient_dashboard')
        else:
            print(" Form errors:", form.errors)
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/signup.html', {'form': form})



# Create your views here.
def home_view(request):
    return render(request, 'medilab/starter-page.html')

def request_access_view(request):
    return render(request, 'users/request-access.html')


##MOHAMMED's VIEWShere.

#def hello(request):
    return HttpResponse("Hello, This is a Cardiovascular app for risk prediction.!")


def home(request):
    if request.user.is_authenticated:
        if request.user.role == 'admin':
            pending_access_requests_count = AccessRequest.objects.filter(status='pending').count()
            total_approved_users = User.objects.filter(is_approved=True).count()
            total_clinicians = User.objects.filter(role='clinician', is_approved=True).count()
            total_patients = Patient.objects.count() # Assuming patients are in the Patient model

            context = {
                'pending_access_requests_count': pending_access_requests_count,
                'total_approved_users': total_approved_users,
                'total_clinicians': total_clinicians,
                'total_patients': total_patients,
            }
            return render(request, 'cardiovascular_app/home.html', context)
        elif request.user.role == 'clinician':
            # If the user is a logged-in clinician, render a personalized dashboard
            return render(request, 'cardiovascular_app/clinician_dashboard.html', {'user': request.user})
    # If not a logged-in clinician (anonymous or patient), show the generic home page
    return render(request, 'cardiovascular_app/home.html')

def about(request):
    return render(request, 'cardiovascular_app/about.html')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Send email (mock for now)
            send_mail(
                'Contact Form Submission',
                f"From: {form.cleaned_data['name']}\nEmail: {form.cleaned_data['email']}\nMessage: {form.cleaned_data['message']}",
                'from@example.com',
                ['admin@example.com'],
                fail_silently=False,
            )
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'cardiovascular_app/contact.html', {'form': form})

def request_access(request):
    if request.method == 'POST':
        form = AccessRequestForm(request.POST)
        if form.is_valid():
            # Check if passwords match if both are provided
            password = form.cleaned_data.get('password')
            confirm_password = request.POST.get('confirm_password')
            
            if password and confirm_password and password != confirm_password:
                form.add_error('password', 'Passwords do not match')
                return render(request, 'cardiovascular_app/request_access.html', {'form': form})
                
            access_request = form.save()
            messages.success(request, 'Your access request has been submitted successfully and is awaiting admin approval.')
            # Return 'OK' for the php-email-form JavaScript to detect success
            return HttpResponse('OK')
    else:
        form = AccessRequestForm()
    return render(request, 'cardiovascular_app/request_access.html', {'form': form})

#def signup(request):
    if request.method == 'POST':
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Removed logic for is_approved and reason_for_access for patient signup
            user = authenticate(request, username=form.cleaned_data.get('username'), password=form.cleaned_data.get('password2'))
            if user is not None:
                login(request, user)
                messages.success(request, 'Your account has been created successfully!')
                return redirect('home') # Redirect to home page after successful signup and login
            else:
                messages.error(request, 'An error occurred during login after signup.')
                return redirect('login') # Fallback to login if auto-login fails
    else:
        form = UserSignUpForm()
    return render(request, 'cardiovascular_app/signup.html', {'form': form})

def batch_prediction(request):
    # Define all required columns for batch prediction
    required_columns = [
        'nhs_number', 'age', 'gender', 'height', 'weight',
        'apolipoprotein_b', 'apolipoprotein_a1', 'alanine', 'glutamine', 'glycine',
        'histidine', 'total_concentration_of_branched_chain_amino_acids_leucine_isoleucine_valine',
        'isoleucine', 'leucine', 'valine', 'phenylalanine', 'tyrosine',
        'average_diameter_for_vldl_particles', 'average_diameter_for_ldl_particles',
        'average_diameter_for_hdl_particles', 'total_concentration_of_lipoprotein_particles',
        'concentration_of_vldl_particles', 'concentration_of_ldl_particles',
        'concentration_of_hdl_particles',
        'concentration_of_chylomicrons_and_extremely_large_vldl_particles',
        'concentration_of_very_large_vldl_particles', 'concentration_of_large_vldl_particles',
        'concentration_of_medium_vldl_particles', 'concentration_of_small_vldl_particles',
        'concentration_of_very_small_vldl_particles', 'concentration_of_idl_particles',
        'concentration_of_large_ldl_particles', 'concentration_of_medium_ldl_particles',
        'concentration_of_small_ldl_particles', 'concentration_of_very_large_hdl_particles',
        'concentration_of_large_hdl_particles', 'concentration_of_medium_hdl_particles',
        'concentration_of_small_hdl_particles', 'total_cholesterol',
        'total_cholesterol_minus_hdl_c', 'remnant_cholesterol_non_hdl', 'non_ldl_cholesterol',
        'vldl_cholesterol', 'clinical_ldl_cholesterol', 'ldl_cholesterol', 'hdl_cholesterol',
        'cholesterol_in_chylomicrons_and_extremely_large_vldl', 'cholesterol_in_very_large_vldl',
        'cholesterol_in_large_vldl', 'cholesterol_in_medium_vldl', 'cholesterol_in_small_vldl',
        'cholesterol_in_very_small_vldl', 'cholesterol_in_idl', 'cholesterol_in_large_ldl',
        'cholesterol_in_medium_ldl', 'cholesterol_in_small_ldl', 'cholesterol_in_very_large_hdl',
        'cholesterol_in_large_hdl', 'cholesterol_in_medium_hdl', 'cholesterol_in_small_hdl',
        'total_esterified_cholesterol', 'cholesteryl_esters_in_vldl', 'cholesteryl_esters_in_ldl',
        'cholesteryl_esters_in_hdl',
        'cholesteryl_esters_in_chylomicrons_and_extremely_large_vldl',
        'cholesteryl_esters_in_very_large_vldl', 'cholesteryl_esters_in_large_vldl',
        'cholesteryl_esters_in_medium_vldl', 'cholesteryl_esters_in_small_vldl',
        'cholesteryl_esters_in_very_small_vldl', 'cholesteryl_esters_in_idl',
        'cholesteryl_esters_in_large_ldl', 'cholesteryl_esters_in_medium_ldl',
        'cholesteryl_esters_in_small_ldl', 'cholesteryl_esters_in_very_large_hdl',
        'cholesteryl_esters_in_large_hdl', 'cholesteryl_esters_in_medium_hdl',
        'cholesteryl_esters_in_small_hdl', 'total_free_cholesterol', 'free_cholesterol_in_vldl',
        'free_cholesterol_in_ldl', 'free_cholesterol_in_hdl',
        'free_cholesterol_in_chylomicrons_and_extremely_large_vldl',
        'free_cholesterol_in_very_large_vldl', 'free_cholesterol_in_large_vldl',
        'free_cholesterol_in_medium_vldl', 'free_cholesterol_in_small_vldl',
        'free_cholesterol_in_very_small_vldl', 'free_cholesterol_in_idl',
        'free_cholesterol_in_large_ldl', 'free_cholesterol_in_medium_ldl',
        'free_cholesterol_in_small_ldl', 'free_cholesterol_in_very_large_hdl',
        'free_cholesterol_in_large_hdl', 'free_cholesterol_in_medium_hdl',
        'free_cholesterol_in_small_hdl', 'total_phospholipids_in_lipoprotein_particles',
        'phospholipids_in_vldl', 'phospholipids_in_ldl', 'phospholipids_in_hdl',
        'phospholipids_in_chylomicrons_and_extremely_large_vldl',
        'phospholipids_in_very_large_vldl', 'phospholipids_in_large_vldl',
        'phospholipids_in_medium_vldl', 'phospholipids_in_small_vldl',
        'phospholipids_in_very_small_vldl', 'phospholipids_in_idl',
        'phospholipids_in_large_ldl', 'phospholipids_in_medium_ldl',
        'phospholipids_in_small_ldl', 'phospholipids_in_very_large_hdl',
        'phospholipids_in_large_hdl', 'phospholipids_in_medium_hdl',
        'phospholipids_in_small_hdl', 'total_lipids_in_lipoprotein_particles',
        'total_lipids_in_vldl', 'total_lipids_in_ldl', 'total_lipids_in_hdl',
        'total_lipids_in_chylomicrons_and_extremely_large_vldl',
        'total_lipids_in_very_large_vldl', 'total_lipids_in_large_vldl',
        'total_lipids_in_medium_vldl', 'total_lipids_in_small_vldl',
        'total_lipids_in_very_small_vldl', 'total_lipids_in_idl',
        'total_lipids_in_large_ldl', 'total_lipids_in_medium_ldl',
        'total_lipids_in_small_ldl', 'total_lipids_in_very_large_hdl',
        'total_lipids_in_large_hdl', 'total_lipids_in_medium_hdl',
        'total_lipids_in_small_hdl', 'phosphoglycerides', 'total_cholines',
        'phosphatidylcholines', 'sphingomyelins', 'total_triglycerides',
        'triglycerides_in_vldl', 'triglycerides_in_ldl', 'triglycerides_in_hdl',
        'triglycerides_in_chylomicrons_and_extremely_large_vldl',
        'triglycerides_in_very_large_vldl', 'triglycerides_in_large_vldl',
        'triglycerides_in_medium_vldl', 'triglycerides_in_small_vldl',
        'triglycerides_in_very_small_vldl', 'triglycerides_in_idl',
        'triglycerides_in_large_ldl', 'triglycerides_in_medium_ldl',
        'triglycerides_in_small_ldl', 'triglycerides_in_very_large_hdl',
        'triglycerides_in_large_hdl', 'triglycerides_in_medium_hdl',
        'triglycerides_in_small_hdl', 'total_fatty_acids', 'degree_of_unsaturation',
        'omega_3_fatty_acids', 'omega_6_fatty_acids', 'polyunsaturated_fatty_acids',
        'monounsaturated_fatty_acids', 'saturated_fatty_acids', 'linoleic_acid',
        'docosahexaenoic_acid', 'glucose', 'lactate', 'pyruvate', 'citrate',
        '3_hydroxybutyrate', 'acetate', 'acetoacetate', 'acetone', 'creatinine',
        'albumin', 'glycoprotein_acetyls',
        'standard_prs_for_alzheimer_s_disease_ad', 'standard_prs_for_cardiovascular_disease_cvd',
        'standard_prs_for_type_1_diabetes_t1d', 'standard_prs_for_type_2_diabetes_t2d',
        'standard_prs_for_atrial_fibrillation_af', 'standard_prs_for_coronary_artery_disease_cad',
        'standard_prs_for_venous_thromboembolic_disease_vte', 'standard_prs_for_ischaemic_stroke_iss',
        'standard_prs_for_asthma_ast', 'standard_prs_for_melanoma_mel',
        'standard_prs_for_bowel_cancer_crc', 'standard_prs_for_prostate_cancer_pc',
        'standard_prs_for_breast_cancer_bc', 'standard_prs_for_parkinson_s_disease_pd',
        'standard_prs_for_osteoporosis_op', 'standard_prs_for_primary_open_angle_glaucoma_poag',
        'standard_prs_for_hypertension_ht'
    ]

    if request.method == 'POST':
        if 'csv_file' not in request.FILES:
            return render(request, 'cardiovascular_app/batch_prediction.html', {'error': 'No file uploaded'})
        
        csv_file = request.FILES['csv_file']
        if not csv_file.name.endswith('.csv'):
            return render(request, 'cardiovascular_app/batch_prediction.html', {'error': 'Please upload a CSV file'})
        
        # Check if the confirmation checkbox is checked
        if not request.POST.get('confirm_data'):
            return render(request, 'cardiovascular_app/batch_prediction.html', {'error': 'Please confirm that you have reviewed the data'})
        
        try:
            # Read the CSV file
            df = pd.read_csv(csv_file)
            
            # Clean column names: strip whitespace, convert to lowercase, and replace spaces/special characters with underscores
            df.columns = df.columns.str.strip().str.lower().str.replace(r'[^a-z0-9]+', '_', regex=True)

            # Ensure all required columns exist in the DataFrame, adding them with NaN if not present
            for col in required_columns:
                if col not in df.columns:
                    df[col] = np.nan

            # Impute missing values (NaNs) across the DataFrame
            for col in required_columns:
                if col in ['nhs_number', 'age', 'height', 'weight'] or 'cholesterol' in col or 'triglycerides' in col or 'glucose' in col or 'pressure' in col or 'acid' in col or 'lactate' in col or 'pyruvate' in col or 'citrate' in col or 'creatinine' in col or 'albumin' in col or 'glycoprotein' in col or 'prs' in col or 'diameter' in col or 'concentration' in col or 'lipids' in col or 'phospholipids' in col or 'esters' in col or 'fatty' in col or 'cholines' in col or 'hydroxybutyrate' in col or 'acetate' in col or 'acetoacetate' in col or 'acetone' in col: 
                    df[col] = df[col].fillna(0)  # Impute numerical with 0
                elif col in ['gender', 'smoking', 'alcohol']:
                    df[col] = df[col].fillna('unknown') # Impute categorical with 'unknown'
                else:
                    df[col] = df[col].fillna('') # Impute other with empty string

            # Calculate completeness based on original non-NaN values for display purposes
            initial_present_columns = [col for col in required_columns if df[col].dropna().any()]
            present_columns_count = len(initial_present_columns)
            total_required_columns = len(required_columns)
            
            if total_required_columns > 0:
                completeness_percentage = (present_columns_count / total_required_columns) * 100
            else:
                completeness_percentage = 0

            missing_columns_for_display = [col for col in required_columns if col not in initial_present_columns]

            # Now proceed with mock prediction
            df['predicted_risk'] = np.random.uniform(0, 1, size=len(df))
            df['risk_category'] = pd.cut(df['predicted_risk'], 
                                       bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
                                       labels=['Very Low', 'Low', 'Medium', 'High', 'Very High'])
            
            # Store the DataFrame and completeness info in the session
            request.session['predicted_df'] = df.to_json(orient='records')
            request.session['completeness_info'] = {
                'present_columns_count': present_columns_count,
                'total_required_columns': total_required_columns,
                'completeness_percentage': round(completeness_percentage, 2),
                'missing_columns': missing_columns_for_display,
            }
            
            # Get rows per page from request, default to 25
            rows_per_page = int(request.GET.get('rows_per_page', 25))
            
            # Convert DataFrame to list of dictionaries for pagination
            data = df.to_dict('records')
            
            # Create paginator
            paginator = Paginator(data, rows_per_page)
            page_number = request.GET.get('page', 1)
            page_obj = paginator.get_page(page_number)
            
            return render(request, 'cardiovascular_app/batch_prediction.html', {
                'show_results': True,
                'columns': df.columns.tolist(),
                'paginated_data': page_obj,
                'page_obj': page_obj,
                'rows_per_page': rows_per_page,
                'present_columns_count': present_columns_count,
                'total_required_columns': total_required_columns,
                'completeness_percentage': round(completeness_percentage, 2),
                'missing_columns': missing_columns_for_display,
            })
            
        except Exception as e:
            return render(request, 'cardiovascular_app/batch_prediction.html', {'error': str(e)})
    
    # GET request handling
    if 'predicted_df' in request.session:
        try:
            # Get rows per page from request, default to 25
            rows_per_page = int(request.GET.get('rows_per_page', 25))
            
            # Load the DataFrame from session
            df = pd.read_json(StringIO(request.session['predicted_df']))
            
            # Retrieve completeness info from session
            completeness_info = request.session.get('completeness_info', {})
            present_columns_count_get_request = completeness_info.get('present_columns_count', 0)
            total_required_columns_get_request = completeness_info.get('total_required_columns', 0)
            completeness_percentage_get_request = completeness_info.get('completeness_percentage', 0)
            missing_columns_get_request = completeness_info.get('missing_columns', [])
            
            # Convert DataFrame to list of dictionaries for pagination
            data = df.to_dict('records')
            
            # Create paginator
            paginator = Paginator(data, rows_per_page)
            page_number = request.GET.get('page', 1)
            page_obj = paginator.get_page(page_number)
            
            return render(request, 'cardiovascular_app/batch_prediction.html', {
                'show_results': True,
                'columns': df.columns.tolist(),
                'paginated_data': page_obj,
                'page_obj': page_obj,
                'rows_per_page': rows_per_page,
                'present_columns_count': present_columns_count_get_request,
                'total_required_columns': total_required_columns_get_request,
                'completeness_percentage': round(completeness_percentage_get_request, 2),
                'missing_columns': missing_columns_get_request,
            })
        except Exception as e:
            return render(request, 'cardiovascular_app/batch_prediction.html', {'error': str(e)})
    
    # Initial GET request for the empty form (before any file upload)
    return render(request, 'cardiovascular_app/batch_prediction.html', {'total_required_columns': len(required_columns)})

@login_required
def download_all_data(request):
    if request.user.role != 'clinician' and request.user.role != 'admin':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')
        
    predicted_df_json = request.session.get('predicted_df')
    
    if not predicted_df_json:
        messages.error(request, 'No prediction results available for download.')
        return redirect('batch_prediction')
        
    df = pd.read_json(predicted_df_json)

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="prediction_results.csv"'

    # Write the DataFrame to the CSV.
    df.to_csv(path_or_buf=response, index=False)

    return response

@login_required
def download_filtered_data(request):
    if request.user.role != 'clinician' and request.user.role != 'admin':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')
        
    predicted_df_json = request.session.get('predicted_df')
    
    if not predicted_df_json:
        messages.error(request, 'No prediction results available for download.')
        return redirect('batch_prediction')
        
    df = pd.read_json(predicted_df_json)

    # Get filtering parameters from GET request
    patient_indices_str = request.GET.get('indices')
    limit_str = request.GET.get('limit')

    filtered_df = df

    try:
        if patient_indices_str:
            patient_indices = [int(i) for i in patient_indices_str.split(',')]
            # Filter by indices, ensuring indices are within bounds
            valid_indices = [i for i in patient_indices if 0 <= i < len(df)]
            filtered_df = df.iloc[valid_indices]
            if len(valid_indices) != len(patient_indices):
                 messages.warning(request, 'Some provided patient indices were invalid and were ignored.')

        elif limit_str:
            limit = int(limit_str)
            if limit > 0:
                filtered_df = df.head(limit)
            else:
                messages.warning(request, 'Limit must be a positive integer.')
                filtered_df = pd.DataFrame() # Return empty if limit is invalid

    except ValueError:
        messages.error(request, 'Invalid filtering parameters.')
        return redirect('batch_prediction')
    except Exception as e:
        messages.error(request, f'Error applying filter: {e}')
        return redirect('batch_prediction')
        
    if filtered_df.empty:
        messages.info(request, 'No data matched the filtering criteria.')
        return redirect('batch_prediction')

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="filtered_prediction_results.csv"'

    # Write the DataFrame to the CSV.
    filtered_df.to_csv(path_or_buf=response, index=False)

    return response

@login_required
def download_single_patient_data(request, patient_index):
    if request.user.role != 'clinician' and request.user.role != 'admin':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')
        
    predicted_df_json = request.session.get('predicted_df')
    
    if not predicted_df_json:
        messages.error(request, 'No prediction results available for download.')
        return redirect('batch_prediction')
        
    df = pd.read_json(predicted_df_json)

    try:
        # Check if the index is valid
        if 0 <= patient_index < len(df):
            single_patient_df = df.iloc[[patient_index]]
            
            # Create the HttpResponse object
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="patient_{patient_index}_data.csv"'

            # Write the DataFrame to the CSV.
            single_patient_df.to_csv(path_or_buf=response, index=False)

            return response
        else:
            messages.error(request, 'Invalid patient index.')
            return redirect('batch_prediction')
            
    except Exception as e:
        messages.error(request, f'Error downloading single patient data: {e}')
        return redirect('batch_prediction')

@login_required
def prediction_results_view(request):
    if request.user.role != 'clinician' and request.user.role != 'admin':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')

    predicted_df_json = request.session.get('predicted_df')

    if not predicted_df_json:
        messages.error(request, 'No prediction results available.')
        return redirect('batch_prediction')

    df = pd.read_json(predicted_df_json)

    # Pass the DataFrame with results as a list of dictionaries to the template
    data_for_template = df.to_dict('records')
    columns_for_template = df.columns.tolist()

    return render(request, 'cardiovascular_app/prediction_results.html', {
        'data': data_for_template,
        'columns': columns_for_template
    })

@login_required
def admin_panel(request):
    if request.user.role != 'admin':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')
    
    all_access_requests = AccessRequest.objects.all().order_by('-created_at')
    all_users = User.objects.all().order_by('date_joined')

    context = {
        'all_access_requests': all_access_requests,
        'all_users': all_users,
    }
    return render(request, 'cardiovascular_app/admin_panel.html', context)

@login_required
def approve_request(request, request_id):
    if request.user.role != 'admin':
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('home')
    
    if request.method == 'POST':
        access_request = get_object_or_404(AccessRequest, id=request_id)
        access_request.status = 'approved'
        access_request.save()
        
        # Create user or update approval status if they exist
        try:
            user = User.objects.get(email=access_request.email)
            user.is_approved = True
            user.save()
            messages.success(request, f'Access request from {access_request.full_name} approved. Existing user account updated.')
        except User.DoesNotExist:
            # Create a new user account if one doesn't exist
            user = User.objects.create_user(
                email=access_request.email,
                password=access_request.password, 
                full_name=access_request.full_name,
                affiliation=access_request.affiliation,
                reason_for_access=access_request.message, 
                role='clinician', 
                is_approved=True
            )
            user.save()
            messages.success(request, f'Access request from {access_request.full_name} approved. New user account created.')

        
        return redirect('admin_panel')
    else:
        messages.error(request, 'Invalid request method.')
        return redirect('admin_panel')

@login_required
def reject_request(request, request_id):
    if request.user.role != 'admin':
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('home')
    
    if request.method == 'POST':
        access_request = get_object_or_404(AccessRequest, id=request_id)
        access_request.status = 'rejected'
        access_request.save()
        
        messages.success(request, f'Access request from {access_request.full_name} has been rejected.')
        return redirect('admin_panel')
    else:
        messages.error(request, 'Invalid request method.')
        return redirect('admin_panel')

@login_required
def delete_user(request, user_id):
    if request.user.role != 'admin':
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('home')

    user_to_delete = get_object_or_404(User, id=user_id)

    # Prevent deleting the currently logged-in admin user
    if user_to_delete == request.user:
        messages.error(request, 'You cannot delete your own admin account.')
        return redirect('admin_panel')

    user_to_delete.delete()
    messages.success(request, f'User {user_to_delete.email} has been deleted.')
    return redirect('admin_panel')

@login_required
def reset_batch_prediction(request):
    if request.user.role != 'clinician' and request.user.role != 'admin':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')

    # Clear the predicted data from the session
    if 'predicted_df' in request.session:
        del request.session['predicted_df']
        
    messages.success(request, 'You can now upload a new batch.')
    return redirect('batch_prediction')

@login_required
def process_pending_batch(request):
    if request.user.role != 'clinician' and request.user.role != 'admin':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')

    pending_df_json = request.session.get('pending_prediction_df')

    if not pending_df_json:
        messages.error(request, 'No data found for processing.')
        return redirect('batch_prediction')

    df = pd.read_json(pending_df_json)

    # Perform the prediction
    # Mock prediction function (replace with actual model)
    def predict_risk(row):
        # This is a simplified mock prediction
        risk_score = (
            row['age'] * 0.1 +
            row['systolic_bp'] * 0.2 +
            row['cholesterol'] * 0.15 +
            row['glucose'] * 0.1 +
            (1 if row['smoking'] == 'yes' else 0) * 20 +
            (1 if row['alcohol'] == 'yes' else 0) * 10
        ) / 100
        return min(max(risk_score, 0), 1)

    # Apply prediction and add results to DataFrame
    df['risk_score'] = df.apply(lambda row: predict_risk(row), axis=1)
    df['risk_level'] = df['risk_score'].apply(lambda score: 'High' if score > 0.7 else 'Medium' if score > 0.3 else 'Low')

    # TODO: Implement database saving logic here
    # Save batch run details and results to the database
    # Example (will need actual model integration):
    # batch_run = BatchPredictionRun.objects.create(user=request.user, num_records=len(df), file_name='uploaded_batch.csv') # Replace filename
    # for index, row in df.iterrows():
    #     BatchPredictionResultDetail.objects.create(batch_run=batch_run, original_row_index=index, **row.to_dict())

    # Store the final predicted DataFrame in the session
    request.session['predicted_df'] = df.to_json()

    # Clear the pending data from the session
    del request.session['pending_prediction_df']

    messages.success(request, 'Batch prediction processed successfully!')
    return redirect('batch_prediction') # Redirect to the same page to show results

@login_required
#def patient_detail_history(request, patient_id):
    if request.user.role not in ['clinician', 'admin']:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')

    patient = get_object_or_404(Patient, pk=patient_id)
    records = patient.records.all().order_by('timestamp') # Order by timestamp for history

    return render(request, 'cardiovascular_app/patient_detail_history.html', {
        'patient': patient,
        'records': records
    })

@login_required
def patient_list_review(request):
    if request.user.role not in ['clinician', 'admin']:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')

    patients = Patient.objects.all().prefetch_related('records')

    # Get filter parameters from the request
    nhs_number = request.GET.get('nhs_number')
    first_name = request.GET.get('first_name')
    last_name = request.GET.get('last_name')
    age = request.GET.get('age')
    gender = request.GET.get('gender')
    ethnicity = request.GET.get('ethnicity')

    # Build filter query
    filter_query = Q()
    if nhs_number:
        filter_query &= Q(nhs_number__icontains=nhs_number)
    if first_name:
        filter_query &= Q(first_name__icontains=first_name)
    if last_name:
        filter_query &= Q(last_name__icontains=last_name)
    if age:
        # Ensure age is an integer before filtering
        try:
            age = int(age)
            filter_query &= Q(age=age)
        except ValueError:
            # Optionally handle invalid age input, e.g., display a message
            pass # For now, just ignore invalid age input
    if gender:
        filter_query &= Q(gender__iexact=gender) # Use iexact for case-insensitive exact match
    if ethnicity:
        filter_query &= Q(ethnicity__icontains=ethnicity)

    # Apply the filter to the queryset
    patients = patients.filter(filter_query)

    patient_data = []
    for patient in patients:
        latest_record = patient.records.order_by('-timestamp').first()
        patient_data.append({
            'patient': patient,
            'record_count': patient.records.count(),
            'latest_prediction_score': latest_record.predicted_risk if latest_record else None,
            'latest_record_date': latest_record.timestamp if latest_record else None,
        })

    return render(request, 'cardiovascular_app/patient_list_review.html', {
        'patient_data': patient_data,
        # We don't need to pass the individual query parameters back explicitly
        # because the template uses request.GET to retain the values in the form.
    })

def download_data_entry_template(request):
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data_entry_template.csv')
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename='data_entry_template.csv')
    else:
        raise Http404("Template not found.")

def download_feature_documentation(request):
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'feature_documentation.csv')
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename='feature_documentation.csv')
    else:
        raise Http404("Documentation not found.")from django.shortcuts import render, redirect, get_object_or_404
