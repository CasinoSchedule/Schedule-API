import os
from twilio.rest import TwilioRestClient


def twilio_shift(number, message):
    """
    number is a 10 digit phone number string.
    """
    account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    auth_token = os.environ["TWILIO_AUTH_TOKEN"]

    client = TwilioRestClient(account_sid, auth_token)

    message = client.messages.create(body=message,
                                     to="+1" + number,
                                     from_="+17602538062")
