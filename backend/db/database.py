import os
import sqlite3
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
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
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_diagnoses_user_created ON diagnoses(user_id, created_at DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_diagnoses_crop ON diagnoses(crop_type)")

        # Improve concurrency for production-like workloads: enable WAL and relaxed synchronous
        try:
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("PRAGMA synchronous=NORMAL;")
        except Exception:
            # Best-effort; some SQLite builds may not support these pragmas
            pass

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

    def get_history(
        self,
        user_id: str,
        crop_filter: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Tuple[List[Dict[str, Any]], int]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        filters = ["user_id = ?"]
        params: List[Any] = [user_id]
        if crop_filter and crop_filter != "All":
            filters.append("crop_type = ?")
            params.append(crop_filter)
        where_clause = " AND ".join(filters)

        cursor.execute(
            f"SELECT COUNT(*) as total FROM diagnoses WHERE {where_clause}",
            params
        )
        total = int(cursor.fetchone()["total"])

        cursor.execute(
            f"SELECT * FROM diagnoses WHERE {where_clause} ORDER BY created_at DESC LIMIT ? OFFSET ?",
            [*params, limit, offset]
        )

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
        return results, total

    def get_diagnosis_by_id(self, diag_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM diagnoses WHERE id = ? AND user_id = ?", (diag_id, user_id))
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

    def delete_diagnosis(self, diag_id: str, user_id: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Retrieve image URL first so we can attempt cleanup of the file on disk
        cursor.execute("SELECT image_url FROM diagnoses WHERE id = ? AND user_id = ?", (diag_id, user_id))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return False

        image_url = row[0] if row and row[0] else None

        cursor.execute("DELETE FROM diagnoses WHERE id = ? AND user_id = ?", (diag_id, user_id))
        affected = cursor.rowcount
        conn.commit()
        conn.close()

        # Attempt to remove the associated uploaded file (best-effort)
        if image_url:
            try:
                # Parse URL to extract the path component robustly
                from urllib.parse import urlparse
                parsed = urlparse(image_url)
                file_name = os.path.basename(parsed.path)
                if file_name:
                    file_path = os.path.join(settings.UPLOAD_DIR, file_name)
                    if os.path.exists(file_path):
                        os.remove(file_path)
            except Exception:
                # Best-effort cleanup; don't fail the delete operation if file removal fails
                pass

        return affected > 0

db = Database()
