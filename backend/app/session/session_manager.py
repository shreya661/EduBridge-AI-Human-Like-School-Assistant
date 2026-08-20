# backend/app/session/session_manager.py
import secrets
import time
from typing import Dict, Optional
from datetime import datetime, timedelta
from .models import Identity


class SessionData:
    def __init__(self, session_id: str, identity: Identity, created_at: datetime, expires_at: datetime):
        self.session_id = session_id
        self.identity = identity
        self.created_at = created_at
        self.expires_at = expires_at
    
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at


class InMemorySessionStore:
    def __init__(self, session_timeout_minutes: int = 60):
        self.sessions: Dict[str, SessionData] = {}
        self.session_timeout_minutes = session_timeout_minutes
    
    def create_session(self, identity: Identity) -> str:
        session_id = secrets.token_urlsafe(32)  # Cryptographically secure
        expires_at = datetime.utcnow() + timedelta(minutes=self.session_timeout_minutes)
        session_data = SessionData(
            session_id=session_id,
            identity=identity,
            created_at=datetime.utcnow(),
            expires_at=expires_at
        )
        self.sessions[session_id] = session_data
        return session_id
    
    def get_session(self, session_id: str) -> Optional[SessionData]:
        session_data = self.sessions.get(session_id)
        if session_data and session_data.is_expired():
            del self.sessions[session_id]
            return None
        return session_data
    
    def invalidate_session(self, session_id: str) -> bool:
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        expired_keys = []
        now = datetime.utcnow()
        for session_id, session_data in self.sessions.items():
            if session_data.is_expired():
                expired_keys.append(session_id)
        
        for key in expired_keys:
            del self.sessions[key]


# Global session store instance
session_store = InMemorySessionStore()
