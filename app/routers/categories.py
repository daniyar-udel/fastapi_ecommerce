from fastapi import APIRouter

routers = APIRouter(prefix='/categories',
                    tags=['categories'])

@routers.get('/')
async def read_categories() -> dict:
    return {'message': 'All categories'}

@routers.post('/')
async def create_category() -> dict:
    return {'message': 'Create category'}

@routers.put('/{category_id}')
async def change_category(category_id: int) -> dict:
    return {'message': 'Change category'}

@routers.delete('/{category_id}')
async def delete_category(category_id: int) -> dict:
    return {'message': 'Delete category'}