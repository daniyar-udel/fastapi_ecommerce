from fastapi import FastAPI
from app.routers.categories import routers as categories
from app.routers.products import routers as products
from app.routers.users import router as users


app = FastAPI(title='FastAPI for store',
              version='0.1.0')

app.include_router(categories)
app.include_router(products)
app.include_router(users)

@app.get('/')
async def main_page() -> dict:
    return {'message': 'Main page'}