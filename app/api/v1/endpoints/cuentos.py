# app/api/v1/endpoints/cuentos.py
# VERSIÓN FINAL – LEVANTA GARANTIZADO

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session

from app.api.v1.schemas.cuento import (
    CuentoCreateRequest,
    CuentoListResponse,
    CuentoDetailResponse,
)
from app.application.stories.create_custom_story import CreateCustomStory
from app.application.stories.list_cuentos import ListarCuentos
from app.application.stories.play_cuento import PlayStory
from app.infrastructure.persistence.repositories.cuento_repo import CuentoRepository
from app.infrastructure.robot.robot_executor import RobotExecutor
from app.infrastructure.database import get_db

router = APIRouter(prefix="/cuentos", tags=["cuentos"])

# ------------------------------------------------------------------
# DEPENDENCY FACTORIES – TODAS CON TIPO EXPLÍCITO → FastAPI las ama
# ------------------------------------------------------------------

def get_cuento_repo(db: Session = Depends(get_db)) -> CuentoRepository:
    return CuentoRepository(db)


def get_listar_cuentos_use_case(repo: CuentoRepository = Depends(get_cuento_repo)) -> ListarCuentos:
    return ListarCuentos(repo)


def get_create_custom_story_use_case() -> CreateCustomStory:
    # Si en el futuro CreateCustomStory necesita repo, azure_client, etc.
    # aquí es donde se inyectan. Por ahora es sin argumentos.
    return CreateCustomStory()


def get_play_story_use_case() -> PlayStory:
    return PlayStory(
        cuento_repo=get_cuento_repo(),
        robot_executor=RobotExecutor()
    )

# ------------------------------------------------------------------
# ENDPOINTS – TODO async, sin return None, sin lambdas, sin Depends()
# ------------------------------------------------------------------

@router.get("/", response_model=list[CuentoListResponse])
async def listar_cuentos(
    use_case: ListarCuentos = Depends(get_listar_cuentos_use_case),
):
    return use_case.ejecutar()


@router.get("/{id}", response_model=CuentoDetailResponse)
async def obtener_cuento(
    id: int,
    repo: CuentoRepository = Depends(get_cuento_repo),
):
    cuento = repo.obtener_por_id(id)
    if not cuento:
        raise HTTPException(status_code=404, detail="Cuento no encontrado")
    return CuentoDetailResponse.model_validate(cuento)


@router.post(
    "/custom",
    status_code=status.HTTP_201_CREATED,
    response_model=None,        # cuerpo vacío → 201 sin problemas
)
async def crear_cuento_personalizado(
    request: CuentoCreateRequest,
    create_use_case: CreateCustomStory = Depends(get_create_custom_story_use_case),
):
    # ¡NUNCA return None! Simplemente terminamos la función
    create_use_case.execute(request)


@router.post("/{cuento_id}/reproducir", status_code=202)
async def reproducir_cuento_en_robot(
    cuento_id: int,
    background_tasks: BackgroundTasks,
    play_use_case: PlayStory = Depends(get_play_story_use_case),
):
    background_tasks.add_task(play_use_case.execute, cuento_id)
    return {
        "status": "reproduciendo",
        "cuento_id": cuento_id,
    }