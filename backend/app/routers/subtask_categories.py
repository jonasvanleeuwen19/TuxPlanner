from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/subtask-categories", tags=["subtask-categories"])


@router.get("/", response_model=List[schemas.SubtaskCategoryResponse])
def list_subtask_categories(db: Session = Depends(get_db)):
    return db.query(models.SubtaskCategory).order_by(models.SubtaskCategory.name).all()


@router.get("/{category_id}", response_model=schemas.SubtaskCategoryResponse)
def get_subtask_category(category_id: int, db: Session = Depends(get_db)):
    cat = db.query(models.SubtaskCategory).filter(models.SubtaskCategory.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return cat


@router.post("/", response_model=schemas.SubtaskCategoryResponse, status_code=status.HTTP_201_CREATED)
def create_subtask_category(category: schemas.SubtaskCategoryCreate, db: Session = Depends(get_db)):
    db_cat = models.SubtaskCategory(**category.model_dump())
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat


@router.put("/{category_id}", response_model=schemas.SubtaskCategoryResponse)
def update_subtask_category(category_id: int, category: schemas.SubtaskCategoryUpdate, db: Session = Depends(get_db)):
    db_cat = db.query(models.SubtaskCategory).filter(models.SubtaskCategory.id == category_id).first()
    if not db_cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    for field, value in category.model_dump(exclude_unset=True).items():
        setattr(db_cat, field, value)
    db.commit()
    db.refresh(db_cat)
    return db_cat


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subtask_category(category_id: int, db: Session = Depends(get_db)):
    db_cat = db.query(models.SubtaskCategory).filter(models.SubtaskCategory.id == category_id).first()
    if not db_cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    db.query(models.Subtask).filter(models.Subtask.category_id == category_id).update(
        {models.Subtask.category_id: None}
    )
    db.delete(db_cat)
    db.commit()
