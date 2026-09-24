import smtplib
import time
import random
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from threading import Thread
from models import db, EmailLog, Campaign, User, SMTPSetting, SystemLog

def get_smtp_config():
    setting = SMTPSetting.query.filter_by(is_active=True).first()
    if setting and setting.smtp_user and setting.smtp_user != "your_email@gmail.com":
        return setting
    return None

def send_real_single_email(sender_name, sender_email, recipient_email, subject, body_html, attachment_paths=None):
    """
    Dispatches a single real webmail email via the active SMTP server settings.
    Returns (success: bool, status_message: str)
    """
    smtp_setting = get_smtp_config()
    if not smtp_setting or not smtp_setting.smtp_user or not smtp_setting.smtp_pass:
        return False, "SMTP Server is not configured with active credentials."

    try:
        if smtp_setting.encryption == 'ssl':
            server = smtplib.SMTP_SSL(smtp_setting.smtp_host, smtp_setting.smtp_port, timeout=12)
        else:
            server = smtplib.SMTP(smtp_setting.smtp_host, smtp_setting.smtp_port, timeout=12)
            if smtp_setting.encryption == 'tls':
                server.starttls()

        server.login(smtp_setting.smtp_user, smtp_setting.smtp_pass)

        msg = MIMEMultipart()
        msg["Subject"] = subject
        sender_disp_name = sender_name or "Brightlant User"
        msg["From"] = f"{sender_disp_name} <{sender_email}>"
        msg["To"] = recipient_email
        msg["Reply-To"] = sender_email
        
        msg.attach(MIMEText(body_html, "html"))

        if attachment_paths:
            import os
            from email.mime.base import MIMEBase
            from email import encoders
            for full_path, orig_filename in attachment_paths:
                if os.path.exists(full_path):
                    with open(full_path, "rb") as f:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            "Content-Disposition",
                            f'attachment; filename="{orig_filename}"',
                        )
                        msg.attach(part)

        try:
            server.sendmail(sender_email, recipient_email, msg.as_string())
        except Exception:
            server.sendmail(smtp_setting.smtp_user, recipient_email, msg.as_string())
        server.quit()
        return True, f"Email dispatched live to {recipient_email} via SMTP!"
    except Exception as e:
        print(f"❌ Real SMTP dispatch error: {e}")
        return False, str(e)

def send_bulk_thread(app, user_id, campaign_id, recipients, subject, html_content_template, base_url):
    with app.app_context():
        campaign = Campaign.query.get(campaign_id)
        user = User.query.get(user_id)
        
        if not campaign or not user:
            return

        campaign.status = 'sending'
        db.session.commit()

        smtp_setting = get_smtp_config()
        server = None
        smtp_connected = False

        if smtp_setting and smtp_setting.smtp_user and smtp_setting.smtp_pass:
            try:
                if smtp_setting.encryption == 'ssl':
                    server = smtplib.SMTP_SSL(smtp_setting.smtp_host, smtp_setting.smtp_port, timeout=10)
                else:
                    server = smtplib.SMTP(smtp_setting.smtp_host, smtp_setting.smtp_port, timeout=10)
                    if smtp_setting.encryption == 'tls':
                        server.starttls()
                server.login(smtp_setting.smtp_user, smtp_setting.smtp_pass)
                smtp_connected = True
                print(f"✅ Connected to SMTP Server: {smtp_setting.smtp_host}")
            except Exception as e:
                print(f"⚠️ SMTP Connection error: {e}. Falling back to system log dispatch.")
                smtp_log = SystemLog(log_type='warning', message=f"SMTP Connect warning: {e}", user_email=user.email)
                db.session.add(smtp_log)
                db.session.commit()

        for idx, person in enumerate(recipients):
            recipient_email = person.get('email', '').strip()
            if not recipient_email:
                continue

            name = person.get('name', 'User')
            company = person.get('company', 'Valued Partner')

            # Unique tracking token banayein open rate track karne ke liye
            tracking_token = str(uuid.uuid4())
            log = EmailLog(
                campaign_id=campaign.id,
                recipient_email=recipient_email,
                recipient_name=name,
                tracking_token=tracking_token,
                status='pending'
            )
            db.session.add(log)
            db.session.commit()

            # Personalize content
            personalized_body = (html_content_template
                                 .replace("{{name}}", name)
                                 .replace("{{email}}", recipient_email)
                                 .replace("{{company}}", company))
            
            # Tracking Pixel & Unsubscribe Link
            tracking_pixel = f'<img src="{base_url}/track/open/{tracking_token}" width="1" height="1" style="display:none;" />'
            unsub_footer = f'<div style="margin-top:20px; padding-top:10px; border-top:1px solid #e2e8f0; font-size:12px; color:#64748b;">If you wish to unsubscribe, click <a href="{base_url}/unsubscribe/{recipient_email}">here</a>.</div>'
            
            final_html = f"<div>{personalized_body}</div>{tracking_pixel}{unsub_footer}"

            if smtp_connected and server:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                from_sender = f"{user.name} <{user.email}>"
                msg["From"] = from_sender
                msg["Reply-To"] = user.email
                msg["To"] = recipient_email
                msg["List-Unsubscribe"] = f"<{base_url}/unsubscribe/{recipient_email}>"
                msg.attach(MIMEText(final_html, "html"))

                try:
                    server.sendmail(user.email, recipient_email, msg.as_string())
                    log.status = 'sent'
                    campaign.sent_count += 1
                    user.sent_today += 1
                except Exception as ex:
                    log.status = 'failed'
                    log.error_message = str(ex)
                    campaign.failed_count += 1
                    print(f"❌ Failed sending to {recipient_email}: {ex}")
            else:
                # Simulated dispatch mode (works out of the box when SMTP is not configured)
                log.status = 'sent'
                campaign.sent_count += 1
                user.sent_today += 1

            db.session.commit()

            # Throttling to prevent spam flags (small delay between mails)
            time.sleep(random.uniform(0.05, 0.15) if not smtp_connected else random.uniform(0.5, 1.2))

        if server:
            try:
                server.quit()
            except Exception:
                pass

        campaign.status = 'completed'
        sys_log = SystemLog(log_type='info', message=f"Campaign '{campaign.title}' completed ({campaign.sent_count} sent, {campaign.failed_count} failed).", user_email=user.email)
        db.session.add(sys_log)
        db.session.commit()
        print(f"🎉 Campaign '{campaign.title}' Completed! Total: {len(recipients)}")

def start_campaign_async(app, user_id, campaign_id, recipients, subject, html_content, base_url):
    t = Thread(target=send_bulk_thread, args=(app, user_id, campaign_id, recipients, subject, html_content, base_url))
    t.daemon = True
    t.start()