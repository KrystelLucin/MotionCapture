# app/api/v1/schemas/cuento.py
from pydantic import BaseModel
from typing import Optional

class CuentoCreateRequest(BaseModel):
    titulo: str
    texto: str
    creado_por: Optional[str] = None

class CuentoListResponse(BaseModel):
    id: int
    titulo: str
    imagen_url: Optional[str]

class CuentoDetailResponse(BaseModel):
    id: int
    titulo: str
    descripcion: Optional[str]
    texto: str
    audio_url: Optional[str]
    movimientos_json_url: Optional[str]
    es_personalizado: bool

class CuentoPlayResponse(BaseModel):
    audio_url: str
    movimientos_json_url: str