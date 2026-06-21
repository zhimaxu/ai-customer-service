"""数据统计 API"""

from datetime import datetime, timedelta, timezone
from sqlalchemy import func
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.stats import (
    ChatTrendItem,
    SatisfactionDistribution,
    EfficiencyMetrics,
    StatsOverview,
)
from app.models.session import Session as SessionModel, Message
from app.models.analytics import RatingRecord, AgentEfficiencyLog

router = APIRouter(prefix="/stats", tags=["stats"])


def _get_trend_data(db: Session, period: str) -> list[dict]:
    """Get daily trend data for the specified period"""
    now = datetime.now(timezone.utc)
    if period == "day":
        start = now - timedelta(hours=24)
        group_by = func.date(SessionModel.created_at)
    elif period == "week":
        start = now - timedelta(days=7)
        group_by = func.date(SessionModel.created_at)
    else:  # month
        start = now - timedelta(days=30)
        group_by = func.date(SessionModel.created_at)

    query = (
        db.query(
            group_by.label("date"),
            func.count(SessionModel.id).label("total"),
            func.sum(func.if_(SessionModel.status == "active", 1, 0)).label("active"),
            func.sum(func.if_(SessionModel.status == "closed", 1, 0)).label("closed"),
        )
        .filter(SessionModel.created_at >= start)
        .group_by(group_by)
        .order_by(group_by)
        .all()
    )

    return [
        {"date": str(r.date), "total": r.total, "active": r.active or 0, "closed": r.closed or 0}
        for r in query
    ]


@router.get("/overview")
def get_overview(db: Session = Depends(get_db)):
    """获取数据概览"""
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    total_sessions = db.query(func.count(SessionModel.id)).scalar() or 0
    active_sessions = (
        db.query(func.count(SessionModel.id))
        .filter(SessionModel.status == "active")
        .scalar() or 0
    )
    closed_sessions = (
        db.query(func.count(SessionModel.id))
        .filter(SessionModel.status == "closed")
        .scalar() or 0
    )

    avg_sat = (
        db.query(func.avg(RatingRecord.score))
        .filter(RatingRecord.score.isnot(None))
        .scalar() or 0
    )

    total_messages = db.query(func.count(Message.id)).scalar() or 0

    return {
        "total_sessions": total_sessions,
        "active_sessions": active_sessions,
        "closed_sessions": closed_sessions,
        "avg_satisfaction": round(float(avg_sat), 2),
        "avg_first_response": 0.0,
        "resolution_rate": round((closed_sessions / total_sessions * 100) if total_sessions > 0 else 0, 2),
        "total_messages": total_messages,
    }


@router.get("/chat")
def get_chat_stats(
    period: str = Query("day", regex="^(day|week|month)$"),
    db: Session = Depends(get_db),
):
    """对话统计"""
    trend = _get_trend_data(db, period)
    return {
        "period": period,
        "trend": [ChatTrendItem(**t).model_dump() for t in trend],
    }


@router.get("/satisfaction")
def get_satisfaction_stats(db: Session = Depends(get_db)):
    """满意度统计"""
    # Average score
    avg_result = db.query(func.avg(RatingRecord.score)).scalar()
    avg_score = float(avg_result) if avg_result else 0.0

    # Distribution
    dist = {}
    for score in range(1, 6):
        count = (
            db.query(func.count(RatingRecord.id))
            .filter(RatingRecord.score == score)
            .scalar() or 0
        )
        dist[str(score)] = count

    return {
        "avg_score": round(avg_score, 2),
        "distribution": dist,
    }


@router.get("/efficiency")
def get_efficiency_stats(db: Session = Depends(get_db)):
    """效率统计"""
    total_sessions = db.query(func.count(SessionModel.id)).scalar() or 0
    total_messages = db.query(func.count(Message.id)).scalar() or 0
    closed_sessions = (
        db.query(func.count(SessionModel.id))
        .filter(SessionModel.status == "closed")
        .scalar() or 0
    )

    # From efficiency log if available
    avg_first = (
        db.query(func.avg(AgentEfficiencyLog.first_response_time))
        .scalar()
    )
    avg_response = (
        db.query(func.avg(AgentEfficiencyLog.avg_response_time))
        .scalar()
    )

    return {
        "avg_first_response_time": round(float(avg_first), 2) if avg_first else None,
        "avg_response_time": round(float(avg_response), 2) if avg_response else None,
        "resolution_rate": round((closed_sessions / total_sessions * 100) if total_sessions > 0 else 0, 2),
        "total_sessions": total_sessions,
        "total_messages": total_messages,
    }


@router.get("/all")
def get_all_stats(
    period: str = Query("day"),
    db: Session = Depends(get_db),
):
    """获取所有统计数据"""
    overview = get_overview(db)
    chat = get_chat_stats(period, db)
    satisfaction = get_satisfaction_stats(db)
    efficiency = get_efficiency_stats(db)

    return {
        "overview": overview,
        "trend": chat["trend"],
        "satisfaction": satisfaction,
        "efficiency": efficiency,
    }
