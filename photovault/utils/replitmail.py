# PhotoVault Email Utility using Replit Mail Service
# Reference: blueprint:replitmail integration

import os
import json
import requests
from typing import List, Optional, Dict, Union

def get_auth_token() -> str:
    """Get authentication token for Replit mail service"""
    repl_identity = os.environ.get('REPL_IDENTITY')
    web_repl_renewal = os.environ.get('WEB_REPL_RENEWAL')
    
    if repl_identity:
        return f"repl {repl_identity}"
    elif web_repl_renewal:
        return f"depl {web_repl_renewal}"
    else:
        raise Exception("No authentication token found. Please set REPL_IDENTITY or ensure you're running in Replit environment.")

def send_email(
    to: Union[str, List[str]],
    subject: str,
    text: Optional[str] = None,
    html: Optional[str] = None,
    cc: Optional[Union[str, List[str]]] = None,
    attachments: Optional[List[Dict]] = None
) -> Dict:
    """
    Send email using Replit mail service
    
    Args:
        to: Recipient email address(es)
        subject: Email subject
        text: Plain text body (optional)
        html: HTML body (optional)
        cc: CC recipient email address(es) (optional)
        attachments: Email attachments (optional)
    
    Returns:
        Dict with response from mail service
    """
    auth_token = get_auth_token()
    
    # Prepare email payload
    payload = {
        "to": to,
        "subject": subject
    }
    
    if text:
        payload["text"] = text
    if html:
        payload["html"] = html
    if cc:
        payload["cc"] = cc
    if attachments:
        payload["attachments"] = attachments
    
    # Send email via Replit mail service
    response = requests.post(
        "https://connectors.replit.com/api/v2/mailer/send",
        headers={
            "Content-Type": "application/json",
            "X_REPLIT_TOKEN": auth_token,
        },
        json=payload
    )
    
    if not response.ok:
        try:
            error_data = response.json()
            error_message = error_data.get('message', 'Failed to send email')
        except:
            error_message = f"Failed to send email: HTTP {response.status_code}"
        raise Exception(error_message)
    
    return response.json()