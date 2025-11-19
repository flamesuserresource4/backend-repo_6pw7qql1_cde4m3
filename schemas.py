"""
Database Schemas for Ad Management

Each Pydantic model represents a MongoDB collection. The collection name is the
lowercased class name (e.g., Campaign -> "campaign").

These are used for validation and by the database helper utilities.
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import date

class Campaign(BaseModel):
    name: str = Field(..., description="Campaign name")
    brand: str = Field(..., description="Brand or client name")
    objective: Literal[
        "awareness",
        "traffic",
        "conversions",
        "leads",
        "engagement",
    ] = Field("awareness", description="Primary campaign objective")
    budget: float = Field(..., ge=0, description="Total budget in USD")
    start_date: date = Field(..., description="Campaign start date (YYYY-MM-DD)")
    end_date: date = Field(..., description="Campaign end date (YYYY-MM-DD)")
    status: Literal["draft", "active", "paused", "completed"] = Field(
        "draft", description="Lifecycle status"
    )

class Ad(BaseModel):
    campaign_id: str = Field(..., description="Associated campaign id")
    name: str = Field(..., description="Ad name")
    channel: Literal["facebook", "instagram", "google", "tiktok", "x", "linkedin", "other"] = Field(
        ..., description="Ad channel/platform"
    )
    format: Literal["image", "video", "carousel", "text", "html5", "other"] = Field(
        ..., description="Creative format"
    )
    headline: Optional[str] = Field(None, description="Primary headline")
    cta: Optional[str] = Field(None, description="Call to action text")
    target_audience: Optional[str] = Field(None, description="Audience notes/segment")
    status: Literal["active", "paused", "archived"] = Field("active", description="Ad status")

class Performance(BaseModel):
    ad_id: str = Field(..., description="Related ad id")
    date: date = Field(..., description="Metric date (YYYY-MM-DD)")
    impressions: int = Field(0, ge=0)
    clicks: int = Field(0, ge=0)
    spend: float = Field(0, ge=0, description="Spend in USD")
