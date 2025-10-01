from typing import List, Dict
from models import db_session, Session as DBSess, Message


class MemoryStore:
	def get_or_create_session(self, session_id: str) -> DBSess:
		sess = db_session.get(DBSess, session_id)
		if not sess:
			sess = DBSess(id=session_id)
			db_session.add(sess)
			db_session.commit()
		return sess

	def add_message(self, session_id: str, role: str, text: str) -> None:
		sess = self.get_or_create_session(session_id)
		msg = Message(session_id=sess.id, role=role, text=text)
		db_session.add(msg)
		db_session.commit()

	def get_recent_messages(self, session_id: str, limit: int = 5) -> List[Dict]:
		msgs = db_session.query(Message).filter(Message.session_id == session_id).order_by(Message.timestamp.desc()).limit(limit).all()
		return [
			{"role": m.role, "text": m.text, "timestamp": m.timestamp.isoformat()}
			for m in reversed(msgs)
		]
