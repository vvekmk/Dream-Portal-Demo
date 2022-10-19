import base64
import os

from django.db import models
from simple_salesforce import Salesforce

from app.models import temp_user
from app.survey_vars import recordtypes


class salesforce_auth:
    def authenticate(self, request, username, password):
        """Custom authentication backend. It checks to see if 
        custom username and password as set, and if not, uses 
        SF ID and last name to authenticate"""

        success = False
        sf = Salesforcer()
        if not username or not password:
            return None

        # Try custom username and password
        contact = sf.query(
            f"SELECT Id, LastName FROM Contact WHERE (Dream_Portal__c='{username}' AND Dream_Portal_Password__c='{encrypt(password)}')")
        if contact['totalSize'] == 1:
            username = contact['records'][0]['Id']
            password = contact['records'][0]['LastName']
            success = True

        # If no custom username and password try ID with Last name
        if not success:
            if len(username) != 18:
                return None

            contact = sf.query(
                f"SELECT LastName FROM Contact WHERE Id='{username}'")
            if contact['totalSize'] == 1:
                lastname = contact['records'][0]['LastName']
                if password.replace(" ", "").upper() == lastname.replace(" ", "").upper():
                    success = True
            else:
                return None

        if success:
            contact = sf.Contact.get(username)
            type = contact['RecordTypeId']
            if type == recordtypes['scholar']:
                user = temp_user.objects.create_user(
                    password=password, **contact, kind='scholar', is_scholar=True)

            elif type == recordtypes['mentee']:
                user = temp_user.objects.create_user(
                    password=password, **contact, kind='mentee', is_mentee=True)

            elif type == recordtypes['prospective']:
                user = temp_user.objects.create_user(
                    password=password, **contact, kind='prospective')

            elif contact['Named_Scholarship_Donor__c'] == True:  # NS Donor
                scholarships = NSData(sf, username)
                user = temp_user.objects.create_user(
                    password=password, **contact, kind='donor', is_donor=True, scholarships=scholarships)

            else:  # Generic
                user = temp_user.objects.create_user(
                    password=password, **contact)
            return user

        return None

    def get_user(self, user_id):
        try:
            return temp_user.objects.get(id=user_id)
        except:
            return None


def NSData(instance, id):
    """Gets Named Scholarship information for NS donors
    Currently not used as NS information is not updated in DB
    and donors do not use the portal."""
    scholarships = []
    scholarships_query = instance.query(
        f"SELECT Named_Scholarship__c FROM Donor_Recepient__c WHERE Contact__c='{id}' AND Type__c='Donor'")
    for scholarship in scholarships_query['records']:
        students = []
        scholarship = instance.Named_Scholarship__c.get(
            scholarship['Named_Scholarship__c'])
        temp_id = scholarship['Id']
        student_query = instance.query(
            f"SELECT Contact__c FROM Donor_Recepient__c WHERE Named_Scholarship__c='{temp_id}' AND Type__c='Recipient'")
        for student in student_query['records']:
            student = instance.Contact.get(student['Contact__c'])
            students.append(
                {'name': f"{student['FirstName']} {student['LastName'][0]}."})

        string = f"|'ID': '{temp_id}', 'Name': '{scholarship['Name']}','Established__c': '{scholarship['Established__c']}','Scholarship_Description__c': '{scholarship['Scholarship_Description__c']}','students': {students}#"
        scholarships.append(string)
    return scholarships


def Salesforcer():
    pwd = os.environ.get('SF_Pwd')
    token = os.environ.get('SF_Token')
    return Salesforce(username='carlos@dreamproject-va.org',
                      password=pwd,
                      security_token=token)


def scholarship_info(list):
    """Ugly solution for local DB being unable to take complex objects"""
    temp = []
    list = eval(list)
    for scholarship in list:
        tempstr = scholarship.replace('|', "{")
        tempstr = tempstr.replace('#', "}")
        tempstr = tempstr.replace('\r', "")
        tempstr = tempstr.replace('\n', " ")
        temp.append(eval(tempstr))
    return temp


def encrypt(password, key='Gg7perUz12AdWMpnWyXk'):
    """Encrypts passwords for SF"""
    encoded_chars = []
    for i in range(len(password)):
        key_c = key[i % len(key)]
        encoded_c = chr(ord(password[i]) + ord(key_c) % 256)
        encoded_chars.append(encoded_c)
    encoded_string = ''.join(encoded_chars)
    return encoded_string
