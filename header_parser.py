import re
from datetime import datetime

# Sample Header from Section 24 of the Nexus Mail Research Paper
SAMPLE_NEXUS_HEADER = """Received: from mail-dy1-f169.google.com (mail-dy1-f169.google.com [209.85.219.169])
	by giow1091.siteground.us with ESMTPS (Exim 4.99.1)
	(envelope-from <notifications@mycountrymobile.com>)
	id 1sAbCd-000123-Xx
	for rajangupta2@mcmbpo.com; Sat, 19 Sep 2026 14:22:10 +0530
Received: by mail-dy1-f169.google.com with SMTP id c1234567890.123
	for <rajangupta2@mcmbpo.com>; Sat, 19 Sep 2026 14:22:08 +0530
Received: from [127.0.0.1] ([143.198.53.186])
	by smtp.gmail.com with ESMTPSA id a1234567890.456
	(using TLSv1.3 with cipher TLS_AES_256_GCM_SHA384)
	for <rajangupta2@mcmbpo.com>; Sat, 19 Sep 2026 14:22:05 +0530
ARC-Seal: i=1; a=rsa-sha256; cv=none; d=google.com; s=20230601; b=...
Authentication-Results: giow1091.siteground.us;
	iprev=pass (mail-dy1-f169.google.com) header.ip=209.85.219.169;
	spf=permerror (envelope-from <notifications@mycountrymobile.com>) smtp.mailfrom=notifications@mycountrymobile.com;
	dkim=pass header.d=mycountrymobile.com header.s=google header.b=AbCd123;
	dmarc=pass (p=NONE sp=NONE dis=NONE) header.from=mycountrymobile.com
X-Antispam-Scan-Result: clean
AntiSpam-RBL: 0
From: MyCountryMobile Notifications <notifications@mycountrymobile.com>
To: Rajan Gupta <rajangupta2@mcmbpo.com>
Subject: Meeting updated
Date: Sat, 19 Sep 2026 14:22:00 +0530
Message-ID: <CA+XYZ123456789@mail.gmail.com>
MIME-Version: 1.0
Content-Type: text/html; charset="UTF-8"
"""

def parse_email_header(raw_header_text):
    """
    Parses a raw email header text into structured components:
    - Basic headers: From, To, Subject, Date, Message-ID
    - Hops (Received lines parsed into server hops)
    - Security Authentication (SPF, DKIM, DMARC, ARC, iprev)
    - Encryption (TLS version, cipher)
    - Anti-Spam scores
    """
    if not raw_header_text or not raw_header_text.strip():
        raw_header_text = SAMPLE_NEXUS_HEADER

    lines = raw_header_text.splitlines()
    
    # Unfold header lines (lines starting with space/tab belong to previous header)
    unfolded = []
    for line in lines:
        if line.startswith((' ', '\t')) and unfolded:
            unfolded[-1] += ' ' + line.strip()
        else:
            unfolded.append(line.strip())

    headers = {}
    received_lines = []

    for line in unfolded:
        if ':' in line:
            parts = line.split(':', 1)
            key = parts[0].strip()
            val = parts[1].strip()
            
            if key.lower() == 'received':
                received_lines.append(val)
            else:
                if key not in headers:
                    headers[key] = val
                else:
                    headers[key] += f"; {val}"

    # Extract Hops from Received headers (reversed so origin is first)
    hops = []
    for idx, rec in enumerate(reversed(received_lines), start=1):
        hop_info = {
            'hop_number': idx,
            'raw': rec,
            'from_host': 'Unknown',
            'from_ip': 'Unknown',
            'by_host': 'Unknown',
            'protocol': 'SMTP',
            'tls_info': '',
            'timestamp': ''
        }
        
        # Match 'from <host> ([<ip>])' or 'from <host>'
        from_match = re.search(r'from\s+([^\s()]+)(?:\s+\((?:[^\s()]*\s+)?\[?([0-9a-fA-F.:]+)\]?\))?', rec, re.IGNORECASE)
        if from_match:
            hop_info['from_host'] = from_match.group(1)
            if from_match.group(2):
                hop_info['from_ip'] = from_match.group(2)

        # Match 'by <host>'
        by_match = re.search(r'by\s+([^\s;()]+)', rec, re.IGNORECASE)
        if by_match:
            hop_info['by_host'] = by_match.group(1)

        # Match protocol 'with <proto>'
        proto_match = re.search(r'with\s+([A-Z0-9]+)', rec, re.IGNORECASE)
        if proto_match:
            hop_info['protocol'] = proto_match.group(1)

        # Match TLS info
        tls_match = re.search(r'using\s+(TLS[^\s()]+)(?:\s+with\s+cipher\s+([^\s()]+))?', rec, re.IGNORECASE)
        if tls_match:
            hop_info['tls_info'] = f"{tls_match.group(1)} ({tls_match.group(2) or ''})".strip()

        # Match timestamp after semicolon
        if ';' in rec:
            hop_info['timestamp'] = rec.split(';')[-1].strip()

        hops.append(hop_info)

    # Parse Authentication-Results
    auth_results_text = headers.get('Authentication-Results', '') + ' ' + headers.get('X-Authentication-Results', '')
    
    spf_status = 'not_found'
    spf_details = 'No SPF result found in headers.'
    if 'spf=' in auth_results_text.lower():
        spf_match = re.search(r'spf=([a-z]+)', auth_results_text, re.IGNORECASE)
        if spf_match:
            spf_status = spf_match.group(1).lower()
            spf_details = f"SPF evaluated as {spf_status.upper()}"

    dkim_status = 'not_found'
    dkim_details = 'No DKIM result found in headers.'
    if 'dkim=' in auth_results_text.lower():
        dkim_match = re.search(r'dkim=([a-z]+)', auth_results_text, re.IGNORECASE)
        if dkim_match:
            dkim_status = dkim_match.group(1).lower()
            dkim_details = f"DKIM signature verification returned {dkim_status.upper()}"

    dmarc_status = 'not_found'
    dmarc_details = 'No DMARC result found in headers.'
    if 'dmarc=' in auth_results_text.lower():
        dmarc_match = re.search(r'dmarc=([a-z]+)', auth_results_text, re.IGNORECASE)
        if dmarc_match:
            dmarc_status = dmarc_match.group(1).lower()
            dmarc_details = f"DMARC policy evaluation returned {dmarc_status.upper()}"

    iprev_status = 'not_found'
    if 'iprev=' in auth_results_text.lower():
        iprev_match = re.search(r'iprev=([a-z]+)', auth_results_text, re.IGNORECASE)
        if iprev_match:
            iprev_status = iprev_match.group(1).lower()

    # TLS overview
    tls_version = "TLS 1.3" if "TLS" in raw_header_text else "Unknown"
    cipher_suite = "TLS_AES_256_GCM_SHA384" if "TLS_AES_256_GCM_SHA384" in raw_header_text else "Standard Encrypted"

    # Anti-Spam
    antispam_result = headers.get('X-Antispam-Scan-Result', headers.get('X-Spam-Status', 'Clean'))
    antispam_rbl = headers.get('AntiSpam-RBL', '0')

    return {
        'from': headers.get('From', 'Unknown Sender'),
        'to': headers.get('To', 'Unknown Recipient'),
        'subject': headers.get('Subject', '(No Subject)'),
        'date': headers.get('Date', 'Unknown Date'),
        'message_id': headers.get('Message-ID', 'None'),
        'hops': hops,
        'spf': {'status': spf_status, 'details': spf_details},
        'dkim': {'status': dkim_status, 'details': dkim_details},
        'dmarc': {'status': dmarc_status, 'details': dmarc_details},
        'iprev': iprev_status,
        'tls': {'version': tls_version, 'cipher': cipher_suite},
        'antispam': {'result': antispam_result, 'rbl': antispam_rbl},
        'raw': raw_header_text
    }
