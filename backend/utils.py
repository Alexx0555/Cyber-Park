import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_email_utility(to_mail,sub,body,attachments=None,is_html=False):
    try:
        smtp_server=os.getenv('MAIL_SERVER')
        smtp_port=int(os.getenv('MAIL_PORT'))
        smtp_uname=os.getenv('MAIL_USERNAME')
        smtp_pwd=os.getenv('MAIL_PASSWORD')
        msg = MIMEMultipart()
        msg['From'] = smtp_uname
        msg['To'] = to_mail
        msg['Subject'] = sub

        if is_html:
            msg.attach(MIMEText(body, 'html'))
        else:
            msg.attach(MIMEText(body, 'plain'))
        
        if attachments:
            for filename, content_type, data in attachments:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(data)
                encoders.encode_base64(part)
                part.add_header('Content-Disposition',f'attachment; filename= {filename}')
                msg.attach(part)
        
        server=smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_uname, smtp_pwd)
        txt = msg.as_string()
        server.sendmail(smtp_uname, to_mail, txt)
        server.quit()
        logger.info(f"Email sent successfully to {to_mail}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {to_mail}: {str(e)}")
        return False
 
def send_html_email(to_mail, sub, html_body, attachments=None):
    return send_email_utility(to_mail, sub, html_body, attachments, is_html=True)

def send_bulk_email(email_list, sub, body, attachments=None, is_html=False):
    re = {'success_count': 0,'failure_count': 0,'failed_emails': []}
    
    for email in email_list:
        if send_email_utility(email, sub, body, attachments, is_html):
            re['success_count'] += 1
        else:
            re['failure_count'] += 1
            re['failed_emails'].append(email)

    return re

def send_email_with_attachment(to_mail, sub, html_body, csv_content, filename):
    try:
        attachments = [(filename, 'text/csv', csv_content.encode('utf-8'))]
        return send_email_utility(to_mail, sub, html_body, attachments, is_html=True)

    except Exception as e:
        logger.error(f"Failed to send email with CSV attachment: {str(e)}")
        return False