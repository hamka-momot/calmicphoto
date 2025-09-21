# PhotoVault Email Service
# Reference: blueprint:replitmail integration

from flask import current_app, url_for
from .replitmail import send_email
import logging

logger = logging.getLogger(__name__)

def send_family_vault_invitation(invitation, vault, invited_by_user):
    """
    Send family vault invitation email
    
    Args:
        invitation: VaultInvitation object
        vault: FamilyVault object
        invited_by_user: User object who sent the invitation
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Generate invitation URL
        invitation_url = url_for(
            'family.accept_invitation', 
            token=invitation.invitation_token, 
            _external=True
        )
        
        # Email subject
        subject = f"You're invited to join '{vault.name}' on PhotoVault"
        
        # Email content (plain text)
        text_content = f"""Hello!

{invited_by_user.username} has invited you to join the family vault "{vault.name}" on PhotoVault.

Vault Details:
- Name: {vault.name}
- Description: {vault.description}
- Your Role: {invitation.role.title()}

To accept this invitation, click the link below:
{invitation_url}

This invitation will expire on {invitation.expires_at.strftime('%B %d, %Y at %I:%M %p')}.

PhotoVault is a secure platform for sharing and managing family photos. If you don't have an account yet, you'll be guided through a quick registration process.

If you did not expect this invitation, you can safely ignore this email.

Best regards,
The PhotoVault Team
"""

        # Email content (HTML)
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>PhotoVault Family Vault Invitation</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background-color: #f8f9fa; padding: 30px; border-radius: 0 0 8px 8px; }}
        .vault-details {{ background-color: white; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .button {{ display: inline-block; background-color: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; color: #666; margin-top: 30px; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📸 PhotoVault Invitation</h1>
        </div>
        <div class="content">
            <h2>You're invited to join a family vault!</h2>
            
            <p><strong>{invited_by_user.username}</strong> has invited you to join their family vault on PhotoVault.</p>
            
            <div class="vault-details">
                <h3>📁 {vault.name}</h3>
                <p><strong>Description:</strong> {vault.description}</p>
                <p><strong>Your Role:</strong> {invitation.role.title()}</p>
                <p><strong>Invited By:</strong> {invited_by_user.username}</p>
            </div>
            
            <p>PhotoVault is a secure platform for sharing and managing family photos. Click the button below to accept this invitation:</p>
            
            <a href="{invitation_url}" class="button">Accept Invitation</a>
            
            <p><small>This invitation will expire on <strong>{invitation.expires_at.strftime('%B %d, %Y at %I:%M %p')}</strong>.</small></p>
            
            <p>If you don't have a PhotoVault account yet, you'll be guided through a quick registration process.</p>
        </div>
        <div class="footer">
            <p>If you did not expect this invitation, you can safely ignore this email.</p>
            <p>© 2025 PhotoVault by Calmic Sdn Bhd. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""
        
        # Send email using Replit Mail service
        result = send_email(
            to=invitation.email,
            subject=subject,
            text=text_content,
            html=html_content
        )
        
        logger.info(f"Family vault invitation email sent to {invitation.email} for vault {vault.name}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send family vault invitation email to {invitation.email}: {str(e)}")
        return False

def send_password_reset_email(user, token):
    """
    Send password reset email using Replit Mail service
    
    Args:
        user: User object
        token: Password reset token
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Generate reset URL
        reset_url = url_for('auth.reset_password', token=token, _external=True)
        
        # Email subject
        subject = "PhotoVault - Password Reset Request"
        
        # Email content (plain text)
        text_content = f"""Hello {user.username},

You have requested a password reset for your PhotoVault account.

Click the link below to reset your password:
{reset_url}

This link will expire in 1 hour.

If you did not request this password reset, please ignore this email.

Best regards,
PhotoVault Team
"""
        
        # Email content (HTML)
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>PhotoVault Password Reset</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background-color: #f8f9fa; padding: 30px; border-radius: 0 0 8px 8px; }}
        .button {{ display: inline-block; background-color: #dc3545; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; color: #666; margin-top: 30px; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 Password Reset</h1>
        </div>
        <div class="content">
            <h2>Hello {user.username},</h2>
            
            <p>You have requested a password reset for your PhotoVault account.</p>
            
            <p>Click the button below to reset your password:</p>
            
            <a href="{reset_url}" class="button">Reset Password</a>
            
            <p><small>This link will expire in <strong>1 hour</strong>.</small></p>
            
            <p>If you did not request this password reset, please ignore this email.</p>
        </div>
        <div class="footer">
            <p>© 2025 PhotoVault by Calmic Sdn Bhd. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""
        
        # Send email using Replit Mail service
        result = send_email(
            to=user.email,
            subject=subject,
            text=text_content,
            html=html_content
        )
        
        logger.info(f"Password reset email sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send password reset email to {user.email}: {str(e)}")
        return False