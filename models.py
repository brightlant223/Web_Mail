from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, date

db = SQLAlchemy()

class Domain(db.Model):
    __tablename__ = 'domains'
    id = db.Column(db.Integer, primary_key=True)
    domain_name = db.Column(db.String(120), unique=True, nullable=False) # e.g. "mycompany.com"
    spf_record = db.Column(db.String(255), default="v=spf1 include:_spf.brightlant.com ~all")
    dkim_record = db.Column(db.String(255), default="v=DKIM1; k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC...")
    dmarc_record = db.Column(db.String(255), default="v=DMARC1; p=none; sp=none; pct=100")
    mx_record = db.Column(db.String(255), default="10 mail.brightlant.com")
    is_verified = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    users = db.relationship('User', backref='domain_rel', lazy=True)
    messages = db.relationship('Message', backref='domain_rel', lazy=True)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False) # e.g. rahul@mycompany.com
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user') # 'admin' ya 'user'
    domain_id = db.Column(db.Integer, db.ForeignKey('domains.id'), nullable=True)
    
    # Send Quota Features
    daily_limit = db.Column(db.Integer, default=500)
    sent_today = db.Column(db.Integer, default=0)
    last_sent_date = db.Column(db.Date, default=date.today)
    status = db.Column(db.String(20), default='active') # 'active', 'suspended'
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    campaigns = db.relationship('Campaign', backref='author', lazy=True)
    contacts = db.relationship('Contact', backref='user', lazy=True)
    templates = db.relationship('Template', backref='user', lazy=True)
    profile = db.relationship('UserProfile', backref='user', uselist=False, lazy=True)
    api_keys = db.relationship('ApiKey', backref='user', lazy=True)

    def can_send_mails(self, count):
        if self.last_sent_date < date.today():
            self.sent_today = 0
            self.last_sent_date = date.today()
            db.session.commit()
        return (self.sent_today + count) <= self.daily_limit

class UserProfile(db.Model):
    __tablename__ = 'user_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    phone = db.Column(db.String(30), nullable=True)
    department = db.Column(db.String(100), default='Sales & Marketing')
    bio = db.Column(db.Text, nullable=True)
    signature_html = db.Column(db.Text, default='<p>Best regards,<br><strong>ProMail User</strong></p>')
    theme_preference = db.Column(db.String(20), default='light')
    avatar = db.Column(db.String(255), nullable=True)  # relative static path e.g. uploads/avatars/x.png
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class ApiKey(db.Model):
    __tablename__ = 'api_keys'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    key_name = db.Column(db.String(100), nullable=False)
    key_value = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    domain_id = db.Column(db.Integer, db.ForeignKey('domains.id'), nullable=True)
    sender_name = db.Column(db.String(100), nullable=False)
    sender_email = db.Column(db.String(150), nullable=False)
    recipient_email = db.Column(db.String(150), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    body_html = db.Column(db.Text, nullable=False)
    folder = db.Column(db.String(20), default='inbox') # inbox, sent, draft, trash
    is_read = db.Column(db.Boolean, default=False)
    is_starred = db.Column(db.Boolean, default=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('messages.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    attachments = db.relationship('Attachment', backref='message', lazy=True, cascade="all, delete-orphan")

class Attachment(db.Model):
    __tablename__ = 'attachments'
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('messages.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, default=0) # bytes
    content_type = db.Column(db.String(100), default='application/octet-stream')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ResearchChecklist(db.Model):
    __tablename__ = 'research_checklists'
    id = db.Column(db.Integer, primary_key=True)
    phase_number = db.Column(db.Integer, nullable=False) # 1 to 6
    task_key = db.Column(db.String(100), unique=True, nullable=False)
    task_label = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100), default='General')
    is_completed = db.Column(db.Boolean, default=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class Campaign(db.Model):
    __tablename__ = 'campaigns'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(150), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=True)
    total_recipients = db.Column(db.Integer, default=0)
    sent_count = db.Column(db.Integer, default=0)
    failed_count = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), default='completed') # sending, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    email_logs = db.relationship('EmailLog', backref='campaign', lazy=True, cascade="all, delete-orphan")

class EmailLog(db.Model):
    __tablename__ = 'email_logs'
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'))
    recipient_email = db.Column(db.String(150), nullable=False)
    recipient_name = db.Column(db.String(150), nullable=True, default='User')
    status = db.Column(db.String(50), default='pending') # sent, failed, opened
    tracking_token = db.Column(db.String(64), unique=True, nullable=False)
    error_message = db.Column(db.Text, nullable=True)
    opened_at = db.Column(db.DateTime, nullable=True)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)

class Contact(db.Model):
    __tablename__ = 'contacts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    company = db.Column(db.String(100), nullable=True)
    tags = db.Column(db.String(100), default='VIP')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Template(db.Model):
    __tablename__ = 'templates'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='Newsletter')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SMTPSetting(db.Model):
    __tablename__ = 'smtp_settings'
    id = db.Column(db.Integer, primary_key=True)
    domain_id = db.Column(db.Integer, db.ForeignKey('domains.id'), nullable=True)
    smtp_host = db.Column(db.String(150), default='smtp.gmail.com')
    smtp_port = db.Column(db.Integer, default=587)
    smtp_user = db.Column(db.String(150), nullable=True)
    smtp_pass = db.Column(db.String(255), nullable=True)
    encryption = db.Column(db.String(20), default='tls') # tls, ssl, none
    sender_name = db.Column(db.String(100), default='ProMail Dispatcher')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SystemLog(db.Model):
    __tablename__ = 'system_logs'
    id = db.Column(db.Integer, primary_key=True)
    log_type = db.Column(db.String(50), default='info') # info, warning, error, auth
    message = db.Column(db.Text, nullable=False)
    user_email = db.Column(db.String(150), nullable=True)
    ip_address = db.Column(db.String(50), default='127.0.0.1')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)