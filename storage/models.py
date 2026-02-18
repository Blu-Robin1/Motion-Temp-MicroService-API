from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy import Float, Integer, String, DateTime, BigInteger, Text, func

class Base(DeclarativeBase):
    pass

class Temperature(Base):
    __tablename__ = "temperature"
    id = mapped_column(Integer, primary_key=True)
    station_id = mapped_column(String(250), nullable=False)
    station_name = mapped_column(String(250), nullable=False)
    temperature_celsius = mapped_column(Float, nullable=False)
    reporting_timestamp = mapped_column(DateTime, nullable=False)
    recorded_timestamp = mapped_column(DateTime, nullable=False)
    trace_id = mapped_column(BigInteger, nullable=False)  
    date_created = mapped_column(DateTime, nullable=False, default=func.now())

    def to_dict(self):
        return {
            "station_id": self.station_id,
            "station_name": self.station_name,
            "temperature_celsius": self.temperature_celsius,
            "reporting_timestamp": self.reporting_timestamp.isoformat(),
            "recorded_timestamp": self.recorded_timestamp.isoformat(),
            "trace_id": getattr(self, "trace_id", None),
        }


class Motion(Base):
    __tablename__ = "motion"
    id = mapped_column(Integer, primary_key=True)
    station_id = mapped_column(String(250), nullable=False)
    station_name = mapped_column(String(250), nullable=False)
    station_location = mapped_column(String(250), nullable=False)
    animal_speed = mapped_column(Integer, nullable=False)
    picture = mapped_column(Text, nullable=False)
    batch_timestamp = mapped_column(DateTime, nullable=False)
    recorded_timestamp = mapped_column(DateTime, nullable=False)
    trace_id = mapped_column(BigInteger, nullable=False)  
    date_created = mapped_column(DateTime, nullable=False, default=func.now())
    
    def to_dict(self):
        return {
            "station_id": self.station_id,
            "station_name": self.station_name,
            "station_location": self.station_location,
            "batch_timestamp": self.batch_timestamp.isoformat(),
            "picture": self.picture,
            "animal_speed": int(self.animal_speed),
            "recorded_timestamp": self.recorded_timestamp.isoformat(),
            "trace_id": getattr(self, "trace_id", None)
        }
