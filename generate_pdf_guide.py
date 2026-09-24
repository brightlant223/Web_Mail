import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

def build_pdf():
    pdf_path = "D:\\code folder\\email_system\\email_system\\ProMail_User_and_Admin_Guide.pdf"
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom Color Palette
    PRIMARY_COLOR = colors.HexColor("#4F46E5")   # Indigo
    SECONDARY_COLOR = colors.HexColor("#0F172A") # Deep Slate
    ACCENT_COLOR = colors.HexColor("#8B5CF6")    # Purple
    SUCCESS_COLOR = colors.HexColor("#10B981")   # Emerald Green
    WARNING_COLOR = colors.HexColor("#F59E0B")   # Amber
    TEXT_DARK = colors.HexColor("#1E293B")       # Dark Charcoal
    BG_LIGHT = colors.HexColor("#F8FAFC")        # Soft Slate Background

    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=PRIMARY_COLOR,
        alignment=TA_LEFT,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=TEXT_DARK,
        alignment=TA_LEFT,
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=SECONDARY_COLOR,
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=TEXT_DARK,
        alignment=TA_LEFT,
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    story = []

    # --- COVER / HEADER ---
    story.append(Paragraph("Brightlant Webmail Platform", title_style))
    story.append(Paragraph("<b>Super Simple Basic to Advanced User & Administrator Guidelines</b>", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY_COLOR, spaceAfter=12))

    # --- OVERVIEW TABLE ---
    overview_data = [
        [Paragraph("<b>System Name:</b>", body_style), Paragraph("Brightlant Corporate Webmail Suite", body_style)],
        [Paragraph("<b>Target Domain:</b>", body_style), Paragraph("brightlant.com (Corporate Employee Mailboxes)", body_style)],
        [Paragraph("<b>Core Features:</b>", body_style), Paragraph("Webmail Inbox, Live Sound Alerts, AI Copilot, Incoming Test Simulator", body_style)],
        [Paragraph("<b>Local Web Server:</b>", body_style), Paragraph("<u>http://127.0.0.1:5000</u>", body_style)]
    ]
    t_overview = Table(overview_data, colWidths=[120, 420])
    t_overview.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    story.append(t_overview)
    story.append(Spacer(1, 10))

    # --- SECTION 1: BASIC USER STEP-BY-STEP GUIDE ---
    story.append(Paragraph("1. Simple 4-Step Basic User Guide (शुरुआती यूजर गाइड)", h1_style))
    story.append(Paragraph("Aasan bhasha me Brightlant Webmail use karne ke 4 saral steps:", body_style))
    
    basic_steps = [
        ["Step", "Action Name", "Instructions (kaise karein)"],
        ["Step 1", "Login (लॉगिन)", "Browser me http://127.0.0.1:5000 kholein. Email (shaswat@brightlant.com) aur Password (user123) daal kar Sign In dabayein."],
        ["Step 2", "Send Mail (ईमेल भेजें)", "Compose New Mail par click karein. To me recipient email, Subject, aur Message type karke Send Email button dabayein."],
        ["Step 3", "Receive Mail (ईमेल प्राप्त करें)", "Inbox me saare mails milenge. Naya email aate hi Web Audio Chime Sound aur screen notification alert aayega."],
        ["Step 4", "Test Mail (टेस्ट करें)", "Inbox page par top me 'Receive Mail Test' button dabayein. Kisi bhi external sender se instant test mail receive karke dekhein."]
    ]
    t_basic = Table(basic_steps, colWidths=[60, 110, 370])
    t_basic.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY_COLOR),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    for i in range(1, len(basic_steps)):
        t_basic._cellvalues[i][0] = Paragraph(f"<b>{basic_steps[i][0]}</b>", body_style)
        t_basic._cellvalues[i][1] = Paragraph(f"<b>{basic_steps[i][1]}</b>", body_style)
        t_basic._cellvalues[i][2] = Paragraph(basic_steps[i][2], body_style)
    story.append(t_basic)
    story.append(Spacer(1, 12))

    # --- SECTION 2: MOBILE & OUTLOOK SETUP ---
    story.append(Paragraph("2. Mobile & Outlook Setup Instructions (मोबाइल और आउटलुक सेटअप)", h1_style))
    story.append(Paragraph("• <b>Android / iPhone Gmail App:</b> Settings -> Add Account -> Other (IMAP). Email: your_name@brightlant.com. Incoming IMAP: mail.brightlant.com (Port 993). Outgoing SMTP: mail.brightlant.com (Port 587).", bullet_style))
    story.append(Paragraph("• <b>Microsoft Outlook 365:</b> File -> Add Account -> Manual Setup -> IMAP. Type Server Host & Credentials and connect!", bullet_style))
    story.append(Spacer(1, 10))

    # --- SECTION 3: ADMINISTRATOR OPERATIONS ---
    story.append(Paragraph("3. Administrator Operations (/admin)", h1_style))
    story.append(Paragraph("• <b>User Creation (/admin/users):</b> Create employee accounts like shaswat@brightlant.com with daily send limits.", bullet_style))
    story.append(Paragraph("• <b>SMTP Setup (/admin/smtp):</b> Connect active Gmail App Password, SES, or cPanel SMTP relay for live internet email delivery.", bullet_style))
    story.append(Paragraph("• <b>DNS Inspector (/admin/dns):</b> Check SPF, DKIM, and DMARC DNS records for brightlant.com domain.", bullet_style))

    doc.build(story)
    print("PDF Build Successful:", pdf_path)

if __name__ == '__main__':
    build_pdf()
