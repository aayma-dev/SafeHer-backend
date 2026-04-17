from fastapi import APIRouter, Depends, HTTPException, status, Query, Form, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
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
def create_report(
    title: str = Form(..., min_length=3, max_length=200),
    description: str = Form(..., min_length=20, max_length=2000),
    category: ReportCategory = Form(...),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    address: Optional[str] = Form(None),
    is_anonymous: bool = Form(True),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
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
    db.commit()
    db.refresh(report)
    
    return report

@router.get("/", response_model=ReportListResponse)
def get_reports(
    category: Optional[ReportCategory] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get list of approved reports with filters."""
    
    query = db.query(Report).filter(Report.status == ReportStatus.APPROVED)
    
    if category:
        query = query.filter(Report.category == category)
    
    total = query.count()
    
    reports = query.order_by(desc(Report.created_at)).offset(skip).limit(limit).all()
    
    return ReportListResponse(
        total=total or 0,
        page=(skip // limit) + 1 if limit > 0 else 1,
        per_page=limit,
        reports=reports
    )

@router.get("/my", response_model=List[ReportResponse])
def get_my_reports(
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Get reports submitted by the authenticated user."""
    
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    reports = db.query(Report).filter(Report.user_id == current_user.id).order_by(desc(Report.created_at)).all()
    
    return reports

@router.get("/nearby", response_model=ReportListResponse)
def get_nearby_reports(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(1.0, ge=0.1, le=50),
    category: Optional[ReportCategory] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get reports near a location using bounding box + distance calculation."""
    
    # Calculate bounding box
    lat_delta = radius_km / 111.0
    lng_delta = radius_km / (111.0 * abs(lat or 1))
    
    # Build query with bounding box
    query = db.query(Report).filter(
        and_(
            Report.status == ReportStatus.APPROVED,
            Report.latitude.between(lat - lat_delta, lat + lat_delta),
            Report.longitude.between(lng - lng_delta, lng + lng_delta)
        )
    )
    
    if category:
        query = query.filter(Report.category == category)
    
    reports = query.order_by(desc(Report.created_at)).limit(limit).all()
    
    # Filter by exact distance and add distance to response
    filtered_reports = []
    for report in reports:
        if report.latitude and report.longitude:
            distance = calculate_distance(lat, lng, report.latitude, report.longitude)
            if distance <= radius_km:
                report.distance_km = round(distance, 2)
                filtered_reports.append(report)
    
    return ReportListResponse(
        total=len(filtered_reports),
        page=1,
        per_page=limit,
        reports=filtered_reports
    )

@router.get("/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a single report by ID."""
    
    report = db.query(Report).filter(Report.id == report_id).first()
    
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
def update_report_status(
    report_id: UUID,
    status_update: ReportUpdate,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update report status (Admin only)."""
    
    report = db.query(Report).filter(Report.id == report_id).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    if status_update.status:
        report.status = status_update.status
        report.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(report)
    
    return report

@router.post("/{report_id}/upvote", response_model=ReportResponse)
def upvote_report(
    report_id: UUID,
    db: Session = Depends(get_db)
):
    """Upvote a report."""
    
    report = db.query(Report).filter(Report.id == report_id).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    report.upvotes += 1
    db.commit()
    db.refresh(report)
    
    return report