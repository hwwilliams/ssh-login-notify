# Download the helper library from https://www.twilio.com/docs/python/install
from twilio.rest import Client

# Your Account Sid and Auth Token from twilio.com/console
# DANGER! This is insecure. See http://twil.io/secure
account_sid = 'XXXXXXXXXXXXXXXXXXXXX'
auth_token = 'XXXXXXXXXXXXXXXXXXXXX'
client = Client(account_sid, auth_token)

message = client.messages \
    .create(
         body="Test Message",
         messaging_service_sid='XXXXXXXXXXXXXXXXXXXXX',
         to='+1234567890'
     )

print(message.sid)
