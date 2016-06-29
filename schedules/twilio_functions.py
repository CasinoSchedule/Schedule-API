
from twilio.rest import TwilioRestClient


account_sid = "{{ AC4fda2321629a018a8fe340993ca05a79 }}" # Your Account SID from www.twilio.com/console
auth_token  = "{{ cc11d51e94c1fd2d4df5ee72b14cae92 }}"


client = TwilioRestClient(account_sid, auth_token)

message = client.messages.create(body="Hello from Python",
    to="+12345678901",    # Replace with your phone number
    from_="+12345678901") # Replace with your Twilio number

print(message.sid)

