import os
import sqlite3
import json
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from backend.config import settings


class Database:
    def __init__(self):
        self.db_path = settings.SQLITE_FALLBACK_DB
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_sqlite()

    def _init_sqlite(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS diagnoses (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                crop_type TEXT,
                image_url TEXT,
                condition TEXT,
                confidence REAL,
                severity TEXT,
                symptoms TEXT,
                recommendations TEXT,
                model_name TEXT,
                model_version TEXT,
                is_mock INTEGER,
                created_at TEXT
            )
        """)
        conn.commit()
        conn.close()

    def save_diagnosis(self, record: Dict[str, Any]) -> Dict[str, Any]:
        doc_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()

        crop_val = record.get("cropType") or record.get("crop")
        if isinstance(crop_val, dict):
            crop_name = str(crop_val.get("name") or "Unknown")
        else:
            crop_name = str(crop_val or "Unknown")

        cond_val = record.get("condition") or record.get("diagnosis")
        if isinstance(cond_val, dict):
            cond_name = str(cond_val.get("name") or "Uncertain Result")
        else:
            cond_name = str(cond_val or "Uncertain Result")

        sev_val = record.get("severity")
        if isinstance(sev_val, dict):
            sev_name = str(sev_val.get("tier") or "Unknown")
        else:
            sev_name = str(sev_val or "Unknown")

        conf_val = record.get("confidence")
        try:
            conf_float = float(conf_val) if conf_val is not None else 0.0
        except (ValueError, TypeError):
            conf_float = 0.0
        conf_float = max(0.0, min(conf_float, 1.0))

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO diagnoses (
                id, user_id, crop_type, image_url, condition, confidence,
                severity, symptoms, recommendations, model_name, model_version, is_mock, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            doc_id,
            str(record.get("userId", "anonymous_farmer"))[:128],
            crop_name[:128],
            str(record.get("imageUrl", "")),
            cond_name[:256],
            conf_float,
            sev_name[:64],
            json.dumps(record.get("symptoms", []), ensure_ascii=False),
            json.dumps(record.get("recommendations", {}), ensure_ascii=False),
            str(record.get("modelName", record.get("model_name", "AI Vision")))[:256],
            str(record.get("modelVersion", record.get("model_version", "unknown")))[:128],
            1 if record.get("isMock", record.get("is_mock", False)) else 0,
            created_at
        ))
        conn.commit()
        conn.close()

        saved_doc = dict(record)
        saved_doc["id"] = doc_id
        saved_doc["createdAt"] = created_at
        return saved_doc

    def get_history(self, user_id: Optional[str] = None, crop_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM diagnoses WHERE 1=1"
        params = []

        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)

        if crop_filter and crop_filter != "All":
            query += " AND crop_type = ?"
            params.append(crop_filter)

        query += " ORDER BY created_at DESC"
        cursor.execute(query, tuple(params))

        rows = cursor.fetchall()
        conn.close()

        results = []
        for r in rows:
            results.append({
                "id": r["id"],
                "userId": r["user_id"],
                "crop": r["crop_type"],
                "cropType": r["crop_type"],
                "imageUrl": r["image_url"],
                "condition": r["condition"],
                "confidence": r["confidence"],
                "severity": r["severity"],
                "symptoms": json.loads(r["symptoms"]) if r["symptoms"] else [],
                "recommendations": json.loads(r["recommendations"]) if r["recommendations"] else {},
                "modelName": r["model_name"],
                "modelVersion": r["model_version"],
                "isMock": bool(r["is_mock"]),
                "createdAt": r["created_at"]
            })
        return results

    def get_diagnosis_by_id(self, diag_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if user_id:
            cursor.execute("SELECT * FROM diagnoses WHERE id = ? AND user_id = ?", (diag_id, user_id))
        else:
            cursor.execute("SELECT * FROM diagnoses WHERE id = ?", (diag_id,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return {
            "id": row["id"],
            "userId": row["user_id"],
            "crop": row["crop_type"],
            "cropType": row["crop_type"],
            "imageUrl": row["image_url"],
            "condition": row["condition"],
            "confidence": row["confidence"],
            "severity": row["severity"],
            "symptoms": json.loads(row["symptoms"]) if row["symptoms"] else [],
            "recommendations": json.loads(row["recommendations"]) if row["recommendations"] else {},
            "modelName": row["model_name"],
            "modelVersion": row["model_version"],
            "isMock": bool(row["is_mock"]),
            "createdAt": row["created_at"]
        }

    def delete_diagnosis(self, diag_id: str, user_id: Optional[str] = None) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if user_id:
            cursor.execute("DELETE FROM diagnoses WHERE id = ? AND user_id = ?", (diag_id, user_id))
        else:
            cursor.execute("DELETE FROM diagnoses WHERE id = ?", (diag_id,))
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0


db = Database()
