import random

# AI Copilot Module for ProMail System
TONE_TEMPLATES = {
    "professional": [
        "Dear {{name}},\n\nI hope this email finds you well. I am reaching out regarding {prompt}. We are committed to providing top-tier solutions for {company}.\n\nPlease let us know your convenient time for a brief discussion.\n\nBest regards,\n{sender}",
        "Hello {{name}},\n\nRegarding {prompt}, we have prepared a tailored proposition for {company}. Our goal is to streamline your workflows and maximize efficiency.\n\nFeel free to review the attached outline and share your feedback.\n\nSincerely,\n{sender}"
    ],
    "sales": [
        "Hi {{name}}! 🚀\n\nAre you looking to scale {company}'s growth with minimal effort? Regarding {prompt}, we have an exclusive offer designed specifically for leaders like you.\n\n👉 Click here to explore how we can boost your ROI by up to 40% this month.\n\nBest,\n{sender}",
        "Hey {{name}},\n\nQuick question: how is {company} currently handling {prompt}? We’ve recently helped over 200+ companies automate this process effortlessly.\n\nLet’s jump on a quick 5-minute call this week!\n\nCheers,\n{sender}"
    ],
    "friendly": [
        "Hey {{name}}!\n\nHope you're having a fantastic week. I wanted to drop a quick line about {prompt}.\n\nIt would be awesome to connect and get your thoughts on this for {company}.\n\nCatch up soon,\n{sender}",
        "Hi {{name}},\n\nJust checking in! I was thinking about {prompt} and thought it might be super useful for you and the team at {company}.\n\nLet me know what you think!\n\nWarmly,\n{sender}"
    ],
    "urgent": [
        "URGENT: Important Notice Regarding {prompt}\n\nDear {{name}},\n\nThis is an urgent follow-up regarding {prompt} for {company}. Immediate action is recommended to ensure seamless continuity.\n\nPlease reply to this email at your earliest convenience.\n\nRegards,\n{sender}"
    ]
}

SUBJECT_TEMPLATES = [
    "Important Update regarding {prompt}",
    "Exclusive Proposal for {{name}} at {company}",
    "Quick Question about {prompt}",
    "Action Required: {prompt} Details inside",
    "Tailored Solution for {{company}} regarding {prompt}"
]

def generate_ai_email(prompt, tone='professional', sender_name='ProMail Team'):
    tone = tone.lower()
    templates = TONE_TEMPLATES.get(tone, TONE_TEMPLATES['professional'])
    chosen = random.choice(templates)
    
    clean_prompt = prompt if prompt else "our latest updates and offerings"
    content = chosen.format(prompt=clean_prompt, company="{{company}}", sender=sender_name)
    
    # Format as HTML paragraph
    paragraphs = content.split('\n\n')
    html_paragraphs = "".join([f"<p>{p.replace('\n', '<br>')}</p>" for p in paragraphs])
    return html_paragraphs

def generate_ai_subject(prompt):
    clean_prompt = prompt if prompt else "New Announcement"
    template = random.choice(SUBJECT_TEMPLATES)
    return template.format(prompt=clean_prompt, company="{{company}}")

def improve_ai_text(text):
    if not text:
        return "<p>Hello {{name}},<br>Thank you for reaching out to us. We look forward to connecting!</p>"
    
    # Clean up and add polish
    return f"<div style='font-family: Arial, sans-serif; line-height: 1.6; color: #333;'>{text}</div>"
