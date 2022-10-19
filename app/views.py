"""
Definition of views.
"""
import base64
import os
import random
import re
from datetime import datetime, timedelta

import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as auth_logout
from django.core.mail import send_mail
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect, render

import app.emails as emails
import app.survey_vars as sv
from app.customauth import Salesforcer, scholarship_info
from app.forms import (EditUserPass, Forgot_creds, ScholarshipAttachments,
                       SubmitAppReview, SubmitDoc, SubmitRec, Survey,
                       UnauthSignup, UpdateProfileDonor, UpdateProfileGeneral,
                       UpdateProfileMentee, UpdateProfileScholar)
from app.models import temp_user
from app.survey_classes import Divider, Question
from app.surveys import surveys


def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    reviewer = False
    if request.user.is_authenticated and request.user.type_of_user not in ['scholar', 'mentee', 'prospective']:
        sf = Salesforcer()
        info = sf.query(f"SELECT Id FROM Scholarship_Reviewer__c WHERE Contact__c='{request.user.id}'\
            AND Scholarship_Review_Year__c='{sv.updated_vars['scholarship_review_year']}'")
        if info['totalSize']:
            reviewer = True

    return render(
        request,
        'app/home.html',
        {
            'title': 'Home',
            'reviewer': reviewer,
            'year': datetime.now().year,
        }
    )


def forgot_creds(request):
    """Emails credentials to user"""
    form = Forgot_creds()
    if request.method == 'POST':
        form = Forgot_creds(data=request.POST)
        if form.is_valid():
            if form.save():
                messages.info(
                    request, 'An email has been sent with your login information. Make sure to check your spam folder.')
            else:
                messages.error(
                    request, 'Unable to find an account associated with that email')
            return HttpResponseRedirect('/login/')
    return render(
        request,
        'app/recover-credentials.html',
        {
            'title': 'Recover Credentials',
            'desc': 'To change your username and/or password you must have your Dream ID',
            'year': datetime.now().year,
            'form': form,
        }
    )


def about(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title': 'About',
            'year': datetime.now().year,
        }
    )


def profile(request):
    """Renders user profile page"""
    assert isinstance(request, HttpRequest)
    user = request.user
    scholarships = scholarship_info(
        user.scholarships) if user.type_of_user == 'donor' else ''
    if request.method == 'POST':

        # Changing username
        if 'usrnm' in request.POST:
            form = EditUserPass(initial={'New_User': user.usrnm})
            return render(request,
                          'app/profile-edit-creds.html',
                          {
                              'title': 'Edit Log In Information',
                              'desc': '',
                              'form': form,
                              'year': datetime.now().year,
                          })

        # Saving username
        elif 'saveusr' in request.POST:
            form = EditUserPass(data=request.POST)
            if form.is_valid():
                form.save(user=user)
                messages.info(
                    request, 'Login information has been updated successfully!')
                next = request.POST.get('next', '/')
                return HttpResponseRedirect(next)
            else:
                return render(request,
                              'app/profile-edit-creds.html',
                              {
                                  'title': 'Edit Log In Information',
                                  'form': form,
                                  'year': datetime.now().year,
                              })
        else:

            # Cancel operation and go back
            if 'cancel' in request.POST:
                next = request.POST.get('next', '/')
                return HttpResponseRedirect(next)

            # Sets form depending on user
            if user.type_of_user == 'scholar':
                fn = UpdateProfileScholar
            elif user.type_of_user == 'donor':
                fn = UpdateProfileDonor
            elif user.type_of_user == 'mentee':
                fn = UpdateProfileMentee
            else:
                fn = UpdateProfileGeneral

            # Saving changes to their profile
            if 'save' in request.POST:
                if user.type_of_user == 'donor':
                    form = fn(data=request.POST, instance=user,
                              scholarships=scholarships)
                else:
                    form = fn(data=request.POST, instance=user)

            # Initializes form to make changes
            else:
                if user.type_of_user == 'donor':
                    form = fn(instance=user, scholarships=scholarships)
                else:
                    form = fn(instance=user)

            # Save changes to profile if changes are valid
            if form.is_valid():
                form.save(pk=user.pk, scholarships=scholarships)
                next = request.POST.get('next', '/')
                return HttpResponseRedirect(next)
            return render(request,
                          'app/profile-edit.html',
                          {
                              'title': 'Edit Profile',
                              'form': form,
                              'year': datetime.now().year,
                              'scholarships': scholarships,
                              'range': range(len(scholarships)),
                          })

    # Fixes phone number display upon opening profile
    if user.phone:
        try:
            phone = ('(%s) %s-%s' %
                     tuple(re.findall(r'\d{4}$|\d{3}', user.phone)))
        except:
            phone = user.phone
    else:
        phone = None
    return render(
        request,
        'app/profile.html',
        {
            'title': 'Profile',
            'year': datetime.now().year,
            'phone': phone,
            'scholarships': scholarships,
        }
    )


def login_redirect(request, id, lastname, redirect_to=False):
    """Automatically logs in and redirects user to specified page
    Used in tandem with login link on SF"""
    if request.user.is_authenticated:
        old_user = request.user
        auth_logout(request)
        old_user.delete()

    pwd = lastname.replace("&", " ")
    user = authenticate(request, username=id, password=pwd)
    if redirect_to:
        dir = redirect_to.replace("&", '/')
    else:
        dir = ''
    if user is not None:
        login(request, user)
    else:
        return HttpResponseRedirect('/login/')
    return HttpResponseRedirect(f'/{dir}')


def logout(request, next_page='/', template_name='app/index.html', current_app=None, extra_context=None):
    """Logs user out"""
    assert isinstance(request, HttpRequest)
    user = request.user
    auth_logout(request)
    user.delete()
    return HttpResponseRedirect('/')


def events(request):
    """Renders the event page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/events.html',
        {
            'title': 'Events',
            'year': datetime.now().year,
        }
    )


def rsvp(request):
    """Renders RSVP page"""
    assert isinstance(request, HttpRequest)

    user = request.user
    list_of_events = []
    sf = Salesforcer()
    if request.method == 'POST':
        ID = list(request.POST.keys())[-1]
        try:
            sf.CampaignMember.create({'CampaignId': ID,
                                      'ContactId': user.id,
                                      'Status': 'Responded',
                                      'Will_Attend__c': True if request.POST[ID] == 'Will Attend' else False})
        except:
            try:
                sf.CampaignMember.delete(ID)
            except Exception as error:
                print(error)
                messages.error(request, 'There was an error')

    # List of events
    events = sf.query(
        "SELECT Id, Name, StartDate, Time__c FROM Campaign WHERE Status='Planned' AND Type='Conference' ORDER BY StartDate ASC")
    for event in events['records']:
        if event['StartDate']:
            if datetime.now() - timedelta(days=1) <= datetime.strptime(event['StartDate'], '%Y-%m-%d'):
                event['StartDate'] = event['StartDate'][5:]
            else:
                continue
        else:
            event['StartDate'] = ''

        # Check if they RSVPed already
        member = sf.query(
            f"SELECT Id, Guests__c, Will_Attend__c FROM CampaignMember WHERE CampaignID='{event['Id']}' AND ContactId='{user.id}'")
        if member['totalSize']:
            event['RSVP'] = True
            event['coming'] = True if member['records'][0]['Will_Attend__c'] else False
            event['guests'] = int(member['records'][0]['Guests__c'])
            event['membid'] = member['records'][0]['Id']
        else:
            event['RSVP'] = False
        list_of_events.append(event)

    return render(
        request,
        'app/events-rsvp.html',
        {
            'title': 'Upcoming Events',
            'year': datetime.now().year,
            'events': list_of_events,
            'len': len(list_of_events)
        }
    )


def volunteer(request):
    """Renders volunteer page"""
    assert isinstance(request, HttpRequest)

    list_of_events = {}
    sf = Salesforcer()
    if request.method == 'POST':
        ID = list(request.POST.keys())[1]
        if request.POST[ID] == "Sign Up":
            sf.Volunteer_Job__c.update(ID, {'Contact__c': request.user.pk})
        else:
            sf.Volunteer_Job__c.update(ID, {'Contact__c': ''})

    # list of events
    events = sf.query(
        "SELECT Id, Name, StartDate FROM Campaign WHERE Status='Planned' AND Type='Conference' AND Volunteers_Needed__c > 0")
    for event in events['records']:

        if event['StartDate']:
            if datetime.now() <= datetime.strptime(event['StartDate'], '%Y-%m-%d'):
                event['StartDate'] = event['StartDate'][5:]
            else:
                continue

        volunteers = sf.query(
            f"SELECT Id, Name, Shift__c, Campaign__c, Contact__c FROM Volunteer_Job__c WHERE Campaign__c='{event['Id']}' AND (Contact__c = '' OR Contact__c = '{request.user.pk}')")
        name = f"{event['Name']} | {event['StartDate']}"
        list_of_events[name] = volunteers['records']
    return render(
        request,
        'app/events-volunteer.html',
        {
            'title': 'Volunteer for an Event',
            'year': datetime.now().year,
            'events': list_of_events,
            'len': len(list_of_events)
        }
    )


def survey(request, questions, redir="/"):
    """Universal survey renderer"""
    assert isinstance(request, HttpRequest)
    if redir != "/":
        redir = f"/{redir}".replace("&", "/")

    instructions = "Please respond to the following statements to the best of your ability."

    # Stored name of survey in Salesforce
    svy = f"{questions.title()} {sv.updated_vars['summer_fall_s']}"

    # Gets survey questions and creates form
    complete_survey = surveys.get(questions)
    form = Survey(complete_survey, shuffle='')

    # Checks to see if survey has instructions attached and overrides default
    if not isinstance(complete_survey[0], (Question, Divider)):
        instructions = complete_survey[0]

    # Checks if this is a multiple part survey, if so it sets the next part of it
    last = questions.split("-")[-1]
    next_part = None
    if len(last) == 1 and last.isdigit():
        if surveys.get(f"{questions[0:-1]}{int(last)+1}"):
            next_part = f'/survey/{questions[0:-1]}{int(last)+1}'

    sf = Salesforcer()
    if request.method == 'POST':
        form = Survey(complete_survey, data=request.POST)
        if form.is_valid():
            form.save(sf, svy, request.user.pk)

            # Redirect to next part if exists
            if next_part:
                return HttpResponseRedirect(next_part)
            else:
                messages.info(
                    request, "Submitted Successfully. Thank you!")
                return HttpResponseRedirect(redir)

    if object_exists(sf, 'Surveys__c', 'Contact__c', request.user.pk, {'name': 'Name', 'value': svy}):
        if next_part:
            return HttpResponseRedirect(next_part)

        if redir == "/":
            messages.error(
                request, "You've already submitted this survey. Thanks!")

        return HttpResponseRedirect(redir)

    return render(
        request,
        'app/survey.html',
        {
            'title': questions.replace('-', ' ').replace('_', ' ').title(),
            'year': datetime.now().year,
            'instructions': instructions,
            'form': form,
            'scale': sv.Scales
        }
    )


def acceptance_form(request):
    """Renders the acceptance form"""
    assert isinstance(request, HttpRequest)
    sf = Salesforcer()

    if object_exists(sf, 'Surveys__c', 'Contact__c', request.user.pk, {'name': 'Name', 'value': 'Summit-Assessment 2022 Pre'}):
        questions = surveys.get('acceptance')
        if request.method == 'POST':
            form = Survey(questions, data=request.POST, files=request.FILES)
            if form.is_valid():
                data = {key: val for key, val in form.cleaned_data.items()
                        if val != ""}

                sf.Contact.update(request.user.pk,
                                  {
                                      "Primary_College_Affiliation_Text__c": data.get('college'),
                                      "Student_ID__c": data.get('student_id'),
                                      "Employment_Status__c": data.get('employed'),
                                      "Major_s__c": data.get('major'),
                                      "Minor_s__c": data.get('minor'),
                                      "Expected_Graduation__c": f"B:{data.get('graduation_year')} | A:{data.get('graduation_year_a')}",
                                      "Interested_in_Parent_Committee__c": data.get('parents'),
                                      "Privacy_policy__c": data.get('release'),
                                      "E_signature__c": data.get('sig'),
                                  }
                                  )
                for file in request.FILES:
                    file = request.FILES[file]
                    _, file_extension = os.path.splitext(file.name)
                    sf.Attachment.create({'Name': f"{datetime.now().year} Student Photo{file_extension}", 'ParentId': request.user.pk, 'body': str(
                        base64.b64encode(file.read()))[2:-1]})

                send_mail('Acceptance Form Received - Dream Project Scholarship',
                          'We received your acceptance form--If you have any questions please let me know at carlos@dreamproject-va.org',
                          emails.email_sender,
                          [request.user.email])
                messages.info(
                    request, "Form Submitted Successfully. An email confirmation was sent to your email.")
                return HttpResponseRedirect('/')
        else:
            form = Survey(questions)
        return render(
            request,
            'app/survey.html',
            {
                'title': 'Acceptance Form',
                'year': datetime.now().year,
                'form': form,
                'scale': sv.Scales
            }
        )
    else:
        return HttpResponseRedirect('/scholarship/summit-survey/True/')


def mentee_signup(request):
    """Renders mentee sign up form"""
    assert isinstance(request, HttpRequest)
    form = Survey(surveys.get('mentoring_sign_up'))
    if request.method == 'POST':
        form = Survey(surveys.get('mentoring_sign_up'), data=request.POST)
        if form.is_valid():
            sf = Salesforcer()
            data = form.cleaned_data
            dups = sf.query(
                f"SELECT Id FROM Contact WHERE Email='{data['Email']}'")
            if dups['totalSize'] == 0:
                try:
                    id = sf.Contact.create({'FirstName': data['First Name'],
                                            'LastName': data['Last Name'],
                                            'Email': data['Email'],
                                            'Phone': data['Phone'],
                                            'Areas_of_Interest__c': "\r\n".join(data['interested_in']),
                                            'Ethnicity__c': data['Ethnicity'],
                                            'Country_of_Origin__c': data['Country of Birth'],
                                            'Birthdate': data['Birth Date'].strftime('%Y-%m-%d'),
                                            'Description': data['grade'],
                                            'High_School__c': data['high_school'],
                                            'RecordTypeId': sv.recordtypes['mentee'],
                                            'Employment_Status__c': data['Employment Status'],
                                            'HS_GPA__c': float(data['GPA']),
                                            'Colleges_of_Interest__c': data['dream_schools'],
                                            'FAFSA__c': data['fafsa'],
                                            'Learned_about_Mentoring_Program__c': data['learned_of_dp'],
                                            'Available_for_Mentoring__c': data['available'],
                                            'Will_apply_to__c': data['number_of_applications'],
                                            'Past_Mentee__c': True, },
                                           )

                    send_mail('Dream Portal Login Info',
                              emails.log_in_info(id['id'], data['Last Name']),
                              emails.email_sender,
                              [data['Email']],
                              html_message=emails.log_in_info(id['id'], data['Last Name']))
                    user = authenticate(
                        request, username=id['id'], password=data['Last Name'])
                    messages.info(
                        request, f"Successfully registered! Check your email ({data['Email']}) for instructions on how to log in. Make sure you check your spam folder. If you do not receive this email, please let me know at carlos@dreamproject-va.org")
                    if user is not None:
                        login(request, user)
                        return HttpResponseRedirect('/survey/mentoring_assessment/')
                    else:
                        return HttpResponseRedirect('/')
                except Exception as e:
                    print(e)
                    messages.info(
                        request, f"There was an error, please email me at carlos@dreamproject-va.org")
                    return HttpResponseRedirect('/')
            messages.info(
                request, "Looks like you've previously signed up. If you have any questions please email me at carlos@dreamproject-va.org")
            return HttpResponseRedirect('/')
    return render(
        request,
        'app/scholarship-application.html',
        {
            'title': 'Mentee Sign Up',
            'year': datetime.now().year,
            'form': form,
            'scale': sv.Scales
        }
    )


def submit_rec(request):
    """Renders recommendation upload page for scholarship portal"""
    assert isinstance(request, HttpRequest)
    form = SubmitRec()
    if request.method == 'POST':
        form = SubmitRec(files=request.FILES, data=request.POST)
        if form.is_valid():
            message = form.save()
            if message:
                messages.info(request, message)

    return render(
        request,
        'app/scholarship-rec.html',
        {
            'title': 'Submit a Recommendation',
            'year': datetime.now().year,
            'form': form,
        }
    )


def submit_file(request):
    """Allows users to submit a file directly to SF"""
    assert isinstance(request, HttpRequest)
    if request.method == 'POST':
        form = SubmitDoc(files=request.FILES, data=request.POST)
        if form.is_valid():
            form.save(id=request.user.id)
            messages.info(request, 'Successfully uploaded the document.')
    else:
        form = SubmitDoc()
    return render(
        request,
        'app/submit_doc.html',
        {
            'title': 'Submit a Document',
            'year': datetime.now().year,
            'form': form,
        }
    )


def scholarship_home(request):
    """Renders Scholarship information page"""
    assert isinstance(request, HttpRequest)

    # Check if scholarshp is supposed to be open
    currently_open = False
    if datetime.now().month in [12, 1]:
        currently_open = True
    elif datetime.now().month == 2:
        if datetime.now().day == 1:
            currently_open = True

    return render(
        request,
        'app/scholarship.html',
        {
            'title': 'Dream Project Scholarship',
            'year': datetime.now().year,
            'open': currently_open,
        }
    )


def scholarship_redirect(request):
    """Finds what part of the application a student is in and redirects them to the appropriate part
    This is mainly for students that leave and come back later"""
    assert isinstance(request, HttpRequest)

    if request.method == 'POST':
        form = Survey(surveys.get('app_type'), data=request.POST)
        if form.is_valid():
            data = form.cleaned_data
            return HttpResponseRedirect(f"/scholarship/{data['app_type']}/")

    # If user is logged in check if they have a current application
    if request.user.is_authenticated:
        sf = Salesforcer()
        current_application = sf.query(
            f"SELECT Id FROM Scholarship_Application__c WHERE Contact__c='{request.user.id}' AND Scholarship_Review_Year__c='{sv.updated_vars['scholarship_review_year']}'")
        if not current_application["totalSize"]:
            if request.user.type_of_user == "scholar":
                return HttpResponseRedirect(f"/scholarship/renewal_app/")
            form = Survey(surveys.get('app_type'))
            return render(
                request,
                'app/scholarship-application-selector.html',
                {
                    'title': 'Dream Portal Scholarship Application Selector',
                    'year': datetime.now().year,
                    'form': form,
                }
            )
        else:
            application_details = sf.Scholarship_Application__c.get(
                current_application['records'][0]["Id"])
            if application_details["Completed__c"]:
                messages.info(
                    request, f"Your application is complete!")
                return HttpResponseRedirect("/scholarship/")
            else:
                kind = app_type_convert(application_details['Type__c'])
                return HttpResponseRedirect(f"/scholarship/{kind}/")
    else:
        return HttpResponseRedirect(f"/scholarship/create_account/")


def create_account(request):
    """Account creation page"""
    assert isinstance(request, HttpRequest)
    if request.user.is_authenticated:
        return HttpResponseRedirect('/scholarship')

    form = Survey(surveys.get('create_account'))
    if request.method == 'POST':
        form = Survey(surveys.get('create_account'), data=request.POST)
        if form.is_valid():
            sf = Salesforcer()
            data = form.cleaned_data
            dups = sf.query(
                f"SELECT Id FROM Contact WHERE Email='{data['Email']}'")
            if dups['totalSize'] == 0:
                try:
                    id = sf.Contact.create({'FirstName': data['First Name'],
                                            'LastName': data['Last Name'],
                                            'Email': data['Email'],
                                            'Phone': data['Phone'],
                                            'Ethnicity__c': data['Ethnicity'],
                                            'Country_of_Origin__c': data['Country of Birth'],
                                            'Birthdate': data['Birth Date'].strftime('%Y-%m-%d'),
                                            'RecordTypeId': sv.recordtypes['prospective'],
                                            'Cohort__c': sv.updated_vars['spring_s'],
                                            'MailingStreet': data['Street'],
                                            'MailingCity': data['City'],
                                            'MailingState': data['State'],
                                            'MailingPostalCode': data['Zip'],
                                            }
                                           )

                    # Email confirmation email with login credentials
                    send_mail('Dream Portal Login Info',
                              emails.log_in_info(id['id'], data['Last Name']),
                              emails.email_sender,
                              [data['Email']],
                              html_message=emails.log_in_info(id['id'], data['Last Name']))
                    user = authenticate(
                        request, username=id['id'], password=data['Last Name'])
                    messages.info(
                        request, f"Successfully registered! Check your email ({data['Email']}) for instructions on how to log in (YOU WILL NEED TO BE LOGGED IN IN ORDER TO SUBMIT YOUR APPLICATION). Make sure you check your spam folder. If you do not receive this email, please let me know at carlos@dreamproject-va.org")
                    if user is not None:
                        login(request, user)
                        return HttpResponseRedirect(f"/scholarship/redir/")
                    else:
                        return HttpResponseRedirect('/')
                except Exception as e:
                    messages.info(
                        request, f"There was an error, please email me at carlos@dreamproject-va.org")
                    return HttpResponseRedirect('/')

            messages.info(
                request, "Looks like you've previously signed up. If you have any questions please email me at carlos@dreamproject-va.org")
            return HttpResponseRedirect('/login/recover-credentials/')
    return render(
        request,
        'app/scholarship-application.html',
        {
            'title': 'Dream Portal Scholarship Sign Up',
            'year': datetime.now().year,
            'form': form,
        }
    )


def scholarship_application(request, app_type):
    """Scholarship application handler"""
    assert isinstance(request, HttpRequest)
    if not request.user.is_authenticated:
        HttpResponseRedirect("/scholarship/")

    sf = Salesforcer()

    # Redirect renewal students to right page
    if app_type != "renewal_app":
        if not object_exists(sf, 'Surveys__c', 'Contact__c', request.user.id, {'name': 'Name', 'value': f"General {sv.updated_vars['summer_fall_s']}"}):
            return HttpResponseRedirect('/survey/general/scholarship&redir/')

    if request.method == 'POST':
        form = Survey(surveys.get(app_type), data=request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                exp = data.get('Expected_Graduation__c', " ").strftime('%Y-%m')
            except:
                exp = None

            # Dictionary to match certain form-fields with their Salesforce counterparts
            fields = {
                'Expected_Graduation__c': exp,
                'Financial_Thoughts__c': "\r\n".join(data.get('Financial_Thoughts__c', " ")),
                'Mandatory_Events__c': "\r\n".join(data.get('Mandatory_Events__c', " ")),
                'First_Generation_Student__c': data.get('First_Generation_Student__c', " ") == "Yes",
                'Identifies_as_Dreamer__c': data.get('Identifies_as_Dreamer__c', " ") == "Yes",
                'Recommender_1__c': f"Name: {data.get('Name_Recommender_1__c')} | Title: {data.get('Title_Recommender_1__c')} | Email: {data.get('Email_Recommender_1__c')} | Phone: {data.get('Phone_Recommender_1__c')}",
                'Recommender_2__c': f"Name: {data.get('Name_Recommender_2__c')} | Title: {data.get('Title_Recommender_2__c')} | Email: {data.get('Email_Recommender_2__c')} | Phone: {data.get('Phone_Recommender_2__c')}",
                'Test_Scores__c': f"SAT: {data.get('SAT_Test_Scores__c')} | ACT: {data.get('ACT_Test_Scores__c')}",
                'Current_Number_of_Credits__c': int(data.get('Current_Number_of_Credits__c') if data.get('Current_Number_of_Credits__c') else 0),
                'Commitment_to_Dream_Project__c': "\r\n".join(data.get('Commitment_to_Dream_Project__c', " ")),
                'History_of_Enrollment__c': f"Fall {sv.updated_vars['summer_fall_s']}: {data.get('Fall_History_of_Enrollment__c')} | Spring {sv.updated_vars['spring_s']}: {data.get('Spring_History_of_Enrollment__c')}",
            }

            # Remove values that don't have a matching field on Salesforce from the original form
            for already_in in ["Financial_Thoughts__c", "Name_Recommender_1__c", "Title_Recommender_1__c", "Email_Recommender_1__c", "Phone_Recommender_1__c", "Name_Recommender_2__c", "Title_Recommender_2__c", "Email_Recommender_2__c", "Phone_Recommender_2__c", "SAT_Test_Scores__c", "ACT_Test_Scores__c", "Current_Number_of_Credits__c", "Commitment_to_Dream_Project__c", "Summer_History_of_Enrollment__c", "Fall_History_of_Enrollment__c", "Spring_History_of_Enrollment__c", "E_Signature", "First_Generation_Student__c", "Identifies_as_Dreamer__c", "Mandatory_Events__c", "Expected_Graduation__c"]:
                data.pop(already_in, None)
            for key in list(data.keys()):
                if "divider" in key:
                    data.pop(key)

            # Add remaining values into dictionary used to update Salesforce
            for key, value in data.items():
                try:
                    if value not in [True, False, None]:
                        fields[key] = float(sv.encrypt(value))
                except:
                    fields[key] = sv.encrypt(value)

            # Check if there's a current application, if not create a new one
            current_application = sf.query(
                f"SELECT Id FROM Scholarship_Application__c WHERE Contact__c='{request.user.id}' AND Scholarship_Review_Year__c='{sv.updated_vars['scholarship_review_year']}'")
            if current_application['totalSize'] == 0:
                sf.Scholarship_Application__c.create(fields)
            else:
                sf.Scholarship_Application__c.update(
                    current_application['records'][0]['Id'], fields)

            if "save&cont" in list(request.POST.keys()):
                return HttpResponseRedirect('/scholarship/submit_documents')
            elif "save" in list(request.POST.keys()):
                messages.info(request, "Progress Saved")
                return render(
                    request,
                    'app/scholarship-application.html',
                    {
                        'title': "Dream Project Scholarship Application",
                        'year': datetime.now().year,
                        'form': form,
                        'scale': sv.Scales,
                        'is_post': request.method == "POST"
                    }
                )
    else:

        # Get most recent application
        data = request.user.get_scholarship(sf, app_type_convert(app_type))

        # If it's done say that, oterwise pass it back in to be completed.
        if data.get('Completed__c') == "Yes":
            messages.info(request, 'Your application is complete!')
            return HttpResponseRedirect('/')

        form = Survey(surveys.get(app_type), data=data if data else None)
    return render(
        request,
        'app/scholarship-application.html',
        {
            'title': "Dream Project Scholarship Application",
            'year': datetime.now().year,
            'form': form,
            'scale': sv.Scales,
            'is_post': request.method == "POST"
        }
    )


def scholarship_application_submit(request):
    """Processess finished applications"""
    assert isinstance(request, HttpRequest)
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/scholarship')

    sf = Salesforcer()

    scholarship_id, scholarship_type, scholarship_status = request.user.get_scholarship_info(
        sf)
    if not scholarship_id:
        return HttpResponseRedirect('/scholarship')
    elif scholarship_status:
        messages.info(request, 'Your application is complete!')
        return HttpResponseRedirect('/')

    if request.method == 'POST':
        skip = False
        if "complete" in request.POST.keys():
            scholarship = request.user.get_scholarship(sf, scholarship_type)
            app_complete = validate_scholarship(scholarship, scholarship_type)

            if app_complete:
                # Check if all required documents have been uploaded, if not prompt user to upload missing docs
                requirements = request.user.get_scholarship_attachments(sf)
                all_reqs = {k: v for k, v in requirements.items() if v.get(
                    'R') and not v['Uploaded']}
                if len(all_reqs) > 0:
                    messages.error(
                        request, f"You are missing the following required documents: {', '.join(list(all_reqs.keys()))}")
                    skip = True
                else:
                    # Finish scholarship application and assign reviewers
                    sf.Scholarship_Application__c.update(
                        scholarship_id, {"Completed__c": True})
                    assign_reviewers(scholarship_id, scholarship_type)

                    # Confirmation email
                    send_mail('Application Received - Dream Project Scholarship',
                              emails.log_in_info(
                                  request.user.id, request.user.last),
                              emails.email_sender,
                              [request.user.email],
                              html_message=emails.log_in_info(request.user.id, request.user.last))

                    # Send email to recommenders
                    if request.user.type_of_user != "scholar":
                        try:
                            for i in [1, 2]:
                                send_mail(f"{request.user.name} {request.user.last} selected you as a recommender",
                                          emails.rec_info(
                                              scholarship[f'Name_Recommender_{i}__c'], f"{request.user.name} {request.user.last}", f"{request.user.id}-{i}"),
                                          emails.email_sender,
                                          [scholarship[f'Email_Recommender_{i}__c']],
                                          html_message=emails.rec_info(scholarship[f'Name_Recommender_{i}__c'], f"{request.user.name} {request.user.last}", f"{request.user.id}-{i}"))
                        except:
                            messages.error(
                                "Unable to email your recommenders. Please reach out to me at carlos@dreamproject-va.org")

                    messages.info(
                        request, f"Application received! Check your email for confirmation. If you have any questions or concerns please email me at carlos@dreamproject-va.org. You should expect to hear from us in late February {sv.updated_vars['spring_s']}.")

                    return HttpResponseRedirect('/')

            else:
                messages.error(
                    request, "Your application is incomplete, please check that you've filled all required fields out.")
                skip = True

        for key, value in request.POST.items():
            if value == "Delete":
                skip = True
                sf.Attachment.delete(key)
                messages.info(request, 'Successfully deleted the document.')

        if not skip:
            form = ScholarshipAttachments(
                scholarship_type, files=request.FILES, data=request.POST)
            if form.is_valid():
                if form.save(sf, scholarship_id):
                    messages.info(
                        request, 'Successfully uploaded the document.')
                else:
                    messages.error(
                        request, "You've already uplodaded this document.")

    requirements = request.user.get_scholarship_attachments(sf)
    form = ScholarshipAttachments(scholarship_type)
    return render(
        request,
        'app/scholarship-documents.html',
        {
            'title': 'Dream Project Scholarship Documents',
            'year': datetime.now().year,
            'form': form,
            'requirements': requirements,
        }
    )


def reviewer_portal(request):
    """Houses the reviewer portal"""
    assert isinstance(request, HttpRequest)
    read = 'first'
    if read == 'first':
        page = 'portal-reviewer.html'
    elif read == 'second':
        page = 'portal-reviewer-second-read.html'

    if request.method == "POST":
        sf = Salesforcer()

        id = list(request.POST)[1]  # ID of applicant
        if request.POST[id] == 'View':
            # Download applicants application and attachments
            applicant, attachments, comments = get_application(sf, id)
            show = False
            for comment in comments:
                if comment['Contact__c'] == request.user.id and comment['Complete__c']:
                    show = True
            if not show:
                for comment in comments:
                    if comment['Complete__c']:
                        show = True
                    else:
                        show = False
                        break

            # Creates the form depending on whether it's a reviewer or an observer
            form = SubmitAppReview(comments, request.user)

            # Checks if applicant completed the fall survey or attended the summit
            applicant['fall_survey'] = object_exists(sf, 'Surveys__c', 'Contact__c', applicant['Contact__c'], {
                                                     'name': 'Name', 'value': 'Fall-Survey-Scholars 2021'})

            # These are a list of SF Campaign IDs that count towards the participation requirement for the scholarship
            workshops = [
                # Summit Workshops
                "7011R000000nAGOQA2",
                "7011R000000nAGJQA2",
                "7011R000000nAG5QAM",
                "7011R000000nAG3QAM",
                "7011R000000nAGEQA2",
                "7011R000000nAG4QAM",
                "7011R000000nAG2QAM",
                "7011R000000nAG1QAM",
                "7011R000000nAG0QAM",
                "7011R000000nAFzQAM",


                # Non Summit events
            ]

            # Check if student participated in any events
            applicant['participation'] = False
            for workshop in workshops:
                if object_exists(sf, 'CampaignMember', 'ContactId', applicant['Contact__c'], {
                        'name': 'CampaignId', 'value': workshop}):
                    applicant['participation'] = True
                    break

            # Replaces Salesforce breaks to HTML breaks
            for key in applicant:
                applicant[key] = str(applicant[key]).replace('\r\n', '<br>')

            return render(
                request,
                f'app/{page}',
                {
                    'title': f"Reviewing: {applicant['Last_Name__c']}, {applicant['First_Name__c']}",
                    'year': datetime.now().year,
                    'stage': 3,
                    'applicant': applicant,
                    'attachments': attachments,
                    'comments': comments,
                    'show': show,
                    'reviewer': request.user.id,
                    'form': form
                }
            )

        # User is attempting to submit or save form
        elif 'save' in request.POST or 'save2' in request.POST:
            applicant, attachments, comments = get_application(sf, id)
            show = False
            for comment in comments:
                if comment['Contact__c'] == request.user.id and comment['Complete__c']:
                    show = True

            form = SubmitAppReview(comments, request.user, data=request.POST)
            if form.is_valid():

                # Save the form, don't submit it
                form.save(final=False if 'save2' in request.POST else True)
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/scholarship/review/'))

            else:
                # Form is not valid
                return render(
                    request,
                    'app/portal-reviewer.html',
                    {
                        'title': f"Reviewing: {applicant['LastName']}, {applicant['FirstName']}",
                        'year': datetime.now().year,
                        'stage': 3,
                        'applicant': applicant,
                        'attachments': attachments,
                        'reviewer': request.user.id,
                        'show': show,
                        'form': form
                    }
                )

        # Queries depending on choice
        else:
            applicants = sf.query(f"SELECT Scholarship_Application__c.Id, Scholarship_Application__c.Type__c,\
                            Scholarship_Application__c.Contact__r.FirstName, Scholarship_Application__c.Contact__r.LastName,\
                            (SELECT Decision__c, Complete__c, Scholarship_Reviewer__r.Contact__c, Scholarship_Reviewer__r.Contact__r.FirstName FROM Scholarship_Application__c.Scholarship_Assignments__r) \
                            FROM Scholarship_Application__c WHERE Completed__c=\
                            TRUE AND Ineligible__c=FALSE AND Scholarship_Review_Year__c='{sv.updated_vars['scholarship_review_year']}' \
                            ORDER BY Scholarship_Application__c.Contact__r.LastName ASC")
            new_q = {'records': []}

            # Filters results
            if 'all' in request.POST:
                for applicant in applicants['records']:
                    if applicant['Type__c'] != 'Renewal':
                        new_q['records'].append(applicant)
            elif 'renewal' in request.POST:
                for applicant in applicants['records']:
                    if applicant['Type__c'] == 'Renewal':
                        new_q['records'].append(applicant)
            elif 'mine' in request.POST:
                for applicant in applicants['records']:
                    if applicant['Scholarship_Assignments__r']:
                        for assignment in applicant['Scholarship_Assignments__r']['records']:
                            if assignment['Scholarship_Reviewer__r']['Contact__c'] == request.user.id:
                                new_q['records'].append(applicant)
                            continue

            applicants = new_q

        return render(
            request,
            f'app/{page}',
            {
                'title': 'Scholarship Applications',
                'year': datetime.now().year,
                'stage': 2,
                'applicants': applicants,
                'reviewer': request.user.id,
            }
        )

    return render(
        request,
        f'app/{page}',
        {
            'title': 'Scholarship Applications',
            'year': datetime.now().year,
            'stage': 1,
            'reviewer': request.user.id,
        }
    )


def interview_schedule(request):
    """For people to sign up to interview"""

    assert isinstance(request, HttpRequest)
    if request.user.is_authenticated:
        if request.user.type_of_user == 'prospective':
            return HttpResponseRedirect('/')

    sf = Salesforcer()

    # Submitted a form to sign up
    if request.method == 'POST':
        ID = list(request.POST.keys())[-1]
        campaign_id = sf.query(f"SELECT Campaign__c FROM Volunteer_Job__c \
            WHERE Id='{ID}'")['records'][0]['Campaign__c']
        start_date = sf.query(f"SELECT StartDate FROM Campaign WHERE \
            Id='{campaign_id}'")['records'][0]['StartDate']

        # The form was filled out and person submitted to confirm.
        if "Name" in list(request.POST.keys()):
            form = UnauthSignup(data=request.POST)
            if form.is_valid():
                data = form.cleaned_data
                form.save(ID, commit=True)

                send_mail('Dream Project Interviews',
                          emails.unauth_signup(data['Name'], start_date),
                          emails.email_sender,
                          [data['Email']],
                          html_message=emails.unauth_signup(data['Name'], start_date))
                send_mail('Reviewer signed up',
                          f"{data['Name']} signed up for interviewing on {start_date}",
                          emails.email_sender,
                          ["carlos@dreamproject-va.org"],
                          )

                messages.info(
                    request, "Successfully signed up. Please check your email for confirmation.")
                return HttpResponseRedirect('/')
        else:
            form = UnauthSignup()
        return render(
            request,
            'app/unauth-signup.html',
            {
                'title': f'Sign up to Interview on {start_date}',
                'desc': '',
                'year': datetime.now().year,
                'form': form,
                'id': ID
            }
        )

    # Displays nights available so people can sign up

    # Gathers nights available
    list_of_nights = {}
    interview_nights = sf.query(
        "SELECT Id, Name, StartDate FROM Campaign WHERE Status='Planned' \
            AND Type='Other' AND Volunteers_Needed__c > 0")['records']
    for interview_night in interview_nights:

        # If today is before the date of the night, set the start date to
        # a string that can be rendered, otherwise, skip this night
        if interview_night['StartDate']:
            if datetime.now() <= datetime.strptime(interview_night['StartDate'], '%Y-%m-%d'):
                interview_night['StartDate'] = interview_night['StartDate'][5:]
            else:
                continue

        # Get list of volunteers for current night
        volunteers = sf.query(
            f"SELECT Id, Name, Campaign__c, Info__c FROM Volunteer_Job__c \
                WHERE Campaign__c='{interview_night['Id']}' AND Contact__c=''")['records']
        name = f"{interview_night['Name']} | {interview_night['StartDate']}"
        list_of_nights[name] = volunteers
    return render(
        request,
        'app/portal-interview-signup.html',
        {
            'title': 'Sign up to Interview',
            'year': datetime.now().year,
            'events': list_of_nights,
            'len': len(list_of_nights),
        }
    )


def interview_schedule_students(request):
    """For students to sign up for interview slots"""
    assert isinstance(request, HttpRequest)

    sf = Salesforcer()
    list_of_nights = {}

    # Gets all interview nights that are not full
    interview_nights = sf.query(
        "SELECT Id, Name, StartDate FROM Campaign WHERE Status='Planned' AND Type='Other' AND NumberOfContacts < 10")['records']

    # If student selected a night
    if request.method == 'POST':
        for interview_night in interview_nights:
            if interview_night['StartDate']:
                if datetime.now() > datetime.strptime(interview_night['StartDate'], '%Y-%m-%d'):
                    continue

            signed_up = sf.query(
                f"SELECT Id FROM CampaignMember WHERE CampaignId='{interview_night['Id']}' AND ContactId='{request.user.id}'")['totalSize']
            if signed_up:
                break

        if not signed_up:
            for key in request.POST.keys():
                if request.POST[key] == 'Sign Up':
                    vals = key.split('|')
            ID, time = vals[0], vals[1]
            campaign_start_date = sf.query(f"SELECT StartDate FROM Campaign WHERE Id='{ID}'")[
                'records'][0]['StartDate']
            days = {0: "M",
                    1: "T",
                    2: "W",
                    3: "R"}
            day = days[datetime.strptime(
                campaign_start_date, '%Y-%m-%d').weekday()]
            code = f"{day}P1|{time}"

            # Checks to see if time slot already assigned, if so assign it to the second panel
            sign_ups = sf.query(
                f"SELECT Id FROM Scholarship_Assignment__c WHERE Interview_Code__c='{code}' AND Scholarship_Application__r.Scholarship_Review_Year__c='{sv.updated_vars['scholarship_review_year']}'")['totalSize']
            if sign_ups:
                code = f"{day}P2|{time}"

            application_id = sf.query(
                f"SELECT Id FROM Scholarship_Application__c WHERE Contact__c='{request.user.id}' AND Scholarship_Review_Year__c='{sv.updated_vars['scholarship_review_year']}'")['records'][0]['Id']

            sf.CampaignMember.create({
                'CampaignId': ID,
                'ContactId': request.user.id,
                'Status': 'Responded',
                'Info__c': time,
                'Will_Attend__c': True
            })
            sf.Scholarship_Assignment__c.create({
                                                "Scholarship_Reviewer__c": "a1S1R00000JMoDTUA1",
                                                "Scholarship_Application__c": application_id,
                                                "Phase__c": "Interview",
                                                "Interview_Code__c": code
                                                })

            send_mail('Dream Project Interviews',
                      emails.interview_signup(
                          request.user.name, f"{campaign_start_date} at {time}"),
                      emails.email_sender,
                      [request.user.email],
                      html_message=emails.interview_signup(request.user.name, f"{campaign_start_date} at {time}"))
            send_mail('Student signed up',
                      f"{request.user.name} signed up",
                      emails.email_sender,
                      ["carlos@dreamproject-va.org"],
                      )
            messages.info(
                request, f'Thank you for signing up! A confirmation email has been sent to {request.user.email}')
            return HttpResponseRedirect('/')
        else:
            messages.error(
                request, f'It looks like you already signed up for another night. If you need to change your date and time please email me at carlos@dreamproject-va.org')
            return HttpResponseRedirect('/')

    # Student has not selected a night
    for interview_night in interview_nights:

        # If date it hasn't passed make it readable otherwise skip the night.
        if interview_night['StartDate']:
            if datetime.now() <= datetime.strptime(interview_night['StartDate'], '%Y-%m-%d'):
                days = {0: "MP",
                        1: "TP",
                        2: "WP",
                        3: "RP"}
                code = days[datetime.strptime(
                    interview_night['StartDate'], '%Y-%m-%d').weekday()]
                interview_night['StartDate'] = interview_night['StartDate'][5:]
            else:
                continue

        # Get list of students being interviewed this night
        interview_assignments = sf.query(
            f"SELECT Interview_Code__c FROM Scholarship_Assignment__c WHERE Interview_Code__c LIKE '%{code}%' AND Phase__c='Interview' AND Scholarship_Application__r.Scholarship_Review_Year__c='{sv.updated_vars['scholarship_review_year']}'")['records']

        # Interview times available by default
        times = ["6:00", "6:30", "7:00", "7:30", "8:00",
                 "6:00", "6:30", "7:00", "7:30", "8:00"]
        for assignment in interview_assignments:
            times.remove(assignment['Interview_Code__c'].split("|")[1])
        name = f"{interview_night['Name']} | {interview_night['StartDate']}"
        list_of_nights[name] = [
            times,
            interview_night['Id']
        ]
    return render(
        request,
        'app/portal-interview-signup.html',
        {
            'title': 'Sign up to Interview',
            'year': datetime.now().year,
            'events': list_of_nights,
            'len': len(list_of_nights),
            'student': True,
        }
    )


def interview_pwd(request):
    """Passwords used by interviewers to access their night's application materials"""
    assert isinstance(request, HttpRequest)
    if request.method == 'POST':
        passwords = {
            'FNP3': 'MP1', 'FNP4': 'MP2',
            'YNP3': 'TP1', 'YNP4': 'TP2',
            'ENP3': 'WP1', 'ENP4': 'WP2',
            'TNP3': 'RP1', 'TNP4': 'RP2',
        }
        reviewer = passwords[request.POST['password']]
        request.session['reviewer'] = reviewer
        return redirect('interview')
    return render(
        request,
        'app/password.html',
        {
            'title': f"Interviews",
            'year': datetime.now().year,
        }
    )


def interview_portal(request):
    """Portal used the night of interviews to view applications"""
    assert isinstance(request, HttpRequest)
    try:
        reviewer = request.session['reviewer']
        panel = request.session['reviewer']
    except:
        return HttpResponseRedirect('password')

    sf = Salesforcer()
    if request.method == "POST":
        id = list(request.POST)[1]  # ID of applicant
        print("posting")
        if request.POST[id] == 'View':
            # Download applicants application and attachments
            applicant, attachments, comments = get_application(sf, id)

            # Checks for panel lead
            panel = None
            for comment in comments:
                if comment['Interview_Code__c']:
                    panel = comment['Interview_Code__c'].split("|")[0]
            panel_lead = False
            if panel:
                if request.user.id == sv.panelchairs[panel]:
                    panel_lead = True

            # Creates the form depending on whether it's a reviewer or an observer
            form = SubmitAppReview(comments, request.user, interview=True, )

            # Replaces Salesforce breaks to HTML breaks
            for key in applicant:
                applicant[key] = str(applicant[key]).replace('\r\n', '<br>')

            return render(
                request,
                f'app/portal-interviewer.html',
                {
                    'title': f"Reviewing: {applicant['Last_Name__c']}, {applicant['First_Name__c']}",
                    'year': datetime.now().year,
                    'stage': 3,
                    'applicant': applicant,
                    'attachments': attachments,
                    'comments': comments,
                    'show': True,
                    'reviewer': panel_lead,
                    'form': form
                }
            )

        # User is attempting to submit or save form
        elif 'save' in request.POST or 'save2' in request.POST:
            applicant, attachments, comments = get_application(sf, id)

            # Checks for panel lead
            panel = None
            for comment in comments:
                if comment['Interview_Code__c']:
                    panel = comment['Interview_Code__c'].split("|")[0]
            panel_lead = False
            if panel:
                if request.user.id == sv.panelchairs[panel]:
                    panel_lead = True

            form = SubmitAppReview(
                comments, request.user, interview=True, data=request.POST)

            if form.is_valid():

                # Save the form, don't submit it
                form.save(final=False if 'save2' in request.POST else True)
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/scholarship/interview/'))

            else:
                # Form is not valid
                return render(
                    request,
                    'app/portal-interviewer.html',
                    {
                        'title': f"Reviewing: {applicant['Last_Name__c']}, {applicant['First_Name__c']}",
                        'year': datetime.now().year,
                        'stage': 3,
                        'applicant': applicant,
                        'attachments': attachments,
                        'reviewer': panel_lead,
                        'show': True,
                        'form': form
                    }
                )

    applicants = sf.query(f"SELECT Scholarship_Application__c.Id, Scholarship_Application__c.Type__c,\
                        Scholarship_Application__c.Contact__r.FirstName, Scholarship_Application__c.Contact__r.LastName,\
                        (SELECT Decision__c, Interview_Code__c, Complete__c, Scholarship_Reviewer__r.Contact__c, Scholarship_Reviewer__r.Contact__r.FirstName FROM Scholarship_Application__c.Scholarship_Assignments__r) \
                        FROM Scholarship_Application__c WHERE Completed__c=\
                        TRUE AND Ineligible__c=FALSE AND Scholarship_Review_Year__c='{sv.updated_vars['scholarship_review_year']}' \
                        ORDER BY Scholarship_Application__c.Contact__r.LastName ASC")
    new_q = {'records': []}
    for applicant in applicants['records']:
        for assignment in applicant['Scholarship_Assignments__r']['records']:
            if assignment['Interview_Code__c']:
                if panel in assignment['Interview_Code__c']:
                    new_q['records'].append(applicant)
    applicants = new_q
    return render(
        request,
        'app/portal-interviewer.html',
        {
            'title': 'Scholarship Applications',
            'year': datetime.now().year,
            'stage': 2,
            'applicants': applicants,
            'reviewer': reviewer,
        }
    )


def error(request):
    """Renders page when there is an error"""
    return render(
        request,
        'app/error.html',
        {
            'title': 'Oh no!',
            'year': datetime.now().year,
        }
    )


def assign_reviewers(application_id, scholarship_type):
    """Assigns reviewers for current scholarship selection year from list of available Reviewers"""
    sf = Salesforcer()
    current_year = f"{str(sv.updated_vars['summer_fall_s'])[2:]}-{str(sv.updated_vars['spring_s'])[2:]}"
    year_info = sf.query(
        f"SELECT Id, Phase__c FROM Scholarship_Process__c WHERE Name='{current_year}'")['records'][0]
    if scholarship_type == "Renewal":
        renewal = True
    else:
        renewal = False

    if not renewal:
        reviewers = sf.query(
            f"SELECT Id, Assigned_Applications__c, Work_Multiplier__c, Contact__c FROM Scholarship_Reviewer__c WHERE Scholarship_Review_Year__c='{year_info['Id']}'")

        # Cleaned reviewers is a list of reviewers with their respective workloads taking into account work multiplier
        cleaned_reviewers = {}
        # Iterate through the list of reviewers and add to cleaned_reviewrs dict with "real" assigned applications
        # Figure out what the least number of applications is over all reviewers
        min_assignments = 100
        for reviewer in reviewers['records']:
            multiplier = 1 if reviewer["Work_Multiplier__c"] == None else float(
                reviewer["Work_Multiplier__c"])

            if multiplier:
                apps = reviewer["Assigned_Applications__c"]/multiplier
            elif multiplier == 0:
                apps = 100000
            else:
                apps = reviewer["Assigned_Applications__c"]

            if apps < min_assignments:
                min_assignments = apps

            cleaned_reviewers[reviewer["Id"]] = {
                "Assigned_Applications__c": round(apps),
                "Contact__c": reviewer["Contact__c"],
            }

        # List of reviewers with the least amount of applications
        available_reviewers = {k: v for k, v in cleaned_reviewers.items(
        ) if v['Assigned_Applications__c'] == min_assignments}

        # If there are more than 2 reviewers with the least number of assignments, randomly choose two
        Reviewer1, Reviewer2 = None, None
        if len(available_reviewers) >= 2:
            Reviewer1 = random.choice(list(available_reviewers.keys()))
            Reviewer2 = random.choice(list(available_reviewers.keys()))
            while Reviewer1 == Reviewer2:
                Reviewer2 = random.choice(list(available_reviewers.keys()))

        # If there is only 1 assign that one, increase the min number of applications by one and assign from the new list of available reviwers
        else:
            Reviewer1 = list(available_reviewers.keys())[0]
            while not Reviewer2:
                min_assignments += 1
                available_reviewers = {k: v for k, v in cleaned_reviewers.items(
                ) if v['Assigned_Applications__c'] == min_assignments}
                if len(available_reviewers) > 0:
                    Reviewer2 = random.choice(list(available_reviewers.keys()))

        curr_phase = year_info['Phase__c']
        if "1" in curr_phase or "0" in curr_phase:
            phase = "First Read"
        elif "2" in curr_phase:
            phase = "Interview"
        elif "3" in curr_phase:
            phase = "Second Read"
        else:
            phase = "Unknown"
    else:
        reviewers = sf.query(
            f"SELECT Id FROM Scholarship_Reviewer__c WHERE Scholarship_Review_Year__c='{year_info['Id']}' AND Renewal_Reviewer__c=TRUE")['records']
        phase = "Renewal Review"
        Reviewer1, Reviewer2 = reviewers[0]['Id'], reviewers[1]['Id']

    for reviewer in [Reviewer1, Reviewer2]:
        sf.Scholarship_Assignment__c.create({
                                            "Scholarship_Reviewer__c": reviewer,
                                            "Scholarship_Application__c": application_id,
                                            "Phase__c": phase,
                                            })


def validate_scholarship(scholarship, type):
    """Makes sure that an application has the required materials before it is allowed to submit"""
    if "New" in type:
        reqs = ["High_School_Name__c", "High_School_City__c", "HS_GPA__c", "List_of_Honors__c", "English_Proficiency__c", "Financial_Thoughts__c", "Employment__c",
                "Other_Responsibilities__c", "Favorite_Animal__c", "Name_Recommender_1__c", "Email_Recommender_1__c", "Name_Recommender_2__c", "Email_Recommender_2__c"]
        if type == "New (HS)":
            reqs += ["Colleges_Applied_to__c"]
        elif type == "New (College)":
            reqs += ["Current_College__c", "Current_Major__c",
                     "Current_Number_of_Credits__c", "College_GPA__c"]

    elif type == "Renewal":
        reqs = ["Commitment_to_Dream_Project__c", "Expected_Graduation__c", "Mandatory_Events__c",
                "College_GPA__c", "Fall_History_of_Enrollment__c", "Spring_History_of_Enrollment__c", ]

    else:
        return False

    missing_reqs = []
    for req in reqs:
        if scholarship.get(req) in ["None", None, 0, 0.0, "", " "]:
            missing_reqs.append(req)

    if len(missing_reqs) > 0:
        return False

    return True


def get_application(sf, id):
    """Gets scholarship application for user"""
    try:
        app_info = sf.Scholarship_Application__c.get(id)
    except:
        info = sf.query(
            f"SELECT Scholarship_Application__c FROM Scholarship_Assignment__c WHERE Id='{id}'")
        id = info['records'][0]['Scholarship_Application__c']
        app_info = sf.Scholarship_Application__c.get(id)
    try:
        app_info['Favorite_Animal__c'] = sv.encrypt(
            app_info['Favorite_Animal__c'], mode="d")
    except:
        pass

    attachments = get_attachments(sf, id)

    reviews = sf.query(
        f"SELECT Id, Decision__c, Comments__c, Interview_Code__c, Complete__c, Scholarship_Reviewer__r.Contact__c, Scholarship_Reviewer__r.Contact__r.FirstName FROM Scholarship_Assignment__c WHERE Scholarship_Application__c='{id}'")
    comments = []
    for review in reviews['records']:
        temp = {
            "Id": review['Id'],
            "Decision__c": review['Decision__c'],
            "Comments__c": review['Comments__c'],
            "Complete__c": review['Complete__c'],
            "Contact__c": review['Scholarship_Reviewer__r']['Contact__c'],
            "Interview_Code__c": review['Interview_Code__c'],
            "FirstName": None,
        }
        if review['Scholarship_Reviewer__r']['Contact__r']:
            temp['FirstName'] = review['Scholarship_Reviewer__r']['Contact__r']['FirstName']
        comments.append(temp)

    return app_info, attachments, comments


def get_attachments(sf, id, type=['.jpg', '.png', '.jpeg', '.pdf']):
    """Gets attachments from object (specified by ID)"""
    attachments = {'pdfs': [], 'images': []}
    list_of_docs = sf.query(
        f"SELECT Id, Name FROM Attachment WHERE ParentId='{id}'")['records']
    extra_attachments = sf.query(
        f"SELECT ContentDocumentId FROM ContentDocumentLink WHERE LinkedEntityId='{id}'")['records']
    for doc in extra_attachments:
        full_doc = sf.ContentDocument.get(doc['ContentDocumentId'])
        data = sf.query(f"SELECT VersionData FROM ContentVersion WHERE ContentDocumentId='{doc['ContentDocumentId']}' AND IsLatest=true")[
            'records'][0]
        list_of_docs.append({
            "Id": full_doc['Id'],
            "Name": full_doc['Title'],
            "ext": f".{full_doc['FileExtension']}",
            "data": data
        })

    for doc in list_of_docs:
        # Clean Document's Name
        invalid_chars = list(" '~`!@#$%^&*()_-+=[]{}|:;,<>/?")
        for invalid_char in invalid_chars:
            doc['Name'] = doc['Name'].replace(invalid_char, "")

        data = doc.get("data")
        if data:
            ext = doc['ext']
            request = f"https://{sf.sf_instance}{data['VersionData']}"
        else:
            ext = os.path.splitext(doc['Name'])[-1].lower()
            request = f"https://{sf.sf_instance}/services/data/v39.0/sobjects/Attachment/{doc['Id']}/body"

        if ext in type:
            response = requests.get(
                request,
                headers={'Content-Type': 'application/text', 'Authorization': 'Bearer ' + sf.session_id})

            file = {
                'name': doc['Name'],
                'varname': doc['Name'].replace(" ", "")[:-4],
                'type': ext,
                'file':  str(base64.b64encode(response.content), 'utf-8'),
                'Id': doc['Id']
            }

            key = 'images' if ext in ['.jpg', '.jpeg', '.png'] else 'pdfs'

            if file not in attachments[key]:
                attachments[key].append(file)

    return attachments


def object_exists(sf, object, id_location, id, *args):
    """Checks if an object exists"""
    query = f"SELECT Id FROM {object} WHERE {id_location}='{id}'"
    for dic in args:
        query += f" AND {dic['name']}='{dic['value']}'"
    check = sf.query(query)
    return bool(check['totalSize'])


def app_type_convert(app_type):
    """Converts SF type apps to code values"""
    if app_type == "New (HS)":
        converted_type = "hs_app"
    elif app_type == "New (College)":
        converted_type = "college_app"
    elif app_type == "Renewal":
        converted_type = "renewal_app"
    elif app_type == "hs_app":
        converted_type = "New (HS)"
    elif app_type == "college_app":
        converted_type = "New (College)"
    elif app_type == "renewal_app":
        converted_type = "Renewal"

    return converted_type
