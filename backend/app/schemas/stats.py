"""数据统计 Schema"""

from pydantic import BaseModel
from typing import Optional


class ChatTrendItem(BaseModel):
    date: str
    total: int
    active: int
    closed: int


class SatisfactionDistribution(BaseModel):
    avg_score: float
    distribution: dict  # {1: count, 2: count, ..., 5: count}


class EfficiencyMetrics(BaseModel):
    avg_first_response_time: Optional[float]
    avg_response_time: Optional[float]
    resolution_rate: float
    total_sessions: int
    total_messages: int


class StatsOverview(BaseModel):
    total_sessions: int
    active_sessions: int
    closed_sessions: int
    avg_satisfaction: float
    avg_first_response: float
    resolution_rate: float


class StatsResponse(BaseModel):
    overview: StatsOverview
    trend: list[ChatTrendItem]
    satisfaction: SatisfactionDistribution
    efficiency: EfficiencyMetrics
