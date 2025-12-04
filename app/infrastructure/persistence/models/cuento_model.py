from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from app.infrastructure.persistence.models.base import Base
from datetime import datetime

class CuentoModel(Base):
    __tablename__ = "cuentos"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    descripcion = Column(Text)
    imagen_url = Column(String)
    texto = Column(Text, nullable=False)
    audio_url = Column(String)
    movimientos_json_url = Column(String)
    es_personalizado = Column(Boolean, default=False)

    activo = Column(Boolean, default=True)
    creado_en = Column(DateTime, default=datetime.utcnow)
    creado_por = Column(String, nullable=True)
    actualizado_en = Column(DateTime, nullable=True)
    actualizado_por = Column(String, nullable=True)
    eliminado_en = Column(DateTime, nullable=True)
    eliminado_por = Column(String, nullable=True)