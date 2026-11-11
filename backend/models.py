"""Database models."""
import json
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    text = db.Column(db.Text, nullable=False)
    result_json = db.Column(db.Text, nullable=False)   # resume analysis
    match_json = db.Column(db.Text)                    # job match (optional)
    match_score = db.Column(db.Float)

    def to_dict(self, full=True):
        d = {"id": self.id, "filename": self.filename,
             "created_at": self.created_at.isoformat(), "match_score": self.match_score}
        if full:
            d.update(analysis=json.loads(self.result_json),
                     match=json.loads(self.match_json) if self.match_json else None,
                     text_preview=self.text[:1500])
        else:
            d["skill_count"] = len(json.loads(self.result_json).get("skills", []))
        return d
