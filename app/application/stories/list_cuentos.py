from typing import List
from app.domain.entities.cuento import Cuento 
from app.infrastructure.persistence.repositories.cuento_repo import CuentoRepository


class ListarCuentos:
    """
    Use case: Lista todos los cuentos disponibles
    """
    def __init__(self, cuento_repo: CuentoRepository):
        self.cuento_repo = cuento_repo

    def ejecutar(self) -> List[Cuento]:
        """
        Devuelve todos los cuentos ordenados por fecha (más nuevos primero)
        """
        return self.cuento_repo.listar()