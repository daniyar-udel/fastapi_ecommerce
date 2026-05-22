from fastapi import FastAPI
from routers.categories import routers as categories
from routers.products import routers as products


app = FastAPI(title='FastAPI for store',
              version='0.1.0')

app.include_router(categories)
app.include_router(products)

@app.get('/')
async def main_page() -> dict:
    return {'message': 'Main page'}