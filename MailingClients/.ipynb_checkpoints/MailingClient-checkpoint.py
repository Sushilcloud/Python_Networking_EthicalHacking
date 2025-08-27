# import smtp liburary
# protocol use for sent mails
#
import smtplib
from email import encoders
# for ordinary test we use
from email.mime.text import MIMEText
# MIMEBase uselfor attachment
from email.mime.base import MIMEBase
#
from email.mime.multipart import MIMEMultipart
# mention server domain name
server=smtplib.SMTP('smtp.gmail.com',587)
server.ehlo()



#saving the user id and password on your script
#server.login('userid','password')
with open('password.txt','r') as f:
    password=f.read()

# how login to your server
server.login('sushilgodiyal@gmail.com',password)

msg=MIMEMultipart()
msg['From']='gmail'
msg['To']='sushil_godiyal@hotmail.com'
msg['Subject']='just a test'

with open('message.txt','r') as f:
    message=f.read()

msg.attach(MIMEText(message,'plain'))
filename='daburlogo.png'
#rb for reading binary
attachment=open(filename,'rb')

# payload objects
p=MIMEBase('application','octet-stream')
p.set_payload(attachment.read())
encoders.encode_base64(p)
p.add_header('content-Disposition',f'attachment;    filename={filename}')
msg.attach(p)

text=msg.as_string()
server.sendmail('sushilgodiyal@gmail.com','sushil_godiyal@hotmail.com',text)