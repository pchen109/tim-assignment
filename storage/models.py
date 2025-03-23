from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy import Integer, String, DateTime, func


class Base(DeclarativeBase):
	pass

class LoginInfo(Base):
	__tablename__ = "login_info"
	id = mapped_column(Integer, primary_key=True)
	user_id = mapped_column(String(50), nullable=False)
	region = mapped_column(String(50), nullable=False)
	login_streak = mapped_column(Integer, nullable=False)
	timestamp = mapped_column(DateTime, nullable=False)
	date_created = mapped_column(DateTime, nullable=False, default=func.now())
	trace_id = mapped_column(String(50), nullable=False)

	def __init__(self, user_id, region, timestamp, login_streak, trace_id):
		self.user_id = user_id
		self.region = region
		self.timestamp = timestamp
		self.login_streak = login_streak
		self.date_created = func.now()
		self.trace_id = trace_id

	def to_dict(self):
		return {
			"user_id": self.user_id,
			"region": self.region,
			"login_streak": self.login_streak,
			"timestamp": self.timestamp,
			"trace_id": self.trace_id
		}

class PerformanceReport(Base):
	__tablename__ = "performance_report"
	id = mapped_column(Integer, primary_key=True)
	user_id = mapped_column(String(50), nullable=False)
	match_id = mapped_column(String(50), nullable=False)
	kills = mapped_column(Integer, nullable=False)
	deaths = mapped_column(Integer, nullable=False)
	assists = mapped_column(Integer, nullable=False)
	timestamp = mapped_column(DateTime, nullable=False)
	game_length = mapped_column(Integer, nullable=False)
	date_created = mapped_column(DateTime, nullable=False, default=func.now())
	trace_id = mapped_column(String(50), nullable=False)

	def __init__(self, user_id, match_id, kills, deaths, assists, game_length, timestamp, trace_id):
		self.user_id = user_id
		self.match_id = match_id
		self.kills = kills
		self.deaths = deaths
		self.assists = assists
		self.game_length = game_length
		self.timestamp = timestamp
		self.date_created = func.now()
		self.trace_id = trace_id

	def to_dict(self):
		return {
			"user_id": self.user_id,
			"match_id": self.match_id,
			"kills": self.kills,
			"deaths": self.deaths,
			"assists": self.assists,
			"game_length": self.game_length,
			"timestamp": self.timestamp,
			"trace_id": self.trace_id
		}