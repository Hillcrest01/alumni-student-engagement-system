from flask import render_template, current_app
from flask_mail import Message
from .extensions import mail

def send_email(to, subject, template, **kwargs):
    """Send formatted email using Flask-Mail"""
    msg = Message(
        subject=subject,
        recipients=[to],
        html=render_template(f'emails/{template}', **kwargs),
        sender=current_app.config['MAIL_DEFAULT_SENDER']
    )
    
    try:
        mail.send(msg)
        current_app.logger.info(f"Email sent to {to}")
    except Exception as e:
        current_app.logger.error(f"Failed to send email to {to}: {str(e)}")