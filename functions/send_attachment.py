import smtplib
import json
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

def get_gmail_credentials():
    cred = json.loads(open('authorizations/gmail-credentials.json').read())
    return cred

def send_attachment_over_email(sender, receivers, subject, filepath, message=''):

    # create message with attachment
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(receivers)

    part = MIMEBase('application', "octet-stream")
    part.set_payload(open(filepath, "rb").read())
    encoders.encode_base64(part)

    part.add_header(
        'Content-Disposition', 'attachment; filename="{}"'.format(filepath.split('/')[-1])
        )

    msg.attach(part)

    # creates SMTP session 
    s = smtplib.SMTP('smtp.gmail.com', 587) 

    # start TLS for security 
    s.starttls() 

    # Authentication 
    cred = get_gmail_credentials()
    s.login(cred['email'], cred['password'])

    # sending the mail 
    s.sendmail(sender, msg['To'], msg.as_string()) 

    # terminating the session 
    s.quit()