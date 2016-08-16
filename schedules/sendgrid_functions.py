import sendgrid
import os
from sendgrid.helpers.mail import *


def send_text_email(from_email, to_email, subject, body):
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email(from_email)
    to_email = Email(to_email)
    content = Content('text/plain', body)
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    return response
