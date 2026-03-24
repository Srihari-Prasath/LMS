import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app


def send_email(to_email, subject, html_body):
    try:
        config = current_app.config
        if not config.get('MAIL_ENABLED'):
            current_app.logger.info(f'Email not enabled. Would send to {to_email}: {subject}')
            return False

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = config.get('MAIL_USERNAME', 'noreply@lms.com')
        msg['To'] = to_email
        msg.attach(MIMEText(html_body, 'html'))

        with smtplib.SMTP(config['MAIL_SERVER'], config['MAIL_PORT']) as server:
            server.starttls()
            server.login(config['MAIL_USERNAME'], config['MAIL_PASSWORD'])
            server.send_message(msg)
        return True
    except Exception as e:
        current_app.logger.error(f'Email send failed: {e}')
        return False


def send_issue_notification(user, book, due_date):
    subject = f'Book Issued: {book.title}'
    body = f"""
    <h2>Book Issued Successfully</h2>
    <p>Hi {user.name},</p>
    <p><strong>{book.title}</strong> by {book.author} has been issued to you.</p>
    <p>Due Date: <strong>{due_date.strftime('%d %B %Y')}</strong></p>
    <p>Please return it on time to avoid fines (Rs. 5/day).</p>
    <p>— ALMS Library</p>
    """
    return send_email(user.email, subject, body)


def send_return_notification(user, book, fine):
    subject = f'Book Returned: {book.title}'
    fine_text = f'<p>Fine charged: <strong>Rs. {fine}</strong></p>' if fine > 0 else ''
    body = f"""
    <h2>Book Returned Successfully</h2>
    <p>Hi {user.name},</p>
    <p><strong>{book.title}</strong> has been returned.</p>
    {fine_text}
    <p>Thank you for using ALMS Library!</p>
    """
    return send_email(user.email, subject, body)


def send_due_reminder(user, book, due_date):
    subject = f'Reminder: {book.title} due on {due_date.strftime("%d %B %Y")}'
    body = f"""
    <h2>Due Date Reminder</h2>
    <p>Hi {user.name},</p>
    <p><strong>{book.title}</strong> is due on <strong>{due_date.strftime('%d %B %Y')}</strong>.</p>
    <p>Please return it on time to avoid late fines.</p>
    <p>— ALMS Library</p>
    """
    return send_email(user.email, subject, body)
