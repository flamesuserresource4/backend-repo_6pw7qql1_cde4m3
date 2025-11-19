import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import db, create_document, get_documents

app = FastAPI(title="Ad Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CampaignCreate(BaseModel):
    name: str
    brand: str
    objective: str
    budget: float
    start_date: str
    end_date: str


@app.get("/")
def read_root():
    return {"message": "Ad Management Backend Ready"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response


# Campaign endpoints
@app.post("/api/campaigns")
def create_campaign(payload: CampaignCreate):
    try:
        from schemas import Campaign  # validate using schema
        # Coerce to schema for validation
        schema_obj = Campaign(
            name=payload.name,
            brand=payload.brand,
            objective=payload.objective,  # enum validated
            budget=payload.budget,
            start_date=datetime.fromisoformat(payload.start_date).date(),
            end_date=datetime.fromisoformat(payload.end_date).date(),
            status="active",
        )
        campaign_id = create_document("campaign", schema_obj)
        return {"id": campaign_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/campaigns")
def list_campaigns():
    try:
        items = get_documents("campaign", {}, limit=100)
        # Convert ObjectId and dates
        for it in items:
            it["_id"] = str(it.get("_id"))
            for k, v in list(it.items()):
                if hasattr(v, "isoformat"):
                    it[k] = v.isoformat()
        return {"items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class AdCreate(BaseModel):
    campaign_id: str
    name: str
    channel: str
    format: str
    headline: Optional[str] = None
    cta: Optional[str] = None


@app.post("/api/ads")
def create_ad(payload: AdCreate):
    try:
        from schemas import Ad
        schema_obj = Ad(
            campaign_id=payload.campaign_id,
            name=payload.name,
            channel=payload.channel,
            format=payload.format,
            headline=payload.headline,
            cta=payload.cta,
            target_audience=None,
            status="active",
        )
        ad_id = create_document("ad", schema_obj)
        return {"id": ad_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/ads")
def list_ads(campaign_id: Optional[str] = None):
    try:
        query = {"campaign_id": campaign_id} if campaign_id else {}
        items = get_documents("ad", query, limit=200)
        for it in items:
            it["_id"] = str(it.get("_id"))
            for k, v in list(it.items()):
                if hasattr(v, "isoformat"):
                    it[k] = v.isoformat()
        return {"items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
