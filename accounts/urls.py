from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from accounts.views import assessment_view  # from Sanjana's side

urlpatterns = [
    # ----------------- Shared or Similar Paths -------------------
    path('', views.home, name='home'),  # Mohammed
    #path('starter/', views.home_view, name='starter-page'),  # Sanjana

    path('about/', views.about, name='about'),  # Mohammed
    path('contact/', views.contact, name='contact'),  # Mohammed

    path('request-access/', views.request_access, name='request_access'),  # Mohammed
    # path('request-access/', views.request_access_view, name='request_access'),  # Sanjana - use one or merge logic

    #path('signup/', views.signup, name='signup'),  # Mohammed
    path('signup/', views.signup_view, name='signup'),  # Sanjana

    # ----------------- Authentication -------------------
    path('login/', views.login_view, name='login'),  # Sanjana
    path('logout/', views.logout_view, name='logout'),  # Sanjana
    path('dashboard/', views.role_based_dashboard_redirect, name='dashboard_redirect'),  # Sanjana

    # ----------------- Password Reset URLs -------------------
    # Sanjana's password reset views
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'), name='password_reset_sanjana'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done_sanjana'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), name='password_reset_confirm_sanjana'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), name='password_reset_complete_sanjana'),

    # Mohammed's password reset views
    path('password_reset_alt/', auth_views.PasswordResetView.as_view(template_name='cardiovascular_app/password_reset_form.html'), name='password_reset_mohammed'),
    path('password_reset/done_alt/', auth_views.PasswordResetDoneView.as_view(template_name='cardiovascular_app/password_reset_done.html'), name='password_reset_done_mohammed'),
    path('reset/<uidb64>/<token>/alt/', auth_views.PasswordResetConfirmView.as_view(template_name='cardiovascular_app/password_reset_confirm.html'), name='password_reset_confirm_mohammed'),
    path('reset/done/alt/', auth_views.PasswordResetCompleteView.as_view(template_name='cardiovascular_app/password_reset_complete.html'), name='password_reset_complete_mohammed'),

    # ----------------- Admin URLs -------------------
    #path('admin/login/', views.admin_login_view, name='admin_login'),  # Sanjana
    #path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),  # Sanjana
    path('admin-panel/', views.admin_panel, name='admin_panel'),  # Mohammed
    

    # ----------------- Patient Views -------------------
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),  # Sanjana
    path('patient/assessment/', views.assessment_view, name='start_assessment'),  # Sanjana
    path('patient/<int:patient_id>/results/', views.clinician_patient_results, name='clinician_patient_results'),  # Sanjana
    path('patient/results/', views.patient_self_results, name='patient_self_results'),  # Sanjana
    path('patient/history/', views.assessment_history, name='assessment_history'),  # Sanjana
    path('patient/learn/', views.patient_learn, name='patient_learn'),  # Sanjana

    # ----------------- Clinician Views -------------------
    path('clinician/dashboard/', views.clinician_dashboard, name='clinician_dashboard'),  # Sanjana

    # ----------------- Mohammed's Data & Batch Prediction -------------------
    path('batch-prediction/', views.batch_prediction, name='batch_prediction'),  # Mohammed
    path('prediction-results/', views.prediction_results_view, name='prediction_results'),  # Mohammed
    path('download-all-data/', views.download_all_data, name='download_all_data'),  # Mohammed
    path('download-single-patient-data/<int:patient_index>/', views.download_single_patient_data, name='download_single_patient_data'),  # Mohammed
    path('download-filtered-data/', views.download_filtered_data, name='download_filtered_data'),  # Mohammed
    path('process-pending-batch/', views.process_pending_batch, name='process_pending_batch'),  # Mohammed
    path('reset-batch-prediction/', views.reset_batch_prediction, name='reset_batch_prediction'),  # Mohammed

    # ----------------- Mohammed's Admin Features -------------------
    path('approve-request/<int:request_id>/', views.approve_request, name='approve_request'),  # Mohammed
    path('reject-request/<int:request_id>/', views.reject_request, name='reject_request'),  # Mohammed
    path('patient-records/', views.patient_list_review, name='patient_list_review'),  # Mohammed
    path('patient-records/<int:patient_id>/', views.patient_detail_history, name='patient_detail_history'),  # Mohammed
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),  # Mohammed

    # ----------------- Mohammed's Downloads -------------------
    path('download-data-entry-template/', views.download_data_entry_template, name='download_data_entry_template'),  # Mohammed
    path('download-feature-documentation/', views.download_feature_documentation, name='download_feature_documentation'),  # Mohammed
]
