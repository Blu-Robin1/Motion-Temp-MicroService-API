from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy import Float, Integer, String, DateTime, func

class Base(DeclarativeBase):
    pass

class Temperature(Base):
    __tablename__ = "temperature"
    id = mapped_column(Integer, primary_key=True)
    station_id = mapped_column(String(250), nullable=False)
    station_name = mapped_column(String(250), nullable=False)
    temp_c = mapped_column(Float, nullable=False)
    batch_timestamp = mapped_column(DateTime, nullable=False)
    reading_timestamp = mapped_column(DateTime, nullable=False)
    date_created = mapped_column(DateTime, nullable=False, default=func.now())

class Motion(Base):
    __tablename__ = "motion"
    id = mapped_column(Integer, primary_key=True)
    station_id = mapped_column(String(250), nullable=False)
    station_name = mapped_column(String(250), nullable=False)
    motion = mapped_column(Float, nullable=False)
    picture = mapped_column(String, nullable=False)
    batch_timestamp = mapped_column(DateTime, nullable=False)
    reading_timestamp = mapped_column(DateTime, nullable=False)
    date_created = mapped_column(DateTime, nullable=False, default=func.now())
