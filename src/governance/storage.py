"""Storage abstraction and SQLite implementation for sessions, events, policies, evaluations."""

import json
import sqlite3
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.governance.schema import (
    ATSEvent,
    ATSEventType,
    PolicyEvaluationRecord,
    PolicyRecord,
    SessionRecord,
    SessionStatus,
)

# Default SQLite path when DATABASE_URL is not set or is file-based
DEFAULT_DB_PATH = Path("agent_ops.db").resolve()


def _now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_utc(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


class IStorage(ABC):
    """Abstract storage interface for governance data."""

    @abstractmethod
    def create_tables(self) -> None:
        """Create or ensure tables exist."""
        ...

    @abstractmethod
    def create_session(self, session: SessionRecord) -> SessionRecord:
        """Persist a new session; return with same id."""
        ...

    @abstractmethod
    def get_session(self, session_id: str) -> SessionRecord | None:
        """Load session by id."""
        ...

    @abstractmethod
    def update_session(
        self,
        session_id: str,
        *,
        status: SessionStatus | None = None,
        ari_score: float | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        """Update session fields."""
        ...

    @abstractmethod
    def list_sessions(
        self,
        limit: int = 50,
        demo_only: bool = False,
    ) -> list[SessionRecord]:
        """List sessions, most recent first."""
        ...

    @abstractmethod
    def create_event(self, event: ATSEvent) -> ATSEvent:
        """Persist event; assign id; return event."""
        ...

    @abstractmethod
    def list_events(self, session_id: str, limit: int = 200) -> list[ATSEvent]:
        """List events for a session by sequence."""
        ...

    @abstractmethod
    def create_policy(self, policy: PolicyRecord) -> PolicyRecord:
        """Persist policy."""
        ...

    @abstractmethod
    def get_policy(self, policy_id: str) -> PolicyRecord | None:
        """Load policy by id."""
        ...

    @abstractmethod
    def list_policies(self) -> list[PolicyRecord]:
        """List all policies."""
        ...

    @abstractmethod
    def update_policy_enabled(self, policy_id: str, enabled: bool) -> None:
        """Toggle policy enabled."""
        ...

    @abstractmethod
    def create_evaluation(self, record: PolicyEvaluationRecord) -> PolicyEvaluationRecord:
        """Persist evaluation; assign id; return record."""
        ...

    @abstractmethod
    def list_evaluations(
        self,
        session_id: str | None = None,
        limit: int = 500,
    ) -> list[PolicyEvaluationRecord]:
        """List evaluations, optionally for one session; most recent first."""
        ...


class SQLiteStorage(IStorage):
    """SQLite implementation of IStorage. Uses sync sqlite3."""

    def __init__(self, path: str | Path = DEFAULT_DB_PATH) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self._path), check_same_thread=False)

    def create_tables(self) -> None:
        conn = self._conn()
        try:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS agent_sessions (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    objective TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    created_at TEXT NOT NULL,
                    updated_at TEXT,
                    ari_score REAL NOT NULL DEFAULT 0 CHECK (ari_score >= 0 AND ari_score <= 100),
                    demo INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS ats_events (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    sequence INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES agent_sessions(id)
                );
                CREATE INDEX IF NOT EXISTS idx_events_session ON ats_events(session_id);
                CREATE TABLE IF NOT EXISTS policies (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    enabled INTEGER NOT NULL DEFAULT 1,
                    config TEXT NOT NULL DEFAULT '{}'
                );
                CREATE TABLE IF NOT EXISTS policy_evaluations (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    policy_id TEXT NOT NULL,
                    result TEXT NOT NULL,
                    reason TEXT NOT NULL DEFAULT '',
                    ari_impact REAL NOT NULL DEFAULT 0,
                    event_sequence INTEGER NOT NULL DEFAULT 0,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES agent_sessions(id)
                );
                CREATE INDEX IF NOT EXISTS idx_evals_session ON policy_evaluations(session_id);
            """)
            conn.commit()
        finally:
            conn.close()

    def create_session(self, session: SessionRecord) -> SessionRecord:
        conn = self._conn()
        try:
            conn.execute(
                """
                INSERT INTO agent_sessions (id, name, objective, status, created_at, updated_at, ari_score, demo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session.id,
                    session.name,
                    session.objective,
                    session.status,
                    session.created_at.isoformat(),
                    session.updated_at.isoformat() if session.updated_at else None,
                    session.ari_score,
                    1 if session.demo else 0,
                ),
            )
            conn.commit()
        finally:
            conn.close()
        return session

    def get_session(self, session_id: str) -> SessionRecord | None:
        conn = self._conn()
        try:
            row = conn.execute(
                "SELECT id, name, objective, status, created_at, updated_at, ari_score, demo FROM agent_sessions WHERE id = ?",
                (session_id,),
            ).fetchone()
        finally:
            conn.close()
        if not row:
            return None
        return SessionRecord(
            id=row[0],
            name=row[1],
            objective=row[2],
            status=row[3],
            created_at=datetime.fromisoformat(row[4].replace("Z", "+00:00")),
            updated_at=_parse_utc(row[5]),
            ari_score=row[6],
            demo=bool(row[7]),
        )

    def update_session(
        self,
        session_id: str,
        *,
        status: SessionStatus | None = None,
        ari_score: float | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        updates: list[str] = []
        args: list[Any] = []
        if status is not None:
            updates.append("status = ?")
            args.append(status)
        if ari_score is not None:
            updates.append("ari_score = ?")
            args.append(ari_score)
        if updated_at is not None:
            updates.append("updated_at = ?")
            args.append(updated_at.isoformat())
        if not updates:
            return
        args.append(session_id)
        conn = self._conn()
        try:
            conn.execute(
                f"UPDATE agent_sessions SET {', '.join(updates)} WHERE id = ?",
                args,
            )
            conn.commit()
        finally:
            conn.close()

    def list_sessions(
        self,
        limit: int = 50,
        demo_only: bool = False,
    ) -> list[SessionRecord]:
        conn = self._conn()
        try:
            if demo_only:
                rows = conn.execute(
                    "SELECT id, name, objective, status, created_at, updated_at, ari_score, demo FROM agent_sessions WHERE demo = 1 ORDER BY created_at DESC LIMIT ?",
                    (limit,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT id, name, objective, status, created_at, updated_at, ari_score, demo FROM agent_sessions ORDER BY created_at DESC LIMIT ?",
                    (limit,),
                ).fetchall()
        finally:
            conn.close()
        return [
            SessionRecord(
                id=r[0],
                name=r[1],
                objective=r[2],
                status=r[3],
                created_at=datetime.fromisoformat(r[4].replace("Z", "+00:00")),
                updated_at=_parse_utc(r[5]),
                ari_score=r[6],
                demo=bool(r[7]),
            )
            for r in rows
        ]

    def create_event(self, event: ATSEvent) -> ATSEvent:
        eid = str(uuid.uuid4())
        conn = self._conn()
        try:
            conn.execute(
                "INSERT INTO ats_events (id, session_id, type, payload, sequence, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    eid,
                    event.session_id,
                    event.type,
                    json.dumps(event.payload),
                    event.sequence,
                    event.timestamp.isoformat(),
                ),
            )
            conn.commit()
        finally:
            conn.close()
        return ATSEvent(
            id=eid,
            session_id=event.session_id,
            type=event.type,
            payload=event.payload,
            sequence=event.sequence,
            timestamp=event.timestamp,
        )

    def list_events(self, session_id: str, limit: int = 200) -> list[ATSEvent]:
        conn = self._conn()
        try:
            rows = conn.execute(
                "SELECT id, session_id, type, payload, sequence, timestamp FROM ats_events WHERE session_id = ? ORDER BY sequence ASC LIMIT ?",
                (session_id, limit),
            ).fetchall()
        finally:
            conn.close()
        return [
            ATSEvent(
                id=r[0],
                session_id=r[1],
                type=r[2],
                payload=json.loads(r[3]) if isinstance(r[3], str) else r[3],
                sequence=r[4],
                timestamp=datetime.fromisoformat(r[5].replace("Z", "+00:00")),
            )
            for r in rows
        ]

    def create_policy(self, policy: PolicyRecord) -> PolicyRecord:
        conn = self._conn()
        try:
            conn.execute(
                "INSERT INTO policies (id, name, enabled, config) VALUES (?, ?, ?, ?)",
                (policy.id, policy.name, 1 if policy.enabled else 0, json.dumps(policy.config)),
            )
            conn.commit()
        finally:
            conn.close()
        return policy

    def get_policy(self, policy_id: str) -> PolicyRecord | None:
        conn = self._conn()
        try:
            row = conn.execute(
                "SELECT id, name, enabled, config FROM policies WHERE id = ?",
                (policy_id,),
            ).fetchone()
        finally:
            conn.close()
        if not row:
            return None
        return PolicyRecord(
            id=row[0],
            name=row[1],
            enabled=bool(row[2]),
            config=json.loads(row[3]) if isinstance(row[3], str) else row[3],
        )

    def list_policies(self) -> list[PolicyRecord]:
        conn = self._conn()
        try:
            rows = conn.execute("SELECT id, name, enabled, config FROM policies").fetchall()
        finally:
            conn.close()
        return [
            PolicyRecord(
                id=r[0],
                name=r[1],
                enabled=bool(r[2]),
                config=json.loads(r[3]) if isinstance(r[3], str) else r[3],
            )
            for r in rows
        ]

    def update_policy_enabled(self, policy_id: str, enabled: bool) -> None:
        conn = self._conn()
        try:
            conn.execute("UPDATE policies SET enabled = ? WHERE id = ?", (1 if enabled else 0, policy_id))
            conn.commit()
        finally:
            conn.close()

    def create_evaluation(self, record: PolicyEvaluationRecord) -> PolicyEvaluationRecord:
        eid = str(uuid.uuid4())
        conn = self._conn()
        try:
            conn.execute(
                """INSERT INTO policy_evaluations (id, session_id, policy_id, result, reason, ari_impact, event_sequence, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    eid,
                    record.session_id,
                    record.policy_id,
                    record.result,
                    record.reason,
                    record.ari_impact,
                    record.event_sequence,
                    record.timestamp.isoformat(),
                ),
            )
            conn.commit()
        finally:
            conn.close()
        return PolicyEvaluationRecord(
            id=eid,
            session_id=record.session_id,
            policy_id=record.policy_id,
            result=record.result,
            reason=record.reason,
            ari_impact=record.ari_impact,
            event_sequence=record.event_sequence,
            timestamp=record.timestamp,
        )

    def list_evaluations(
        self,
        session_id: str | None = None,
        limit: int = 500,
    ) -> list[PolicyEvaluationRecord]:
        conn = self._conn()
        try:
            if session_id:
                rows = conn.execute(
                    """SELECT id, session_id, policy_id, result, reason, ari_impact, event_sequence, timestamp
                    FROM policy_evaluations WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?""",
                    (session_id, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    """SELECT id, session_id, policy_id, result, reason, ari_impact, event_sequence, timestamp
                    FROM policy_evaluations ORDER BY timestamp DESC LIMIT ?""",
                    (limit,),
                ).fetchall()
        finally:
            conn.close()
        return [
            PolicyEvaluationRecord(
                id=r[0],
                session_id=r[1],
                policy_id=r[2],
                result=r[3],
                reason=r[4],
                ari_impact=r[5],
                event_sequence=r[6],
                timestamp=datetime.fromisoformat(r[7].replace("Z", "+00:00")),
            )
            for r in rows
        ]
