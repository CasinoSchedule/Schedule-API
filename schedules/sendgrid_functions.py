import sendgrid
import os
from sendgrid.helpers.mail import *


def signup_email(profile_email, profile_id):
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("admin@rosterbarn.com")
    subject = "Welcome to Roster Barn. New account signup."
    to_email = Email(profile_email)
    signup_link = 'http://0.0.0.0:5000/employee/{}'.format(profile_id)
    body = "A profile has been created for you, please click the following " \
           "link to sign up. \n {}".format(signup_link)
    content = Content("text/plain", body)
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    return response.status_code


def email_shift(email, message):
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("shift.notifications@rosterbarn.com")
    subject = "You have new shifts posted"
    to_email = Email(email)
    body = message
    content = Content('text/plain', body)
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    return response.status_code


def general_email(subject, body, email):
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("messages@rosterbarn.com")
    to_email = Email(email)
    content = Content('text/plain', body)
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    return response.status_code


def send_text_email(from_email, to_email, subject, body):
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email(from_email)
    to_email = Email(to_email)
    content = Content('text/plain', body)
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    return response
