from app.refresh import refresh


def dub(string):
    return (string, string)


def list_dub(list):
    t_list = []
    for item in list:
        t_list.append((item, item))
    return t_list


updated_vars = refresh()

recordtypes = {
    'mentee': '012360000019GntAAE',
    'parent': '012360000008G3RAAU',
    'supporter': '012360000019GnyAAE',
    'scholar': '012360000007kVvAAI',
    'prospective': '012360000012H1kAAE',
    'alumni': '012360000019GnoAAE'
}

panelchairs = {
    "MP1": "0033600000m3BlEAAU",
    "MP2": "0033600001bdNLuAAM",

    "TP1": "0033600000m3BlEAAU",
    "TP2": "0033600000m3BblAAE",

    "WP1": "0033600000umIryAAE",
    "WP2": "0033600000Knw0tAAB",

    "RP1": "0033600001d4dJpAAI",
    "RP2": "",
}

Scales = {
    'agree4': ('Strongly Disagree', 'Disagree', 'Agree', 'Strongly Agree'),
    'agree5': ('Strongly Disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly Agree'),
    'agree7': ('Strongly Disagree', 'Disagree', 'Slightly Disagree', 'Neutral', 'Slightly Agree', 'Agree', 'Strongly Agree'),
    'involve5': ('Not at All Involved', 'Not Very Involved', 'Somewhat Involved', 'Very Involved', 'Extremely Involved'),
    'comfort5': ('Not at all comfortable', 'Not very comfortable', 'Somewhat comfortable', 'Very comfortable', 'Extremely comfortable'),
    'all5': ('None', 'Almost none', 'Some', 'Most', 'All'),
    'numbers': ('1', '2', '3', '4', '5'),
    'likely': ('Very Unlikely', 'Unlikely', 'Neutral', 'Likely', 'Very Likely'),
}

likert4 = [
    ('1', ''),
    ('2', ''),
    ('3', ''),
    ('4', '')
]

likert5 = [
    ('1', ''),
    ('2', ''),
    ('3', ''),
    ('4', ''),
    ('5', '')
]

likert7 = [
    ('1', ''),
    ('2', ''),
    ('3', ''),
    ('4', ''),
    ('5', ''),
    ('6', ''),
    ('7', '')
]

ethnicity = [
    ('', ''),
    ('White', 'White'),
    ('Black or African American', 'Black or African American'),
    ('Hispanic or Latino', 'Hispanic or Latino'),
    ('Native American', 'Native American'),
    ('Asian or Pacific Islander', 'Asian or Pacific Islander'),
    ('Prefer not to answer', 'Prefer not to answer')
]

yearofstudy = [
    ('Freshman', 'Freshman'),
    ('Sophomore', 'Sophomore'),
    ('Junior', 'Junior'),
    ('Senior', 'Senior')
]

employ = [
    ('', ''),
    ('Employed Full-time (40+hrs/week)', 'Employed Full-time (40+hrs/week)'),
    ('Employed Part-time (20-39hrs/week)', 'Employed Part-time (20-40hrs/week)'),
    ('Employed Part-time (fewer than 20hrs/week)',
     'Employed Part-time (fewer than 20hrs/week)'),
    ('Looking for Work', 'Looking for Work'),
    ('Part-Time Student', 'Part-Time Student'),
    ('Full-Time Student', 'Full-Time Student'),
]

financial_thoughts = [
    dub('I have applied for or plan to apply for other scholarships'),
    dub('I have received other scholarships to help with expenses'),
    dub('I will work while in school to pay for expenses'),
    dub('I can depend upon my family to provide some financial help to attend college'),
    dub('I have savings to help pay for college'),
    dub('I am eligible for in-state tuition to help with expenses'),
    dub('I plan to take out a loan'),
    dub('I will go to school part-time to be able to pay for classes'),
    dub('I have no idea of how I will pay for college')
]

financial_thoughts_c = [
    dub('I have plan to apply for other scholarships'),
    dub('I have received other scholarships to help with expenses'),
    dub('I work while in school to pay for expenses'),
    dub('My family helps provide financial help to attend college'),
    dub('I have savings to help pay for college'),
    dub('I am eligible for in-state tuition to help with expenses'),
    dub('I plan to take out a loan'),
    dub('I will go to school part-time to be able to pay for classes'),
]

status_key = [
    ('Beluga',          'U.S. Citizen'),
    ('Cheetah',         'Legal Permanent Resident (Green Card Holder)'),
    ('Platypus',        'DACA Recipient'),
    ('Hippopotamus',    'Temporary Protected Status (TPS)'),
    ('Narwhal',         'Undocumented'),
    ('Moose',           'Asylum Applicant'),
    ('Dodo',            'Asylee or Refugee'),
    ('Polar Bear',      'Special Immigrant Juvenile (SIJ) Pending'),
    ('Bonobo',          'Prefer not to answer'),
    ('Lemur',           'Other')
]

# Create status categories off the status key
status = []
for tup in status_key:
    status.append(dub(tup[1]))


def encrypt(answer, mode="e"):
    if isinstance(answer, str):
        answer = answer.strip()
        for st in status_key:
            if answer in st:
                if mode == "e":
                    return st[0]
                if mode == "d":
                    return st[1]
    return answer
