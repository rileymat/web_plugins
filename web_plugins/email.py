import smtplib

def send_email(sender, recipient, message):
	formatted_message = 'From: {name} <{email}>\n'.format(**sender) +\
						'To: {name} <{email}>\n'.format(**recipient) +\
						'Subject: {subject}\n\n{message}\n'.format(**message)
	smtpObj = smtplib.SMTP('localhost')
	smtpObj.sendmail(sender["email"], [recipient["email"]], formatted_message)         
	#except smtplib.SMTPException: #deal with this exception later.

