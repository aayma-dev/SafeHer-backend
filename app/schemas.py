from uuid import UUID  
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
import re
from typing import Optional, List
from uuid import UUID
from enum import Enum

# Replace the UserCreate class with this (no confirm_password, username removed)
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def password_strength(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

# Replace the UserLogin class with this (email only)
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    role: str
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None
    username: Optional[str] = None

class EmailVerification(BaseModel):
    token: str

class ForgotPassword(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str
    
    @validator('new_password')
    def password_strength(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v
    
    # Add these after your existing code (before the last closing bracket if any)
class ReportCategory(str, Enum):
    HARASSMENT = "Harassment"
    STALKING = "Stalking / Following"
    PHYSICAL_ASSAULT = "Physical Assault"
    UNSAFE_AREA = "Unsafe Area"
    VERBAL_ABUSE = "Verbal Abuse"
    OTHER = "Other"

class ReportStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    RESOLVED = "resolved"

class ReportCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=20, max_length=2000)
    category: ReportCategory
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    address: Optional[str] = Field(None, max_length=500)
    is_anonymous: bool = True

class ReportUpdate(BaseModel):
    status: Optional[ReportStatus] = None
    title: Optional[str] = None
    description: Optional[str] = None

class ReportResponse(BaseModel):
    id: UUID
    title: str
    description: str
    category: ReportCategory
    latitude: Optional[float]
    longitude: Optional[float]
    address: Optional[str]
    status: ReportStatus
    is_anonymous: bool
    user_id: Optional[UUID]
    image_urls: List[str]
    upvotes: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ReportListResponse(BaseModel):
    total: int
    page: int
    per_page: int
    reports: List[ReportResponse]