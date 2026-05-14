from fastapi import FastAPI
from app.routers import categories, products

app = FastAPI(title='FastAPI for store',
              version='0.1.0')

app.include_router(categories.routers)
app.include_router(products.routers)

@app.get('/')
async def main_page() -> dict:
    return {'message': 'Main page'}