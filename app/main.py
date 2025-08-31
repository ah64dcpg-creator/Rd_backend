import os, json
from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from .database import init_db, get_db
from . import models

app = FastAPI(title="Raising Daisies – Backend", version="0.5.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ALLOW_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
def auth_ok(authorization: str | None):
    token = os.getenv("ADMIN_TOKEN")
    if not token: return True
    if not authorization or not authorization.startswith("Bearer "): raise HTTPException(status_code=401, detail="Missing or invalid token")
    if authorization.split(" ",1)[1] != token: raise HTTPException(status_code=403, detail="Forbidden")
    return True

@app.get('/health')
def health(): return {'ok': True, 'time': datetime.utcnow().isoformat()}

@app.get('/events')
def list_events(db: Session = Depends(get_db)):
    rows = db.query(models.Event).order_by(models.Event.starts_at.asc()).all()
    def to_out(e: models.Event):
        return {
            "id": e.id, "title": e.title, "description": e.description,
            "starts_at": e.starts_at, "ends_at": e.ends_at, "timezone": e.timezone,
            "format": e.format, "audience": e.audience, "language": e.language,
            "cost_min": e.cost_min, "cost_max": e.cost_max, "badges": e.badges, "verified": bool(e.verified),
            "organizer": {"name": e.organizer.name, "email": e.organizer.email, "verified": e.organizer.verified} if e.organizer else None,
            "venue": {"name": e.venue.name, "address": e.venue.address, "city": e.venue.city, "state": e.venue.state, "postal_code": e.venue.postal_code, "lat": e.venue.lat, "lng": e.venue.lng} if e.venue else None
        }
    return [to_out(x) for x in rows]

def upsert_event(db: Session, p: dict):
    from datetime import datetime
    from sqlalchemy import and_
    org=None
    if p.get("organizer_name"):
        org = db.query(models.Organizer).filter(models.Organizer.name==p["organizer_name"]).first()
        if not org:
            org = models.Organizer(name=p["organizer_name"], email=p.get("organizer_email"), verified=False)
            db.add(org); db.flush()
    ven=None
    if p.get("venue_name"):
        ven = db.query(models.Venue).filter(models.Venue.name==p["venue_name"], models.Venue.city==p.get("city")).first()
        if not ven:
            ven = models.Venue(name=p["venue_name"], address=p.get("address"), city=p.get("city"), state=p.get("state"), postal_code=p.get("postal_code"), lat=p.get("lat"), lng=p.get("lng"))
            db.add(ven); db.flush()
    starts_at = datetime.fromisoformat(str(p["starts_at"]).replace("Z","+00:00")) if isinstance(p["starts_at"], str) else p["starts_at"]
    q = db.query(models.Event).filter(models.Event.title==p["title"], models.Event.starts_at==starts_at)
    if p.get("city"): q = q.join(models.Venue, isouter=True).filter(models.Venue.city==p["city"])
    ex = q.first()
    if ex:
        ex.description = p.get("description") or ex.description
        ex.ends_at = p.get("ends_at") or ex.ends_at
        ex.format = p.get("format") or ex.format
        ex.audience = p.get("audience") or ex.audience
        ex.language = p.get("language") or ex.language
        ex.cost_min = p.get("cost_min") if p.get("cost_min") is not None else ex.cost_min
        ex.cost_max = p.get("cost_max") if p.get("cost_max") is not None else ex.cost_max
        ex.organizer_id = org.id if org else ex.organizer_id
        ex.venue_id = ven.id if ven else ex.venue_id
        ex.verified = True
        db.commit(); return ex.id
    else:
        ev = models.Event(
            title=p["title"], description=p.get("description"),
            starts_at=starts_at, ends_at=p.get("ends_at"),
            timezone=p.get("timezone"), format=p.get("format"),
            audience=p.get("audience"), language=p.get("language"),
            cost_min=p.get("cost_min"), cost_max=p.get("cost_max"), badges=p.get("badges"),
            organizer_id=org.id if org else None, venue_id=ven.id if ven else None,
            source=p.get("source"), source_id=p.get("source_id"), verified=True
        )
        db.add(ev); db.commit(); db.refresh(ev); return ev.id

@app.post('/admin/ingest_bulk')
def ingest_bulk(body: dict, db: Session = Depends(get_db), authorization: str | None = Header(None)):
    auth_ok(authorization)
    items = body.get("events") or []
    ids=[]; count=0
    for p in items:
        try:
            ids.append(upsert_event(db,p)); count+=1
        except Exception: pass
    return {"ok": True, "ingested": count, "ids": ids}
