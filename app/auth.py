from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.config import settings
from app.models import User, UserSession
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt  # ✅ Return just the token string

def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

def store_user_session(db: Session, user_id: str, token_jti: str, user_agent: str = None, ip_address: str = None):
    """Store user session in database"""
    session = UserSession(
        user_id=user_id,
        token_jti=token_jti,
        user_agent=user_agent,
        ip_address=ip_address,
        expires_at=datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    db.add(session)
    db.commit()
    return session

def revoke_user_session(db: Session, token_jti: str):
    """Revoke a user session (logout)"""
    session = db.query(UserSession).filter(UserSession.token_jti == token_jti).first()
    if session:
        session.is_revoked = True
        db.commit()
        return True
    return False

def is_token_revoked(db: Session, token_jti: str) -> bool:
    """Check if a token has been revoked"""
    session = db.query(UserSession).filter(UserSession.token_jti == token_jti).first()
    return session is None or session.is_revoked