from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.categories import Category as CategoryModel
from app.models.products import Product as ProductModel
from app.schemas import Product as ProductSchema, ProductCreate as ProductCreateSchema
from app.db_depends import get_db, get_async_db

from app.models.users import User as UserModel
from app.auth import get_current_seller

routers = APIRouter(prefix='/products',
                  tags=['products'])

@routers.get('/', response_model=list[ProductSchema], status_code=200)
async def read_productrs(db: AsyncSession=Depends(get_async_db)):
    stmn = select(ProductModel).where(ProductModel.is_active==True)
    db_product = await db.scalars(stmn)

    return db_product.all()

@routers.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreateSchema,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_seller)
):
    """
    Создаёт новый товар, привязанный к текущему продавцу (только для 'seller').
    """
    category_result = await db.scalars(
        select(CategoryModel).where(CategoryModel.id == product.category_id, CategoryModel.is_active == True)
    )
    if not category_result.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found or inactive")
    db_product = ProductModel(**product.model_dump(), seller_id=current_user.id)
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)  # Для получения id и is_active из базы
    return db_product

@routers.get('/{product_id}', response_model=ProductSchema, status_code=200)
async def read_product(product_id: int, db: AsyncSession=Depends(get_async_db)):
    stmn = select(ProductModel).where(ProductModel.id==product_id).where(ProductModel.is_active==True)
    result = await db.scalars(stmn)
    db_product = result.first()
    if db_product is None:
        raise HTTPException(status_code=400, detail='Product not found or inactive')
    
    stmn = select(CategoryModel).where(CategoryModel.id == db_product.category_id).where(CategoryModel.is_active==True)
    db_category = await db.scalars(stmn)
    if db_category.first() is None:
        raise HTTPException(status_code=404, detail='Category not found or inactive')

    return db_product

@routers.get('/category/{category_id}', response_model=list[ProductSchema], status_code=200)
async def read_product_by_category(category_id: int, db: AsyncSession=Depends(get_async_db)):
    stmn = select(CategoryModel).where(CategoryModel.id==category_id).where(CategoryModel.is_active==True)
    db_category = await db.scalars(stmn)
    if db_category.first() is None:
        raise HTTPException(status_code=404, detail='Category not found or inactive')
    
    stmn = select(ProductModel).where(ProductModel.category_id==category_id).where(ProductModel.is_active==True)
    db_product = await db.scalars(stmn)

    return db_product.all()

@routers.put("/{product_id}", response_model=ProductSchema)
async def update_product(
    product_id: int,
    product: ProductCreateSchema,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_seller)
):
    """
    Обновляет товар, если он принадлежит текущему продавцу (только для 'seller').
    """
    result = await db.scalars(select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active == True))
    db_product = result.first()
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    if db_product.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only update your own products")
    category_result = await db.scalars(
        select(CategoryModel).where(CategoryModel.id == product.category_id, CategoryModel.is_active == True)
    )
    if not category_result.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found or inactive")
    await db.execute(
        update(ProductModel).where(ProductModel.id == product_id).values(**product.model_dump())
    )
    await db.commit()
    await db.refresh(db_product)  # Для консистентности данных
    return db_product

@routers.delete("/{product_id}", response_model=ProductSchema)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_seller)
):
    """
    Выполняет мягкое удаление товара, если он принадлежит текущему продавцу (только для 'seller').
    """
    result = await db.scalars(
        select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active == True)
    )
    product = result.first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found or inactive")
    if product.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own products")
    await db.execute(
        update(ProductModel).where(ProductModel.id == product_id).values(is_active=False)
    )
    await db.commit()
    await db.refresh(product)  # Для возврата is_active = False
    return product

                  
