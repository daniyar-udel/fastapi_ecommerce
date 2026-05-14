from fastapi import APIRouter

routers = APIRouter(prefix='/products',
                  tags=['products'])

@routers.get('/')
async def read_productrs() -> dict:
    return {'message': 'All products'}

@routers.post('/')
async def create_product() -> dict:
    return {'message': 'Create product'}

@routers.get('/{product_id}')
async def read_product(product_id: int) -> dict:
    return {'message': 'Product'}

@routers.get('/category/{category_id}')
async def read_product_by_category(category_id: int) -> dict:
    return {'message': 'Product by category'}

@routers.put('/{product_id}')
async def change_product(product_id: int) -> dict:
    return {'message': 'Change product'}

@routers.delete('/{product_id}')
async def delete_product(product_id: int) -> dict:
    return {'message': 'Delete_product'}