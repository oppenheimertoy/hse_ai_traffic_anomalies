from fastapi import APIRouter

api_router = APIRouter(prefix='/v1')


@api_router.get('/health')
async def health_check() -> dict[str, str]:
    return {'status': 'ok'}
