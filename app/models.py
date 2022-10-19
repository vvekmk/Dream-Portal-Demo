"""
Definition of models.
"""

import datetime

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, User
from django.db import models

import app.survey_vars as sv


class UserManager(BaseUserManager):
    def create_user(self, **data):
        if not (data['Email'] or data.get('password')):
            raise ValueError('No Email/Password')
        user = self.model(
            type_of_user=data.get('kind', 'g'),
            # Universal
            email=self.normalize_email(data['Email']),
            name=data['FirstName'],
            last=data['LastName'],
            phone=data['Phone'],
            gender=data['Gender__c'],
            ethnicity=data['Ethnicity__c'],
            country=data['Country_of_Origin__c'],
            birthday=data['Birthdate'],
            id=data['Id'],
            street=data['MailingStreet'],
            city=data['MailingCity'],
            state=data['MailingState'],
            zip=data['MailingPostalCode'],
            usrnm=data['Dream_Portal__c'],

            # Scholar
            college=data['Primary_College_Affiliation_Text__c'] if data.get(
                'is_scholar') else None,
            student_id=data['Student_ID__c'] if data.get(
                'is_scholar') else None,
            college_email=data['npe01__AlternateEmail__c'] if data.get(
                'is_scholar') else None,
            major=data['Major_s__c'] if data.get('is_scholar') else None,
            minor=data['Minor_s__c'] if data.get('is_scholar') else None,
            gpa=data['GPA__c'] if data.get('is_scholar') else None,

            # Mentee
            areas_of_interest=data['Areas_of_Interest__c'] if data.get(
                'is_mentee') else None,
            year_of_study=data['Description'] if data.get(
                'is_mentee') else None,
            colleges_applied=data['Colleges_Applied_to__c'] if data.get(
                'is_mentee') else None,
            scholarships_applied=data['Scholarships_Applied_to__c'] if data.get(
                'is_mentee') else None,

            #Mentee & Scholars
            employed=data['Employment_Status__c'] if data.get(
                'is_scholar') or data.get('is_mentee') else None,

            # NS Donor
            scholarships=data['scholarships'] if data.get(
                'is_donor') else None,
        )

        user.set_password(data['password'])
        user.save(using=self._db)
        return user


class temp_user(AbstractBaseUser):
    """Creates temporary user that is NOT synced with DB
    This is to limit calls to the DB. User is stored locally and deleted on logout"""

    USERNAME_FIELD = 'id'
    id = models.CharField(unique=True, primary_key=True,
                          max_length=255, blank=True)

    objects = UserManager()

    email = models.EmailField(max_length=255, default='abc@noemail.com')
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    type_of_user = models.CharField(max_length=255, default='')

    # GENERAL
    name = models.CharField(max_length=255, blank=True, null=True)
    last = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=255, blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)  # YYYY-MM-DD

    usrnm = models.CharField(max_length=255, blank=True, null=True)

    # MAIL INFO
    street = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    zip = models.CharField(max_length=255, blank=True, null=True)

    # SCHOLAR FIELDS
    ethnicity = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    employed = models.CharField(max_length=255, blank=True, null=True)

    college = models.CharField(max_length=255, blank=True, null=True)
    student_id = models.CharField(max_length=255, blank=True, null=True)
    college_email = models.EmailField(max_length=255, blank=True, null=True)
    major = models.CharField(max_length=255, blank=True, null=True)
    minor = models.CharField(max_length=255, blank=True, null=True)
    gpa = models.CharField(max_length=255, blank=True, null=True)

    # DONOR FIELDS
    scholarships = models.CharField(max_length=5000, blank=True, null=True)

    # MENTEE FIELDS
    areas_of_interest = models.CharField(
        max_length=1000, blank=True, null=True)
    year_of_study = models.CharField(max_length=100, blank=True, null=True)
    colleges_applied = models.CharField(max_length=1000, blank=True, null=True)
    scholarships_applied = models.CharField(
        max_length=1000, blank=True, null=True)

    def get_info(self):
        scholarship_fields = {
            "Email": self.email,
            "First Name": self.name,
            "Last Name": self.last,
            "Phone": self.phone,
            "Birth Date": self.birthday,
            "Street": self.street,
            "City": self.city,
            "State": self.state,
            "Zip": self.zip,
            "Ethnicity": self.ethnicity,
            "Country of Birth": self.country,
            "Employment Status": self.employed
        }
        return scholarship_fields

    def get_scholarship(self, sf, application_type):
        scholarship_application = {}
        current_application = sf.query(
            f"SELECT Id FROM Scholarship_Application__c WHERE Contact__c='{self.id}' AND Scholarship_Review_Year__c='{sv.updated_vars['scholarship_review_year']}'")

        if current_application['totalSize'] > 0:
            application_details = sf.Scholarship_Application__c.get(
                current_application['records'][0]["Id"])

            # Sets all fields in SF to fields in Dream Portal
            for key in application_details:
                scholarship_application[key] = sv.encrypt(
                    application_details[key], mode="d")

            History_of_Enrollment__c = scholarship_application['History_of_Enrollment__c']
            if History_of_Enrollment__c:
                scholarship_application['Fall_History_of_Enrollment__c'] = History_of_Enrollment__c.split(" | ")[
                    0].split(": ")[1]
                try:
                    scholarship_application['Spring_History_of_Enrollment__c'] = History_of_Enrollment__c.split(" | ")[
                        1].split(": ")[1]
                except:
                    pass

            for i in [1, 2]:
                Recommender = scholarship_application[f'Recommender_{i}__c']
                if Recommender:
                    scholarship_application[f'Name_Recommender_{i}__c'] = Recommender.split(" | ")[
                        0].split(": ")[1]
                    scholarship_application[f'Title_Recommender_{i}__c'] = Recommender.split(" | ")[
                        1].split(": ")[1]
                    scholarship_application[f'Email_Recommender_{i}__c'] = Recommender.split(" | ")[
                        2].split(": ")[1]
                    try:
                        scholarship_application[f'Phone_Recommender_{i}__c'] = Recommender.split(" | ")[
                            3].split(": ")[1]
                    except:
                        pass

            Test_Scores__c = scholarship_application['Test_Scores__c']
            if Test_Scores__c:
                scholarship_application['SAT_Test_Scores__c'] = Test_Scores__c.split(" | ")[
                    0].split(": ")[1]
                try:
                    scholarship_application['ACT_Test_Scores__c'] = Test_Scores__c.split(" | ")[
                        1].split(": ")[1]
                except:
                    pass

            Expected_Graduation__c = scholarship_application['Expected_Graduation__c']
            if Expected_Graduation__c:
                scholarship_application['Expected_Graduation__c'] = datetime.datetime.strptime(
                    Expected_Graduation__c, "%Y-%m")
            elif application_type == "Renewal":
                scholarship_application['Expected_Graduation__c'] = datetime.datetime.today(
                )

            for k, v in scholarship_application.items():
                if isinstance(v, str):
                    if "\r\n" in v:
                        scholarship_application[k] = v.split("\r\n")
                if isinstance(v, bool):
                    if v:
                        scholarship_application[k] = "Yes"
                    else:
                        scholarship_application[k] = "No"

            return scholarship_application

        else:
            data = {"Contact__c": self.id, "Type__c": application_type,
                    "Scholarship_Review_Year__c": sv.updated_vars['scholarship_review_year']}
            if application_type == "Renewal":
                data['Expected_Graduation__c'] = datetime.datetime.today().strftime(
                    '%Y-%m')

            sf.Scholarship_Application__c.create(data)
            return {}

    def get_scholarship_info(self, sf):
        current_application = sf.query(
            f"SELECT Id, Type__c, Completed__c FROM Scholarship_Application__c WHERE Contact__c='{self.id}' AND Scholarship_Review_Year__c='{sv.updated_vars['scholarship_review_year']}'")
        if current_application['totalSize'] > 0:
            return current_application['records'][0]['Id'], current_application['records'][0]['Type__c'], current_application['records'][0]['Completed__c']
        else:
            return None, None, None

    def get_scholarship_attachments(self, sf):
        current_application = sf.query(
            f"SELECT Id, Type__c FROM Scholarship_Application__c WHERE Contact__c='{self.id}' AND Scholarship_Review_Year__c='{sv.updated_vars['scholarship_review_year']}'")
        if current_application['totalSize'] == 0:
            return None
        app_id, app_type = current_application['records'][0]['Id'], current_application['records'][0]['Type__c']
        attachments = sf.query(
            f"SELECT Id, Name FROM Attachment WHERE ParentId='{app_id}'")

        if app_type == "Renewal":
            reqs = {"C_Transcript": {"Uploaded": False, "Id": None, "R": True}}
        elif app_type == "New (HS)":
            reqs = {"Essay": {"Uploaded": False, "Id": None, "R": True},
                    "HS_Transcript": {"Uploaded": False, "Id": None, "R": True},
                    "SAT_Score": {"Uploaded": False, "Id": None, "R": False},
                    "ACT_Score": {"Uploaded": False, "Id": None, "R": False},
                    }
        elif app_type == "New (College)":
            reqs = {"Essay": {"Uploaded": False, "Id": None, "R": True},
                    "HS_Transcript": {"Uploaded": False, "Id": None, "R": True},
                    "C_Transcript": {"Uploaded": False, "Id": None, "R": True},
                    "SAT_Score": {"Uploaded": False, "Id": None, "R": False},
                    "ACT_Score": {"Uploaded": False, "Id": None, "R": False},
                    }

        for attachment in attachments['records']:
            reqs[attachment['Name']] = {
                "Uploaded": True, "Id": attachment['Id']}

        return reqs
