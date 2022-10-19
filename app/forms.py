"""
Definition of forms.
"""

import base64
import datetime
from random import shuffle as shf

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail
from django.core.validators import FileExtensionValidator
from django.utils import timezone

import app.survey_vars
import app.surveys as sv
from app.customauth import Salesforcer, encrypt
from app.emails import forgot_info
from app.models import temp_user
from app.survey_classes import Divider, Question


class LikertField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        self.scale = kwargs['scale']
        del kwargs['scale']
        super(LikertField, self).__init__(*args, **kwargs)


class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(label="Dream ID",
                               max_length=254,
                               widget=forms.TextInput({
                                   'placeholder': 'Dream ID / Username'}))
    password = forms.CharField(label="Last Name",
                               widget=forms.PasswordInput({
                                   'placeholder': 'Last Name / Password'}))


class UpdateProfileScholar(forms.ModelForm):
    gender = forms.ChoiceField(required=False, choices=[(
        'Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    ethnicity = forms.ChoiceField(required=False, choices=[('', ''),
                                                           ('White', 'White'),
                                                           ('Black or African American',
                                                            'Black or African American'),
                                                           ('Hispanic or Latino',
                                                            'Hispanic or Latino'),
                                                           ('Native American',
                                                            'Native American'),
                                                           ('Asian or Pacific Islander',
                                                            'Asian or Pacific Islander'),
                                                           ('Prefer not to answer', 'Prefer not to answer')])
    employed = forms.ChoiceField(required=False, choices=[('', ''),
                                                          ('Employed Full-time (40+hrs/week)',
                                                           'Employed Full-time (40+hrs/week)'),
                                                          ('Employed Part-time (Fewer than 40hrs/week)',
                                                           'Employed Part-time (Fewer than 40hrs/week)'),
                                                          ('Looking for Work',
                                                           'Looking for Work'),
                                                          ('Student', 'Student'), ])
    birthday = forms.DateField(
        required=False, widget=forms.SelectDateWidget(years=range(1940, 2019)))
    phone = forms.CharField(required=False, min_length=10, max_length=14)

    chunks = {
        'General': {
            'name': 'First Name',
            'last': 'Last Name',
            'phone': 'Phone',
            'email': 'Email',
            'gender': 'Gender',
            'birthday': 'Birthday'
        },
        'Mailing Address': {
            'street': 'Street',
            'city': 'City',
            'state': 'State',
            'zip': 'Zip Code'
        },
        'Other': {
            'country': 'Country',
            'ethnicity': 'Ethnicity',
            'employed': 'Employment'
        },
        'College': {
            'college': 'College',
            'student_id': 'Student ID',
            'college_email': 'College Email',
            'major': 'Major(s)',
            'minor': 'Minor(s)',
            'gpa': 'GPA'
        }
    }

    class Meta:
        model = temp_user
        fields = ('name', 'last', 'phone', 'email', 'gender', 'birthday',
                  'street', 'city', 'state', 'zip',
                  'country', 'ethnicity', 'employed',
                  'college', 'student_id', 'college_email', 'major', 'minor', 'gpa')

    def save(self, pk, scholarships, commit=True):
        user = super(UpdateProfileScholar, self).save(commit=False)
        user.email = self['email'].value()
        user.name = self['name'].value()
        user.last = self['last'].value()
        user.phone = self['phone'].value()
        user.gender = self['gender'].value()
        user.ethnicity = self['ethnicity'].value()
        user.country = self['country'].value()
        user.birthday = self['birthday'].value()
        user.employed = self['employed'].value()

        user.street = self['street'].value()
        user.city = self['city'].value()
        user.state = self['state'].value()
        user.zip = self['zip'].value()

        user.college = self['college'].value()
        user.student_id = self['student_id'].value()
        user.college_email = self['college_email'].value()
        user.major = self['major'].value()
        user.minor = self['minor'].value()
        user.gpa = self['gpa'].value()

        update_dic = {
            'Email': user.email,
            'FirstName': user.name,
            'LastName': user.last,
            'Phone': user.phone,
            'Gender__c': user.gender,
            'Birthdate': user.birthday,

            'Ethnicity__c': user.ethnicity,
            'Country_of_Origin__c': user.country,

            'MailingStreet': user.street,
            'MailingCity': user.city,
            'MailingState': user.state,
            'MailingPostalCode': user.zip,

            'Primary_College_Affiliation_Text__c': user.college,
            'Student_ID__c': user.student_id,
            'npe01__AlternateEmail__c': user.college_email,
            'Major_s__c': user.major,
            'Minor_s__c': user.minor,
            'GPA__c': user.gpa,
            'Employment_Status__c': user.employed,
        }

        if commit:
            sf = Salesforcer()
            sf.Contact.update(pk, update_dic)
            user.save()
            print(f'Successfully Updated: {user.name}, {user.last}')
        return user


class UpdateProfileMentee(forms.ModelForm):
    gender = forms.ChoiceField(required=False, choices=[(
        'Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    ethnicity = forms.ChoiceField(required=False, choices=[('', ''),
                                                           ('White', 'White'),
                                                           ('Black or African American',
                                                            'Black or African American'),
                                                           ('Hispanic or Latino',
                                                            'Hispanic or Latino'),
                                                           ('Native American',
                                                            'Native American'),
                                                           ('Asian or Pacific Islander',
                                                            'Asian or Pacific Islander'),
                                                           ('Prefer not to answer', 'Prefer not to answer')])
    employed = forms.ChoiceField(required=False, choices=[('', ''),
                                                          ('Employed Full-time (40+hrs/week)',
                                                           'Employed Full-time (40+hrs/week)'),
                                                          ('Employed Part-time (Fewer than 40hrs/week)',
                                                           'Employed Part-time (Fewer than 40hrs/week)'),
                                                          ('Looking for Work',
                                                           'Looking for Work'),
                                                          ('Student', 'Student'), ])
    year_of_study = forms.ChoiceField(choices=[
        ('Freshman', 'Freshman'),
        ('Sophomore', 'Sophomore'),
        ('Junior', 'Junior'),
        ('Senior', 'Senior'), ])
    birthday = forms.DateField(
        required=False, widget=forms.SelectDateWidget(years=range(1940, 2019)))
    phone = forms.CharField(required=False, min_length=10, max_length=14)
    areas_of_interest = forms.CharField(
        required=False, widget=forms.Textarea(attrs={'rows': 5, 'cols': 20}))
    colleges_applied = forms.CharField(
        required=False, widget=forms.Textarea(attrs={'rows': 5, 'cols': 20}))
    scholarships_applied = forms.CharField(
        required=False, widget=forms.Textarea(attrs={'rows': 5, 'cols': 20}))

    chunks = {'General': {'name': 'First Name',
                          'last': 'Last Name',
                          'phone': 'Phone',
                          'email': 'Email',
                          'gender': 'Gender',
                          'birthday': 'Birthday'},
              'Mailing Address': {'street': 'Street',
                                  'city': 'City',
                                  'state': 'State',
                                  'zip': 'Zip Code'},
              'Other': {'country': 'Country',
                        'ethnicity': 'Ethnicity',
                        'employed': 'Employment',
                        'areas_of_interest': 'Area(s) of Interest',
                        'year_of_study': 'Year of Study',
                        'colleges_applied': 'Colleges Applied To',
                        'scholarships_applied': 'Scholarships Applied To',
                        }}

    class Meta:
        model = temp_user
        fields = ('name', 'last', 'phone', 'email', 'gender', 'birthday',
                  'street', 'city', 'state', 'zip',
                  'country', 'ethnicity', 'employed', 'areas_of_interest',
                  'year_of_study', 'colleges_applied', 'scholarships_applied')

    def save(self, pk, scholarships, commit=True):
        user = super(UpdateProfileMentee, self).save(commit=False)
        user.email = self['email'].value()
        user.name = self['name'].value()
        user.last = self['last'].value()
        user.phone = self['phone'].value()
        user.gender = self['gender'].value()
        user.ethnicity = self['ethnicity'].value()
        user.country = self['country'].value()
        user.birthday = self['birthday'].value()
        user.employed = self['employed'].value()

        user.street = self['street'].value()
        user.city = self['city'].value()
        user.state = self['state'].value()
        user.zip = self['zip'].value()

        user.areas_of_interest = self['areas_of_interest'].value()
        user.year_of_study = self['year_of_study'].value()
        user.colleges_applied = self['colleges_applied'].value()
        user.scholarships_applied = self['scholarships_applied'].value()

        update_dic = {
            'Email': user.email,
            'FirstName': user.name,
            'LastName': user.last,
            'Phone': user.phone,
            'Gender__c': user.gender,
            'Birthdate': user.birthday,

            'Ethnicity__c': user.ethnicity,
            'Country_of_Origin__c': user.country,

            'MailingStreet': user.street,
            'MailingCity': user.city,
            'MailingState': user.state,
            'MailingPostalCode': user.zip,

            'Areas_of_Interest__c': user.areas_of_interest,
            'Description': user.year_of_study,

            'Employment_Status__c': user.employed,
            'Colleges_Applied_to__c': user.colleges_applied,
            'Scholarships_Applied_to__c': user.scholarships_applied
        }

        if commit:
            sf = Salesforcer()
            sf.Contact.update(pk, update_dic)
            user.save()
            print(f'Successfully Updated: {user.name}, {user.last}')
        return user


class UpdateProfileDonor(forms.ModelForm):
    def __init__(self, scholarships, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i in range(len(scholarships)):
            ns_name = f'ns_name{i}'
            ns_desc = f'ns_desc{i}'
            self.fields[ns_name] = forms.CharField(required=False)
            self.fields[ns_desc] = forms.CharField(
                required=False, widget=forms.Textarea)
            try:
                self.initial[ns_name] = scholarships[i]['Name']
                self.initial[ns_desc] = scholarships[i]['Scholarship_Description__c']
            except IndexError:
                self.initial[ns_name] = ''
                self.initial[ns_desc] = ''

    gender = forms.ChoiceField(required=False, choices=[(
        'Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    birthday = forms.DateField(
        required=False, widget=forms.SelectDateWidget(years=range(1940, 2019)))
    phone = forms.CharField(required=False, min_length=10, max_length=14)

    chunks = {'General': {'name': 'First Name',
                          'last': 'Last Name',
                          'phone': 'Phone',
                          'email': 'Email',
                          'gender': 'Gender',
                          'birthday': 'Birthday'},
              'Mailing Address': {'street': 'Street',
                                  'city': 'City',
                                  'state': 'State',
                                  'zip': 'Zip Code'},
              }

    class Meta:
        model = temp_user
        fields = ('name', 'last', 'phone', 'email', 'gender', 'birthday',
                  'street', 'city', 'state', 'zip')

    def save(self, pk, scholarships, commit=True):
        user = super(UpdateProfileDonor, self).save(commit=False)
        user.email = self['email'].value()
        user.name = self['name'].value()
        user.last = self['last'].value()
        user.phone = self['phone'].value()
        user.gender = self['gender'].value()
        user.birthday = self['birthday'].value()

        user.street = self['street'].value()
        user.city = self['city'].value()
        user.state = self['state'].value()
        user.zip = self['zip'].value()

        for i in range(len(scholarships)):
            num = 1
            for field in self.get_scholarship_fields():
                if str(i) in field.label and num % 2 == 0:
                    scholarships[i]['Scholarship_Description__c'] = field.value()
                    num += 1
                elif str(i) in field.label:
                    scholarships[i]['Name'] = field.value()
                    num += 1
        scholarshiplist = []
        for i in range(len(scholarships)):
            temp = list(str(scholarships[i]))
            temp[0] = '|'
            temp[-1] = '#'
            scholarshiplist.append(''.join(temp))

        user.scholarships = str(scholarshiplist)
        update_dic = {
            'Email': user.email,
            'FirstName': user.name,
            'LastName': user.last,
            'Phone': user.phone,
            'Gender__c': user.gender,
            'Birthdate': user.birthday,

            'MailingStreet': user.street,
            'MailingCity': user.city,
            'MailingState': user.state,
            'MailingPostalCode': user.zip,
        }

        if commit:
            sf = Salesforcer()
            sf.Contact.update(pk, update_dic)
            for i in range(len(scholarships)):
                ID = scholarships[i]['ID']
                scholarships[i].pop('ID')
                scholarships[i].pop('students')
                sf.Named_Scholarship__c.update(ID, scholarships[i])
            user.save()
            print(f'Successfully Updated: {user.name}, {user.last}')
        return user

    def get_scholarship_fields(self):
        for field_name in self.fields:
            if field_name.startswith('ns'):
                yield self[field_name]


class UpdateProfileGeneral(forms.ModelForm):
    gender = forms.ChoiceField(required=False, choices=[(
        'Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    birthday = forms.DateField(
        required=False, widget=forms.SelectDateWidget(years=range(1940, 2019)))
    phone = forms.CharField(required=False, min_length=10, max_length=14)

    chunks = {'General': {'name': 'First Name',
                          'last': 'Last Name',
                          'phone': 'Phone',
                          'email': 'Email',
                          'gender': 'Gender',
                          'birthday': 'Birthday'},
              'Mailing Address': {'street': 'Street',
                                  'city': 'City',
                                  'state': 'State',
                                  'zip': 'Zip Code'}}

    class Meta:
        model = temp_user
        fields = ('name', 'last', 'phone', 'email', 'gender',
                  'birthday', 'street', 'city', 'state', 'zip',)

    def save(self, pk, scholarships, commit=True):
        user = super(UpdateProfileGeneral, self).save(commit=False)
        user.email = self['email'].value()
        user.name = self['name'].value()
        user.last = self['last'].value()
        user.phone = self['phone'].value()
        user.gender = self['gender'].value()
        user.birthday = self['birthday'].value()

        user.street = self['street'].value()
        user.city = self['city'].value()
        user.state = self['state'].value()
        user.zip = self['zip'].value()

        update_dic = {
            'Email': user.email,
            'FirstName': user.name,
            'LastName': user.last,
            'Phone': user.phone,
            'Gender__c': user.gender,
            'Birthdate': user.birthday,

            'MailingStreet': user.street,
            'MailingCity': user.city,
            'MailingState': user.state,
            'MailingPostalCode': user.zip,
        }

        if commit:
            sf = Salesforcer()
            sf.Contact.update(pk, update_dic)
            user.save()
            print(f'Successfully Updated: {user.name}, {user.last}')
        return user


class Survey(forms.Form):
    def __init__(self, list_of_questions, shuffle='', *args, **kwargs):
        """Custom wrapper for quick survey developing, complex surves can be glitchy. 
        See survey_classes.py and surveys.py for a better idea of how this works """
        super().__init__(*args, **kwargs)
        for question in list_of_questions:
            if not isinstance(question, (Question, Divider)):
                continue

            if question.type == 'divider':
                self.fields[question.question] = forms.CharField(
                    widget=None,
                    required=False,
                    label=question.label,
                    label_suffix='',
                )
            elif question.type == 'choice':
                self.fields[question.question] = forms.ChoiceField(
                    required=question.required,
                    choices=question.choices,
                    help_text=question.help,
                    label_suffix='',
                    label=question.label,
                )
            elif question.type == 'likert':
                self.fields[question.question] = LikertField(
                    required=question.required,
                    choices=question.choices,
                    widget=forms.RadioSelect,
                    scale=question.scale,
                    help_text=question.help,
                    label_suffix='',
                    label=question.label,
                )
            elif question.type == 'multiplechoice':
                self.fields[question.question] = forms.MultipleChoiceField(
                    required=question.required,
                    choices=question.choices,
                    widget=forms.CheckboxSelectMultiple,
                    help_text=question.help,
                    label_suffix='',
                    label=question.label,)
            elif 'text' in question.type:
                self.fields[question.question] = forms.CharField(
                    required=question.required,
                    widget=forms.Textarea if question.type == 'textlong' else None,
                    help_text=question.help,
                    label_suffix='',
                    label=question.label,
                )
            elif question.type == 'date':
                self.fields[question.question] = forms.DateField(
                    required=question.required,
                    initial=datetime.date.today(),
                    widget=forms.SelectDateWidget(years=question.date_range),
                    help_text=question.help,
                    label_suffix='',
                    label=question.label,)
            elif question.type == 'phone':
                self.fields[question.question] = forms.CharField(
                    required=question.required,
                    min_length=10, max_length=14,
                    help_text=question.help,
                    label_suffix='',
                    label=question.label,)
            elif question.type == 'email':
                self.fields[question.question] = forms.EmailField(
                    required=question.required,
                    max_length=255,
                    help_text=question.help,
                    label_suffix='',
                    label=question.label,)
            elif question.type == 'file':
                self.fields[question.question] = forms.FileField(
                    required=question.required,
                    help_text=question.help,
                    label_suffix='',
                    label=question.label,
                    validators=[FileExtensionValidator(
                        allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])]
                )
            elif question.type == 'number':
                self.fields[question.question] = forms.DecimalField(
                    required=question.required,
                    help_text=question.help,
                    label_suffix='',
                    label=question.label,
                    max_digits=question.max_digits,
                    decimal_places=question.decimal_places,)

        if shuffle == 'likert':
            final_order = []
            dic = self.get_likert_fields(name=True)
            for group in dic:
                shf(dic[group])
                for question in dic[group]:
                    final_order.append(question)
            self.order_fields(final_order)

        elif shuffle == 'all':
            fields = list(self.get_fields(name=True))
            shf(fields)
            self.order_fields(fields)

    def get_likert_fields(self, name=False):
        likert_groups = {}
        scales = self.get_scales()
        for scale in scales:
            likert_groups[scale] = []
            for field_name in self.fields:
                if hasattr(self.fields[field_name], 'scale'):
                    if self.fields[field_name].scale == scale:
                        likert_groups[scale].append(
                            self[field_name].name if name else self[field_name])
        return likert_groups

    def get_non_likert_fields(self, name=False):
        for field_name in self.fields:
            if hasattr(self.fields[field_name], 'scale'):
                continue
            else:
                yield self[field_name].name if name else self[field_name]

    def get_fields(self, name=False):
        for field_name in self.fields:
            yield self[field_name].name if name else self[field_name]

    def get_scales(self):
        scales = []
        for field in self.fields:
            if hasattr(self.fields[field], 'scale'):
                scale = getattr(self.fields[field], 'scale')
                if scale not in scales:
                    scales.append(scale)
        return scales

    def has_likert(self):
        for field_name in self.fields:
            if hasattr(self.fields[field_name], '_choices'):
                if '1' in getattr(self.fields[field_name], '_choices')[0]:
                    return True
        return False

    def save(self, sf, name_of_survey, id):
        dictionary = {'Name': name_of_survey, 'Contact__c': id}
        for question in self.cleaned_data:
            if "divider" in question:
                continue

            answer = app.survey_vars.encrypt(self[question].value())
            if type(answer) == list:
                answer = "\r\n".join(answer)
            dictionary[f"Question_{question}__c"] = answer

        sf.Surveys__c.create(dictionary)


class SubmitRec(forms.Form):
    file = forms.FileField(required=True, label='Recommendation', label_suffix=' *',
                           validators=[FileExtensionValidator(allowed_extensions=['pdf', 'PDF'])])
    id = forms.CharField(required=True, min_length=15,
                         max_length=20, label='Dream ID', label_suffix=": *")

    def save(self):
        sf = Salesforcer()
        file = self['file'].value()
        contact_id = self['id'].value().replace(" ", "")
        try:
            filename = f"Recommendation-{contact_id.split('-')[1]}"
            contact_id = contact_id.split("-")[0]
        except:
            return "Unable to match ID with student, please verify that it is correct."
        application_id = sf.query(
            f"SELECT Id FROM Scholarship_Application__c WHERE Contact__c='{contact_id}' AND Scholarship_Review_Year__c='{sv.updated_vars['scholarship_review_year']}'")['records'][0]['Id']

        if sf.query(f"SELECT Id FROM Attachment WHERE Name='{filename}' AND ParentId='{application_id}'")['totalSize'] == 0:
            sf.Attachment.create({'Name': filename, 'ParentId': application_id, 'body': str(
                base64.b64encode(file.read()))[2:-1]})
            return "Successfully uploaded the recommendation."
        else:
            return "You have already submitted this recommendation. Thanks!"


class ScholarshipAttachments(forms.Form):
    def __init__(self, type, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if type == "Renewal":
            choices = [("C_Transcript", "College Transcript")]
        elif type == "New (HS)":
            choices = [("Essay", "Scholarship Essay"),
                       ("HS_Transcript", "High School Transcript"),
                       ("SAT_Score", "SAT Score (optional)"),
                       ("ACT_Score", "ACT Score (optional)"),
                       ]
        elif type == "New (College)":
            choices = [("Essay", "Scholarship Essay"),
                       ("HS_Transcript", "High School Transcript"),
                       ("C_Transcript", "College Transcript"),
                       ("SAT_Score", "SAT Score (optional)"),
                       ("ACT_Score", "ACT Score (optional)")
                       ]

        print(choices)

        self.fields['file_type'] = forms.ChoiceField(
            required=False,
            choices=choices,
            label="Please select the file you're uploading from the list.",
        )
        self.fields['file'] = forms.FileField(label='File', required=False, label_suffix=' *', validators=[
                                              FileExtensionValidator(allowed_extensions=['pdf', 'PDF', 'PNG', 'png', 'jpeg', 'JPEG'])])

    def save(self, sf, parent_id):
        file = self['file'].value()
        name = f"{self['file_type'].value()}.pdf"

        if not file or not name:
            return False

        if sf.query(f"SELECT Id FROM Attachment WHERE Name='{name}' AND ParentId='{parent_id}'")['totalSize'] == 0:
            sf.Attachment.create({'Name': name, 'ParentId': parent_id, 'body': str(
                base64.b64encode(file.read()))[2:-1]})
            return True
        else:
            return False


class SubmitDoc(forms.Form):
    file = forms.FileField(required=True, label='File', label_suffix=' *',
                           validators=[FileExtensionValidator(allowed_extensions=['pdf', 'PDF'])])

    def save(self, parent_id, doc_name=None):
        sf = Salesforcer()
        file = self['file'].value()
        if doc_name:
            name = doc_name
        else:
            name = file.name
        sf.Attachment.create({'Name': name, 'ParentId': parent_id, 'body': str(
            base64.b64encode(file.read()))[2:-1]})


class SubmitAppReview(forms.Form):
    def __init__(self, comments, user, interview=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If the current user matches one of the assignments set them as the reviewer
        self.reviewer = False
        for comment in comments:
            if not interview:
                if user.id and comment['Contact__c'] == user.id:
                    self.reviewer = user.id
                    self.id = comment['Id']  # Id of Scholarship Assignment
            elif interview and comment['Interview_Code__c']:
                self.id = comment['Id']

        for comment in comments:
            initial = "Academic Achievement: \n\nOvercoming Adversity: \n\nCommunity Engagement/Employment/Leadership: \n\nDemonstrated Need:"
            name = comment['FirstName']

            if comment['Interview_Code__c']:
                initial = f"{initial} \n\nWhat is something you learned from this interview that was not found in the application?"
                name = "Interview Panel"
            if comment['Comments__c']:
                initial = comment['Comments__c']
            self.fields[f"{comment['Id']}"] = forms.CharField(
                initial=initial,
                required=False,
                widget=forms.Textarea,
                label=f"Comments ({name})")

            if (user.id == comment['Contact__c'] and not comment['Complete__c']) or comment['Interview_Code__c']:
                val = None
                choice_list = [(2, 'Yes'), (1, 'Maybe'), (0, 'No')]
                if comment['Interview_Code__c']:
                    choice_list = [(2, 'Absolutely Must Fund'),
                                   (1, 'Fund if Possible'), (0, 'Do not Fund')]
                if comment['Decision__c']:
                    val = int(comment['Decision__c'])
                self.fields['Decision__c'] = forms.ChoiceField(
                    initial=val,
                    required=False,
                    choices=choice_list,
                    widget=forms.RadioSelect,
                    label='Decision',
                )

    def save(self, final=False):
        sf = Salesforcer()
        update = {
            'Decision__c': self['Decision__c'].value(),
            'Comments__c': self[self.id].value(),
        }
        if final:
            update['Complete__c'] = True

        sf.Scholarship_Assignment__c.update(self.id, update)
        return


class EditUserPass(forms.Form):
    New_User = forms.CharField(max_length=20, label='New Username')
    New_Password = forms.CharField(
        required=False, max_length=20, label='New Password')
    Dream_ID = forms.CharField(
        required=True, min_length=15, max_length=20, label='Dream ID')

    def save(self, user, commit=False):
        if user.pk == self['Dream_ID'].value():
            update_dic = {}
            if not self['New_User'].value() == (None or ''):
                if not self['New_User'].value() == user.usrnm:
                    user.usrnm = self['New_User'].value()
                    update_dic['Dream_Portal__c'] = user.usrnm
                    commit = True

            if not self['New_Password'].value() == (None or ''):
                password = encrypt(self['New_Password'].value())
                update_dic['Dream_Portal_Password__c'] = password
                commit = True

            if commit:
                sf = Salesforcer()
                sf.Contact.update(user.pk, update_dic)
                user.save()
                print(f'Successfully Updated: {user.name}, {user.last}')
        return

    def clean_New_User(self):
        username = self.cleaned_data.get('New_User')
        user = temp_user.objects.get(id=self['Dream_ID'].value())
        if user.usrnm == username:
            return username
        sf = Salesforcer()
        same_username = sf.query(
            f"SELECT Id FROM Contact WHERE Dream_Portal__c='{username}'")
        if same_username['totalSize'] > 0:
            raise forms.ValidationError('That username is already taken')
        return username


class UnauthSignup(forms.Form):
    Name = forms.CharField(required=True, max_length=50, label='Full Name')
    Email = forms.EmailField(required=True, max_length=255, label='Email')
    Phone = forms.CharField(required=True, min_length=10, label='Phone')

    def save(self, volunteer_job_id, commit=False):
        info = f"{self['Name'].value()} | Email: {self['Email'].value()} | Phone: {self['Phone'].value()}"
        if commit:
            sf = Salesforcer()
            sf.Volunteer_Job__c.update(volunteer_job_id, {
                "Info__c": info,
                "Contact__c": "0031R0000213Qi8QAE",
            })
        return


class Forgot_creds(forms.Form):
    email = forms.CharField(required=True, label='Email')

    def save(self):
        email = self.cleaned_data.get('email')
        sf = Salesforcer()

        results = sf.query(
            f"SELECT Id, LastName FROM Contact WHERE Email='{email}' OR npe01__AlternateEmail__c='{email}' OR npe01__HomeEmail__c='{email}' OR npe01__Preferred_Email__c='{email}' OR npe01__WorkEmail__c='{email}'")

        if results['totalSize'] == 1:
            info = results['records'][0]
            send_mail('Dream Portal Login Info',
                      forgot_info(info['Id'], info['LastName']),
                      'carlos@dreamproject-va.org',
                      [email],
                      html_message=forgot_info(info['Id'], info['LastName']))
            return True
        else:
            return False
