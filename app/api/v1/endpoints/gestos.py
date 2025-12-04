from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from app.api.v1.dependencies import (
    get_gestor_sesiones,
    get_azure_storage,
    get_gesture_recorder,
)
from app.application.gestos.crear_sesion import CrearSesionGesto, CrearSesionGestoRequest, CrearSesionGestoResponse
from app.application.gestos.aprobar_gesto import AprobarGesto, AprobarGestoRequest, AprobarGestoResponse
from app.application.gestos.iniciar_grabacion import IniciarStreamGrabacion
from app.application.gestos.obtener_sesion import ObtenerSesion, ObtenerSesionResponse
from app.application.gestos.preview_gesto import PreviewGesto, PreviewGestoRequest
from app.domain.enums.gesture_type import GestureType
from app.infrastructure.storage.azure_storage import AzureStorageService

router = APIRouter(prefix="/gestos", tags=["gestos"])


@router.get("/sesion/{sesion_id}", response_model=ObtenerSesionResponse)
def obtener_sesion(
    sesion_id: str,
    gestor = Depends(get_gestor_sesiones),
):
    use_case = ObtenerSesion(gestor)
    return use_case.ejecutar(sesion_id)

@router.post("/sesion", response_model=CrearSesionGestoResponse)
def crear_sesion(
    request: CrearSesionGestoRequest,
    gestor = Depends(get_gestor_sesiones),
):
    use_case = CrearSesionGesto(gestor)
    return use_case.ejecutar(request)

@router.get("/sesion/{sesion_id}/stream")
def stream_gesto(
    sesion_id: str,
    gestor = Depends(get_gestor_sesiones),
    recorder = Depends(get_gesture_recorder),
):
    use_case = IniciarStreamGrabacion(gestor, recorder)
    generator = use_case.ejecutar(sesion_id)
    return StreamingResponse(generator, media_type="text/event-stream")

# Añade estas dos rutas

@router.post("/sesion/{sesion_id}/preview")
def generar_preview(
    sesion_id: str,
    gestor = Depends(get_gestor_sesiones),
    azure = Depends(get_azure_storage),
):
    use_case = PreviewGesto(gestor, azure)
    return use_case.ejecutar(PreviewGestoRequest(sesion_id=sesion_id))

@router.post("/sesion/{sesion_id}/aprobar")
def aprobar_gesto(
    sesion_id: str,
    nombre: str = Query(..., description="Nombre permanente del gesto"),
    gestor = Depends(get_gestor_sesiones),
    azure = Depends(get_azure_storage),
):
    use_case = AprobarGesto(gestor, azure)
    return use_case.ejecutar(AprobarGestoRequest(sesion_id=sesion_id, nombre=nombre))
@router.get("/gestos/{tipo}")
def listar_gestos(tipo: GestureType, storage: AzureStorageService = Depends()):
    return storage.listar_gestos_por_tipo(tipo)