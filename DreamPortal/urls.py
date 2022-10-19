"""
Definition of urls for DreamPortal.
"""

from datetime import datetime

from app import forms, views
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import path

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('login/',
         LoginView.as_view
         (
             template_name='app/login.html',
             authentication_form=forms.BootstrapAuthenticationForm,
             extra_context={
                 'title': 'Log in',
                 'year': datetime.now().year,
             }
         ),
         name='login'),
    path('login/recover-credentials/', views.forgot_creds, name='forgotcreds'),
    path('alogin/<id>/<lastname>/<redirect_to>/',
         views.login_redirect, name='autologinredir'),
    path('alogin/<id>/<lastname>/', views.login_redirect, name='autologin'),
    path('logout/', views.logout, name='logout'),
    #path('admin/', admin.site.urls),
    path('profile/', views.profile, name='profile'),
    path('profile/submit-a-document', views.submit_file, name='submit_doc'),



    path('events/', views.events, name='events'),
    path('events/rsvp/', views.rsvp, name='rsvp'),
    path('events/volunteer/', views.volunteer, name='volunteer'),

    path('survey/<questions>/<redir>/', views.survey, name='survey_redir'),
    path('survey/<questions>/', views.survey, name='survey'),
    path('mentee/sign-up/', views.mentee_signup, name='mentee_signup'),

    path('scholarship/', views.scholarship_home, name='scholarship_homepage'),
    path('scholarship/redir/', views.scholarship_redirect,
         name='scholarship_redir'),
    path('scholarship/create_account/',
         views.create_account, name='scholarship_start'),
    path('scholarship/submit_documents/',
         views.scholarship_application_submit, name='scholarship_documents'),

    path('scholarship/recommendation/', views.submit_rec, name='submit_rec'),
    path('scholarship/acceptance/', views.acceptance_form, name='acceptance_form'),

    path('scholarship/review/', views.reviewer_portal, name='review'),
    path('scholarship/interview/', views.interview_portal, name='interview'),
    path('scholarship/interview/sign-up/',
         views.interview_schedule, name='interview_schedule'),
    path('scholarship/interview/student/sign-up/',
         views.interview_schedule_students, name='interview_schedule_students'),
    path('scholarship/interview/password/',
         views.interview_pwd, name='interview_pwd'),

    path('scholarship/<app_type>/',
         views.scholarship_application, name='scholarship_app'),
    path('error/', views.error, name='error'),
]


def error_handler(request, exception=None):
    return redirect("error")


handler404 = error_handler
handler500 = error_handler
handler403 = error_handler
handler400 = error_handler
