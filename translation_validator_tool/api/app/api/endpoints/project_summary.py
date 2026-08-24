import json
from datetime import date, datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db


router = APIRouter()

SUMMARY_PATH = Path(__file__).resolve().parents[3] / "data" / "project_summary.json"
PROJECT_TIMELINE_YEAR = 2026


def _official_timeline():
    return [
        {"label": "Inicio del proyecto", "date": date(PROJECT_TIMELINE_YEAR, 3, 20).isoformat()},
        {"label": "Traducción", "date": date(PROJECT_TIMELINE_YEAR, 4, 22).isoformat()},
        {"label": "Validación", "date": date(PROJECT_TIMELINE_YEAR, 7, 6).isoformat()},
        {"label": "Finalización", "date": date.today().isoformat()},
    ]


def _apply_official_timeline(summary):
    timeline = _official_timeline()
    summary["timeline"] = timeline
    summary.setdefault("stats", {})["months"] = _months_between(
        date.fromisoformat(timeline[0]["date"]),
        date.fromisoformat(timeline[-1]["date"]),
    )
    return summary


def _months_between(start, end):
    if not start or not end:
        return 0
    return max(1, (end.year - start.year) * 12 + end.month - start.month + 1)


def _participant(row):
    translations = int(row.traducciones or 0)
    validations = int(row.validaciones or 0)
    return {
        "name": row.nombre_completo or "Participante",
        "translations": translations,
        "validations": validations,
        "total": translations + validations,
    }


def _leader(row, key):
    return {
        "name": row.nombre_completo or "Participante",
        "count": int(getattr(row, key) or 0),
    }


def _build_summary(db: Session):
    totals = db.execute(text("""
        WITH participant_ids AS (
            SELECT user_id FROM annotation_translations
            UNION
            SELECT user_id FROM annotation_validations WHERE status = 'completed'
        )
        SELECT
            (SELECT COUNT(*) FROM participant_ids) AS participantes,
            (SELECT COUNT(*) FROM annotation_translations) AS traducciones,
            (SELECT COUNT(*) FROM annotation_validations WHERE status = 'completed') AS validaciones;
    """)).one()

    top_translators = db.execute(text("""
        SELECT u.nombre_completo, COUNT(*) AS traducciones
        FROM annotation_translations at
        JOIN users u ON u.id = at.user_id
        GROUP BY u.id, u.nombre_completo
        ORDER BY traducciones DESC, u.nombre_completo ASC
        LIMIT 5;
    """)).fetchall()

    top_validators = db.execute(text("""
        SELECT u.nombre_completo, COUNT(*) AS validaciones
        FROM annotation_validations av
        JOIN users u ON u.id = av.user_id
        WHERE av.status = 'completed'
        GROUP BY u.id, u.nombre_completo
        ORDER BY validaciones DESC, u.nombre_completo ASC
        LIMIT 5;
    """)).fetchall()

    participants = db.execute(text("""
        WITH translation_stats AS (
            SELECT user_id, COUNT(*) AS traducciones
            FROM annotation_translations
            GROUP BY user_id
        ),
        validation_stats AS (
            SELECT user_id, COUNT(*) AS validaciones
            FROM annotation_validations
            WHERE status = 'completed'
            GROUP BY user_id
        )
        SELECT
            u.nombre_completo,
            COALESCE(t.traducciones, 0) AS traducciones,
            COALESCE(v.validaciones, 0) AS validaciones
        FROM users u
        LEFT JOIN translation_stats t ON t.user_id = u.id
        LEFT JOIN validation_stats v ON v.user_id = u.id
        WHERE COALESCE(t.traducciones, 0) + COALESCE(v.validaciones, 0) > 0
        ORDER BY COALESCE(t.traducciones, 0) + COALESCE(v.validaciones, 0) DESC, u.nombre_completo ASC;
    """)).fetchall()

    generated_at = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    summary = {
        "generated_at": generated_at,
        "stats": {
            "participants": int(totals.participantes or 0),
            "translations": int(totals.traducciones or 0),
            "validations": int(totals.validaciones or 0),
            "months": 0,
        },
        "timeline": [],
        "top_translators": [_leader(row, "traducciones") for row in top_translators],
        "top_validators": [_leader(row, "validaciones") for row in top_validators],
        "participants": [_participant(row) for row in participants],
    }
    return _apply_official_timeline(summary)


@router.get("", response_model=dict)
async def get_project_summary(db: Session = Depends(get_db)):
    if SUMMARY_PATH.exists():
        try:
            with open(SUMMARY_PATH, "r", encoding="utf-8") as file:
                summary = json.load(file)
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=500, detail="El resumen del proyecto no se pudo leer.") from exc

        updated_summary = _apply_official_timeline(summary)
        with open(SUMMARY_PATH, "w", encoding="utf-8") as file:
            json.dump(updated_summary, file, ensure_ascii=False, indent=2)
        return updated_summary

    summary = _build_summary(db)
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SUMMARY_PATH, "w", encoding="utf-8") as file:
        json.dump(summary, file, ensure_ascii=False, indent=2)
    return summary
