import sendgrid
import os
from sendgrid.helpers.mail import *


def signup_email(profile_email, profile_id):
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("admin@rosterbarn.com")
    subject = "Welcome to Roster Barn. New account signup."
    to_email = Email(profile_email)
    body = "A profile has been created for you, please click the following " \
           "link to sign up. \n {}".format(profile_id)
    content = Content("text/plain", body)
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    return response.status_code





# sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
# from_email = Email("test@example.com")
# subject = "Hello World from the SendGrid Python Library"
# to_email = Email("test@example.com")
# content = Content("text/plain", "some text here")
# mail = Mail(from_email, subject, to_email, content)
# response = sg.client.mail.send.post(request_body=mail.get())
#
# print(response.status_code)
# print(response.body)
# print(response.headers)