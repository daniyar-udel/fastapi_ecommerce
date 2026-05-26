from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.categories import Category as CategoryModel
from app.models.products import Product as ProductModel
from app.schemas import Product as ProductSchema, ProductCreate as ProductCreateSchema
from app.db_depends import get_db

routers = APIRouter(prefix='/products',
                  tags=['products'])

@routers.get('/', response_model=list[ProductSchema], status_code=200)
async def read_productrs(db: Session=Depends(get_db)):
    stmn = select(ProductModel).where(ProductModel.is_active==True)
    db_product = db.scalars(stmn).all()

    return db_product

@routers.post('/', response_model=ProductSchema, status_code=201)
async def create_product(product: ProductCreateSchema, db: Session=Depends(get_db)):
    stmn = select(CategoryModel).where(CategoryModel.id==product.category_id).where(CategoryModel.is_active==True)
    db_category = db.scalars(stmn).first()
    if db_category is None:
        raise HTTPException(status=400, detail='Category not found or inactive')
    
    db_product = ProductModel(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    return db_product

@routers.get('/{product_id}', response_model=ProductSchema, status_code=200)
async def read_product(product_id: int, db: Session=Depends(get_db)):
    stmn = select(ProductModel).where(ProductModel.id==product_id).where(ProductModel.is_active==True)
    db_product = db.scalars(stmn).first()
    if db_product is None:
        raise HTTPException(status_code=400, detail='Product not found or inactive')
    
    stmn = select(CategoryModel).where(CategoryModel.id == db_product.category_id).where(CategoryModel.is_active==True)
    db_category = db.scalars(stmn).first()
    if db_category is None:
        raise HTTPException(status_code=404, detail='Category not found or inactive')

    return db_product

@routers.get('/category/{category_id}', response_model=list[ProductSchema], status_code=200)
async def read_product_by_category(category_id: int, db: Session=Depends(get_db)):
    stmn = select(CategoryModel).where(CategoryModel.id==category_id).where(CategoryModel.is_active==True)
    db_category = db.scalars(stmn).first()
    if db_category is None:
        raise HTTPException(status_code=404, detail='Category not found or inactive')
    
    stmn = select(ProductModel).where(ProductModel.category_id==category_id).where(ProductModel.is_active==True)
    db_product = db.scalars(stmn).all()

    return db_product

@routers.put('/{product_id}', response_model=ProductSchema, status_code=200)
async def change_product(product_id: int, product: ProductCreateSchema, db:Session=Depends(get_db)):
    stmn = select(ProductModel).where(ProductModel.id == product_id).where(ProductModel.is_active==True)
    db_product = db.scalars(stmn).first()
    if db_product is None:
        raise HTTPException(status_code=400, detail='Product not found or inactive')
    
    stmn = select(CategoryModel).where(CategoryModel.id==product.category_id).where(CategoryModel.is_active==True)
    if db.scalars(stmn).first() is None:
        raise HTTPException(status_code=404, detail='Category not found or inactive')
    
    db.execute(update(ProductModel).where(ProductModel.id==product_id).where(ProductModel.is_active==True)
               .values(**product.model_dump()))
    db.commit()
    db.refresh(db_product)

    return db_product

@routers.delete('/{product_id}', status_code=200)
async def delete_product(product_id: int, db: Session=Depends(get_db)) -> dict:
    stmn = select(ProductModel).where(ProductModel.id==product_id).where(ProductModel.is_active==True)
    db_product = db.scalars(stmn).first()
    if db_product is None:
        raise HTTPException(status_code=400, detail='Product not found or inactive')
    
    db.execute(update(ProductModel).where(ProductModel.id==product_id).where(ProductModel.is_active==True).values(is_active=False))
    db.commit()
    
    return {'message': 'sucess deleted'}