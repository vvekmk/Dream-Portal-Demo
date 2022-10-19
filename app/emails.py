email_sender = 'Carlos Puerta <carlos@dreamproject-va.org>'

carlossig = """
    <br>
    Regards,<br>
    <br>
    Carlos Puerta<br>
    Program Manager & Systems Developer<br>
    The Dream Project<br>
    O: (703) 672-1541<br>
    <br>
    <a href='https://www.cfp-dc.org/accept/list.php?y=2018'>"One of the Best Local Non-Profits in the Washington Area"</a><br>
    Support us, support Dreamers <a href='https://www.dreamproject-va.org/donate/'>here</a>. <br>
    <img src="https://www.dreamproject-va.org/wp-content/uploads/2019/03/Dream-Project-Logo.395.png" alt="Dream Project Logo" width='200'><br>
    Follow us on Twitter: @DreamProjectVA <br>
    Like us on Facebook: Facebook.com/DreamProjectVA
    """

emmasig = """
    <br>
    With gratitude,<br>
    <br>
    Emma Violand-Sanchez<br>
    Dream Project Founder and Chair of the Board,<br>
    The Dream Project <br>
    <br>
    <a href='https://www.cfp-dc.org/accept/list.php?y=2018'>"One of the Best Local Non-Profits in the Washington Area"</a><br>
    Support us, support Dreamers <a href='https://www.dreamproject-va.org/donate/'>here</a>. <br>
    <img src="https://www.dreamproject-va.org/wp-content/uploads/2019/03/Dream-Project-Logo.395.png" alt="Dream Project Logo" width='200'><br>
    Follow us on Twitter: @DreamProjectVA <br>
    Like us on Facebook: Facebook.com/DreamProjectVA
    """


def log_in_info(ID, lastname):
    message = f"""
    You have successfully registered for the Dream Portal. Please use the following information to log in:<br>
    <br>
    Dream ID: {ID} <br>
    Last Name: {lastname} <br>
    <br>
    <b><i>KEEP THIS INFORMATION IN YOUR RECORDS AS IT CAN ALWAYS BE USED TO LOG IN, AND IT WILL BE NEEDED IF YOU EVER FORGET YOUR CUSTOM USERNAME/PASSWORD</b></i> <br>
    <br>
    Once you log in, you can create a custom username and password to make logging in easier. To do this, log in, go to profile, and click "Edit Login Info".
    <br>
    """
    return message + carlossig


def forgot_info(ID, lastname):
    message = f"""
    Here are your credentials for the Dream Portal:<br>
    <br>
    Dream ID: {ID} <br>
    Last Name: {lastname} <br>
    <br>
    <b><i>Keep this information in your records so that you may always log in.</b></i> <br>
    <br>
    Once you log in, you can create a custom username and password to make logging in easier. To do this, go to your profile, and click "Edit Login Info".
    <br>
    """
    return message + carlossig


def app_log_in_info(ID, lastname):
    message = f"""
    We have received your application. Please use the following information to log in:<br>
    <br>
    Dream ID: {ID} <br>
    Last Name: {lastname} <br>
    <br>
    Please reach out to your recommenders and make sure they submit a recommendation for you before February 11th. They should have received an email with instructions on how to submit the recommendation. If they did not receive it, please contact me as soon as possible.
    <br>
    """
    return message + carlossig


def rec_info(rec, student, ID):
    message = f"""
    Dear {rec},
    <br> <br>
    {student} has listed you as one of their recommenders for the Dream Project Scholarship. To submit a recommendation, please go to <a href='http://dreamportal.herokuapp.com/scholarship/'>http://dreamportal.herokuapp.com/scholarship/</a> and follow the instructions. Please submit your recommendation as soon as possible. Recommendation submitted after February 11th may not be reviewed and could influence the likelyhood a student receives a scholarship.
    <br><br>
    Use this Dream ID for {student}:
    <br><br>
    {student}: <b>{ID}</b> <br>
    <br>
    <b>Please note that his ID is unique to you as a recommender, please do not share or forward this ID</b>
    <br>
    The Dream Project supports students whose immigration status poses a barrier to college. We support students by offering high school juniors and seniors with a mentoring program aimed at easing the college application process, and by providing 95 students with a scholarship. To learn more about what we do, feel free to reach out to me at <a href='mailto:carlos@dreamproject-va.org'>carlos@dreamproject-va.org</a> or to check out our website <a href='www.dreamproject-va.org'>www.dreamproject-va.org</a>.
    <br>
    """
    return message + carlossig


def rec_reminder(rec, student, ID):
    message = f"""
    Dear {rec},
    <br> <br>
    This is a reminder that {student} has listed you as one of their recommenders for the Dream Project Scholarship, and we have not received your recommendation yet. I know some of you have had some trouble with the website, but all those issues should be fixed! To submit a recommendation, please go to <a href='http://dreamportal.herokuapp.com/scholarship/'>http://dreamportal.herokuapp.com/scholarship/</a> and follow the instructions. There is a circular button at the bottom of the page with an envelope, clicking that will take you to the right page.  Please submit your recommendation as soon as possible. Recommendation submitted after February 11th may not be reviewed and could influence the likelyhood a student receives a scholarship.
    <br><br>
    Use this Dream ID for {student}:
    <br><br>
    {student}: <b>{ID}</b> <br>
    <br>
    <b>Please note that his ID is unique to you as a recommender, please do not share or forward this ID</b>
    <br>
    The Dream Project supports students whose immigration status poses a barrier to college. We support students by offering high school juniors and seniors with a mentoring program aimed at easing the college application process, and by providing 95 students with a scholarship. To learn more about what we do, feel free to reach out to me at <a href='mailto:carlos@dreamproject-va.org'>carlos@dreamproject-va.org</a> or to check out our website <a href='www.dreamproject-va.org'>www.dreamproject-va.org</a>.
    <br>
    """
    return message + carlossig


def unauth_signup(name, date):
    message = f"""
    {name},
    <br> <br>
    You have successfully signed up to interview on {date}. This year, the interviews will be held online via Zoom. Please plan on logging in by 5:30pm so you can get set up before the first interview at 6pm. Please be on the lookout for another email with more information on what to expect, and how to access your interview materials.
    <br><br>
    Thank you for all of your support and see you soon!
    """
    return message + carlossig


def interview_signup(name, date):
    message = f"""
    {name},
    <br> <br>
    You have successfully signed up for an interview on {date}. The interviews will be online this year via Zoom. \
    Please be on the lookout for another email with more information closer to the date of your interview.
    <br>
    """
    return message + carlossig


def accept(first, last, id):
    message = f"""
    Dear {first},
    <br> <br>
    After carefully reviewing your appliction we want to extend an invitation to the Dream Project Scholarship Interviews. This is the next step in becoming a Dream Scholar. Interviews will be held March 9th, 10th, 11th and 12th from 6:00pm to 8:30pm at the Arlington Career Center. To schedule a date for your interview you must first log into the Dream Portal and fill out the interview survey (It will be an icon on the homepage). Please note that this survey is completely anonymous and will not be used to make any decisions on whether you will be awarded a scholarship. After completing the survey, you will be redirected to a page where you can see the available times.
    <br><br>
    Here's your log in information in case you have forgotten:
    <br><br>
    Dream ID: {id} <br>
    Last Name: {last}
    <br>
    <br>
    Let me know if you have any questions.
    """
    return message + carlossig


def versatile(msg):
    return msg + carlossig


def emmasign(msg):
    return msg + emmasig


def interview_email(name, date, password):
    message = f"""
    Dear {name}, <br><br>
    Thank you for interviewing Dream Scholar applicants. Plan to be with us from 5:30 until 9:00 pm on the day of your panel, {date}. <br><br>
    All interviews will be remote via Zoom. You will need to have a computer with a camera so that your face can be seen by the other panelists and the applicants. If you are not familiar with Zoom please contact me at carlos@dreamproject-va.org for a brief training. The zoom link to join is <a href=' https://us02web.zoom.us/j/85802573844?pwd=bmJJOUZaa3RML2xScklFTVR6UGZjdz09'> https://us02web.zoom.us/j/85802573844?pwd=bmJJOUZaa3RML2xScklFTVR6UGZjdz09</a>. The passcode is: 729320.<br><br>

    You may review the applications of the students you'll be interviewing ahead of time. You can do this my going to <a href='http://dreamportal.herokuapp.com/scholarship/interview/password/'>the Dream Portal</a> and typing in the password for your assigned night. <b>If you signed up for more than one night, you'll receive multiple emails with different passwords.</b> <br><br>

    <b>The password for {date} is {password}.</b><br><br>
    Please note that the list of students may increase, decrease, or change because of student cancellations or sign-ups.
    <br><br>
    Here is what you can expect the day of the interview:<br>
    You will be in a group of 4-5 interviewers. A scholarship committee member will chair. Others in your group will include board members, community support members and graduates of our scholarship program. At 5:30 the group will convene to look over the applications of the five scholars, discuss plans, get acquainted and get set up. Then starting at 6PM, each scholar will come in at half hour intervals. The last interview is scheduled at 8:00 pm. At the end of each interview you will work together to submit the following:<br>
    <ul>
        <li>A few notes about, academic achievement, hardships overcome, non-academic activities and need for a scholarship</li>
        <li>A rating for the student as “absolutely must fund”, “fund if money is available” and “do not fund”.</li>
        <li>Finally, you will answer the question: What did you learn about this candidate that was not in the written application</li>
    </ul>
    At 8:30, you will also create a consensus ranking to be used as input to the scholarship committee. Please note we are interviewing more people than we have scholarships so not everyone interviewed will receive a scholarship.
    You will be given a list of topics to cover in the interview but if something about the candidate interests you, feel free to probe. The whole panel will have a chance to ask questions.<br>
    The criteria we use to select scholars are:<br>
    <ul>
        <li>Academic achievement.</li>
        <li>Obstacles overcome.  This is used to offset lower academic achievement but no matter what, scholarship recipients should have the ability to succeed in college.</li>
        <li>Activities in or out of school, leadership, employment, community engagement, caring for family members.</li>
        <li>Need for a scholarship.</li><br>
    </ul>
    Please emphasize to the students that as Dream Scholars they will be joining a community and that they will be expected to participate in it by attending Dream Project events and completing the fall survey. The Dream Summit will be valuable to them because it gives them information that is particularly important to immigrant students in college. And if they are selected they may have the opportunity to participate in a program called Beyond 12 which provides coaches who are recent college grads to help them figure out many aspects of college life. We also have an emergency load fund.<br><br>
    I look forward to seeing you at 5:30 on {date}.
    {carlossig}
    """
    return message


def fall_survey_reminder(first, last, id):
    last = last.replace(" ", "")
    link = f"http://dreamportal.herokuapp.com/alogin/{id}/{last}/survey&fall-survey-scholars"
    message = f"""
    Hi there {first},
    <br> <br>
    This is a reminder that the mandatory fall survey is live. Failure to complete this survey will mean you will not be eligible for renewal! If you are planning on applying for renewal in December, please make sure you answer this survey by Friday, Dec 10th.
    <br> <br>
    You may access the survey by <a href={link}>clicking here</a>, or copy-pasting this link ({link})
    <br> <br>
    PLEASE NOT THAT THIS LINK IS UNIQUE TO YOU, SO PLEASE DO NOT FORWARD OR SHARE THIS LINK WITH ANYONE.
    <br> <br>
    If you have any questions or concerns please let me know,
    <br> <br>
    Regards,
    <br> <br>
    Carlos Puerta<br>
    Program & Systems Manager<br>
    The Dream Project<br>
    """
    return message


def fall_survey_reminder_alumni(first, last, id):
    last = last.replace(" ", "")
    link = f"http://dreamportal.herokuapp.com/alogin/{id}/{last}/survey&fall-survey-alumni-1"
    message = f"""
    Hi there {first},
    <br> <br>
    I am reaching out one last time to please ask for 10 minutes of your time. We have gotten a very bad response rate from our Alumni with our annual fall survey. We would greatly appreciate you taking a few minutes to complete the survey. This is a very easy way to give back to our ogranization, as this information helps us better tell the story of our students through numbers and data which is then used for fundraising!
    <br> <br>
    You may access the survey by <a href={link}>clicking here</a>, or copy-pasting this link ({link})
    <br> <br>
    PLEASE NOT THAT THIS LINK IS UNIQUE TO YOU, SO PLEASE DO NOT FORWARD OR SHARE THIS LINK WITH ANYONE.
    <br> <br>
    If you have any questions or concerns please let me know,
    <br> <br>
    Regards,
    <br> <br>
    Carlos Puerta<br>
    Program & Systems Manager<br>
    The Dream Project<br>
    """
    return message


def b12_eval_email(first, last, id, year):
    last = last.replace(" ", "")
    link = f"http://dreamportal.herokuapp.com/alogin/{id}/{last}/survey&b12-evaluation-{year}"
    message = f"""
    {first},
    <br> <br>
    As a Beyond12 student, we are reaching out to ask you to complete a very short survey to understand how Beyond12 is working for you. The survey shouldn't take more than 10 minutes, and it helps make informed decisions on the Beyond12 coaching program. We would love to get your insight.
    <br> <br>
    You may access the survey by <a href={link}>clicking here</a>, or copy-pasting this link ({link})
    <br> <br>
    PLEASE NOT THAT THIS LINK IS UNIQUE TO YOU, SO PLEASE DO NOT FORWARD OR SHARE THIS LINK WITH ANYONE.
    <br> <br>
    If you have any questions or concerns please let me know,
    <br> <br>
    Regards,
    <br> <br>
    Carlos Puerta<br>
    Program & Systems Manager<br>
    The Dream Project<br>
    """
    return message


def interview_invitation_supporter():
    message = f"""
    To Our Generous Supporters, <br><br>

    I want to extend an invitation to participate as an interviewer in our scholarship review process. This is a fantastic volunteering opportunity to get to know the community that we serve and some of the new scholars that will be selected, but we also know that supporters find it inspirational to have a chance to talk with these hard-working students. We will be interviewing students from March 14th-17th, and as much as we would love to have every one of you participate, space is limited. <br><br>

    If you'd like to sign up to be an interviewer please do so by <a href="http://dreamportal.herokuapp.com/scholarship/interview/sign-up">clicking here</a>.<br><br>

    If you have any questions or problems please let me know!
    <br>
    {carlossig}    
    """
    return message


def interview_invitation_students(First, Id, Last):
    Last = Last.replace(" ", "")
    link = f"http://dreamportal.herokuapp.com/alogin/{Id}/{Last}/scholarship&interview&student&sign-up"
    message = f"""    
    Hi {First},
    <br><br>
    Congratulations. You have been selected to interview for a Dream Project Scholarship and access to the benefits of membership with the Dream Project community -- a community whose sole purpose is to help you succeed in college. 
    <br><br>
    The half hour Zoom interview will be scheduled between March 14-17 between 6:00pm and 8:30pm.
    <br><br>
    To schedule an interview time please <a href="{link}">click here</a>! Interview times are awarded on a first-come-first-serve basis, so sign up as soon as you can.
    <br><br>
    The interview will be a chance for members of the Dream Project community to get to know you better and for you to learn about what it means to be Dream Scholar. Participants in the interview will include members of the Scholarship Committee, Donors, Board Members, and Alumni of the Dream Project who have graduated from college. As such it is required that you turn your camera on for your Zoom interview. This is a competitive process, and not everyone who is interviewed will receive a scholarship. Do your best to schedule an interview, show up ON TIME, and be prepared to answer questions about your goals, the challenges you have faced, and your commitment to your community.
    <br><br>
    We look forward to meeting you soon.
    <br>
    {carlossig}    
    """
    return message
