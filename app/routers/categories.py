from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import Category as CategorySchema, CategoryCreate
from app.models.categories import Category as CategoryModel
from app.db_depends import get_db, get_async_db

routers = APIRouter(prefix='/categories',
                    tags=['categories'])

@routers.get('/', response_model=list[CategorySchema], status_code=status.HTTP_200_OK)
async def read_categories(db: AsyncSession=Depends(get_async_db)):
    stmn = select(CategoryModel).where(CategoryModel.is_active==True)
    result = await db.scalars(stmn)

    return result.all()

@routers.post('/', response_model=CategorySchema, status_code=status.HTTP_200_OK)
async def create_category(category: CategoryCreate, db: AsyncSession=Depends(get_async_db)):
    if category.parent_id is not None:
        stmn = select(CategoryModel).where(CategoryModel.id == category.parent_id).where(CategoryModel.is_active==True)
        result  = await db.scalars(stmn)
        parent = result.first()
        if parent is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Parent category does not exist')
    
    db_category = CategoryModel(**category.model_dump())
    db.add(db_category)
    await db.commit()
    

    return db_category

@routers.put('/{category_id}', response_model=CategorySchema, status_code=status.HTTP_200_OK)
async def delete_category(category_id: int, category: CategoryCreate, db: AsyncSession=Depends(get_async_db)):
    stmn = select(CategoryModel).where(CategoryModel.id==category_id).where(CategoryModel.is_active==True)
    result = await db.scalars(stmn)
    db_category = result.first()
    if db_category is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Category not found')
    
    if category.parent_id is not None:
        stmn = select(CategoryModel).where(CategoryModel.id==category.parent_id).where(CategoryModel.is_active==True)
        result = await db.scalars(stmn)
        parent = result.first()
        if parent is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Category with parent id does not exist')
        if parent.id == category_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Category id can not be equal parent id')

    await db.execute(update(CategoryModel).where(CategoryModel.id==category_id).values(**category.model_dump()))
    await db.commit()

    return db_category

@routers.delete('/{category_id}', status_code=status.HTTP_200_OK)
async def change_category(category_id: int, db: AsyncSession=Depends(get_async_db)):
    stmn = select(CategoryModel).where(CategoryModel.id==category_id).where(CategoryModel.is_active==True)
    result = await db.scalars(stmn)
    deleted = result.first()
    if deleted is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Category id not found')
    
    await db.execute(update(CategoryModel).where(CategoryModel.id==category_id).values(is_active=False))
    await db.commit()

    return deleted
