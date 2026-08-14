import os
import sqlite3
import json
import uuid
from datetime import datetime
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
        created_at = datetime.utcnow().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO diagnoses (
                id, user_id, crop_type, image_url, condition, confidence,
                severity, symptoms, recommendations, model_name, model_version, is_mock, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            doc_id,
            record.get("userId", "anonymous_farmer"),
            record.get("crop", record.get("cropType", "Tomato")),
            record.get("imageUrl", ""),
            record.get("condition", "Healthy"),
            float(record.get("confidence", 0.90)),
            record.get("severity", "Moderate"),
            json.dumps(record.get("symptoms", [])),
            json.dumps(record.get("recommendations", {})),
            record.get("model_name", "AI Vision"),
            record.get("model_version", "v1.0"),
            1 if record.get("is_mock", False) else 0,
            created_at
        ))
        conn.commit()
        conn.close()

        saved_doc = dict(record)
        saved_doc["id"] = doc_id
        saved_doc["createdAt"] = created_at
        return saved_doc

    def get_history(self, crop_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if crop_filter and crop_filter != "All":
            cursor.execute("SELECT * FROM diagnoses WHERE crop_type = ? ORDER BY created_at DESC", (crop_filter,))
        else:
            cursor.execute("SELECT * FROM diagnoses ORDER BY created_at DESC")

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

    def get_diagnosis_by_id(self, diag_id: str) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
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

    def delete_diagnosis(self, diag_id: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM diagnoses WHERE id = ?", (diag_id,))
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0

db = Database()
