import secrets
from datetime import datetime, timedelta

def generate_verification_token() -> str:
    """Generate a secure email verification token"""
    return secrets.token_urlsafe(32)

def send_verification_email(to_email: str, username: str, verification_token: str):
    """Send email verification link (simplified - prints to console for now)"""
    verification_link = f"http://localhost:8000/api/auth/verify-email?token={verification_token}"
    
    print(f"\n{'='*60}")
    print(f"📧 EMAIL VERIFICATION")
    print(f"To: {to_email}")
    print(f"Hello {username},")
    print(f"Please verify your email by clicking: {verification_link}")
    print(f"{'='*60}\n")
    
    # Return True to simulate email sent
    return True