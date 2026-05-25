from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.schemas import Category as CategorySchema, CategoryCreate
from app.models.categories import Category as CategoryModel
from app.db_depends import get_db

routers = APIRouter(prefix='/categories',
                    tags=['categories'])

@routers.get('/', response_model=list[CategorySchema], status_code=status.HTTP_200_OK)
async def read_categories(db: Session=Depends(get_db)):
    stmn = select(CategoryModel).where(CategoryModel.is_active==True)
    result = db.scalars(stmn).all()

    return result

@routers.post('/', response_model=CategorySchema, status_code=status.HTTP_200_OK)
async def create_category(category: CategoryCreate, db: Session=Depends(get_db)):
    if category.parent_id is not None:
        stmn = select(CategoryModel).where(CategoryModel.id == category.parent_id).where(CategoryModel.is_active==True)
        parent = db.scalars(stmn).first()
        if parent is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Parent category does not exist')
    
    db_category = CategoryModel(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)

    return db_category

@routers.delete('/{category_id}', status_code=status.HTTP_200_OK)
async def change_category(category_id: int, db: Session=Depends(get_db)) -> dict:
    stmn = select(CategoryModel).where(CategoryModel.id==category_id).where(CategoryModel.is_active==True)
    result = db.scalars(stmn).first()
    if result is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Category id not found')
    
    db.execute(update(CategoryModel).where(CategoryModel.id==category_id).values(is_active=False))
    db.commit()

    return {'message': f'Category with {category_id} id deactivated'}

@routers.put('/{category_id}', response_model=CategorySchema, status_code=status.HTTP_200_OK)
async def delete_category(category_id: int, category: CategoryCreate, db: Session=Depends(get_db)):
    stmn = select(CategoryModel).where(CategoryModel.id==category_id).where(CategoryModel.is_active==True)
    db_category = db.scalars(stmn).first()
    if db_category is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Category not found')
    
    if category.parent_id is not None:
        stmn = select(CategoryModel).where(CategoryModel.id==category.parent_id).where(CategoryModel.is_active==True)
        parent = db.scalars(stmn).first()
        if parent is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Category with parent id does not exist')

    db.execute(update(CategoryModel).where(CategoryModel.id==category_id).values(**category.model_dump()))
    db.commit()
    db.refresh(db_category)

    return db_category
