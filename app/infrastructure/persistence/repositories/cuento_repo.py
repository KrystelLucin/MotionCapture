# app/infrastructure/persistence/repositories/cuento_repo.py
from sqlalchemy.orm import Session
from app.domain.entities.cuento import Cuento
from app.infrastructure.persistence.models.cuento_model import CuentoModel

class CuentoRepository:
    def __init__(self, db: Session):
        self.db = db

    def guardar(self, cuento: Cuento) -> Cuento:
        model = CuentoModel(
            titulo=cuento.titulo,
            descripcion=cuento.descripcion,
            texto=cuento.texto,
            imagen_url=cuento.imagen_url,
            audio_url=cuento.audio_url,
            movimientos_json_url=cuento.movimientos_json_url,
            es_personalizado=cuento.es_personalizado,
            creado_por=cuento.creado_por
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        cuento.id = model.id
        return cuento

    def obtener_por_id(self, id: int) -> Cuento | None:
        model = self.db.query(CuentoModel).filter(CuentoModel.id == id).first()
        return self._to_entity(model) if model else None

    def listar(self):
        models = self.db.query(CuentoModel).all()
        return [self._to_entity(m) for m in models]

    def _to_entity(self, model: CuentoModel) -> Cuento:
        return Cuento(
            id=model.id,
            titulo=model.titulo,
            descripcion=model.descripcion,
            texto=model.texto,
            imagen_url=model.imagen_url,
            audio_url=model.audio_url,
            movimientos_json_url=model.movimientos_json_url,
            es_personalizado=model.es_personalizado,
            creado_en=model.creado_en,
            creado_por=model.creado_por
        )