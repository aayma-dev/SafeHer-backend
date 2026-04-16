from fastapi import APIRouter, Depends, HTTPException, status, Query, Form, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2

from app.database import get_db
from app.models import Report, User, ReportCategory, ReportStatus
from app.schemas import (
    ReportResponse, ReportUpdate, 
    ReportListResponse, ReportStatus as ReportStatusEnum
)
from app.dependencies import get_current_user_optional, get_current_admin_user

router = APIRouter(prefix="/api/reports", tags=["Reports"])

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points in km using Haversine formula"""
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    title: str = Form(..., min_length=3, max_length=200),
    description: str = Form(..., min_length=20, max_length=2000),
    category: ReportCategory = Form(...),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    address: Optional[str] = Form(None),
    is_anonymous: bool = Form(True),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit a new incident report.
    - Can be anonymous (no login required) or authenticated
    - Title and description are required
    """
    
    report = Report(
        title=title.strip(),
        description=description.strip(),
        category=category,
        latitude=latitude,
        longitude=longitude,
        address=address.strip() if address else None,
        is_anonymous=is_anonymous,
        user_id=None if is_anonymous or not current_user else current_user.id,
        status=ReportStatus.PENDING
    )
    
    db.add(report)
    await db.commit()
    await db.refresh(report)
    
    return report

@router.get("/", response_model=ReportListResponse)
async def get_reports(
    category: Optional[ReportCategory] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get list of approved reports with filters."""
    
    query = select(Report).where(Report.status == ReportStatus.APPROVED)
    
    if category:
        query = query.where(Report.category == category)
    
    count_query = select(func.count()).select_from(Report).where(Report.status == ReportStatus.APPROVED)
    if category:
        count_query = count_query.where(Report.category == category)
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    query = query.order_by(desc(Report.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    reports = result.scalars().all()
    
    return ReportListResponse(
        total=total or 0,
        page=(skip // limit) + 1 if limit > 0 else 1,
        per_page=limit,
        reports=reports
    )

@router.get("/my", response_model=List[ReportResponse])
async def get_my_reports(
    current_user: User = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """Get reports submitted by the authenticated user."""
    
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    query = select(Report).where(Report.user_id == current_user.id).order_by(desc(Report.created_at))
    result = await db.execute(query)
    reports = result.scalars().all()
    
    return reports

@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a single report by ID."""
    
    query = select(Report).where(Report.id == report_id)
    result = await db.execute(query)
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    if report.status != ReportStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    return report

@router.patch("/{report_id}/status", response_model=ReportResponse)
async def update_report_status(
    report_id: UUID,
    status_update: ReportUpdate,
    admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Update report status (Admin only)."""
    
    query = select(Report).where(Report.id == report_id)
    result = await db.execute(query)
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    if status_update.status:
        report.status = status_update.status
        report.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(report)
    
    return report

@router.post("/{report_id}/upvote", response_model=ReportResponse)
async def upvote_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Upvote a report."""
    
    query = select(Report).where(Report.id == report_id)
    result = await db.execute(query)
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    report.upvotes += 1
    await db.commit()
    await db.refresh(report)
    
    return report