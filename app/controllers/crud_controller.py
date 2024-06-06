from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from typing import Type, TypeVar, Any, Optional

SchemaType = TypeVar('SchemaType', bound=BaseModel)
ModelType = TypeVar('ModelType')


class CRUDController:

    @classmethod
    def create_object(cls, db: Session, model: Type[ModelType], schema: SchemaType) -> ModelType:
        obj = model(**schema.model_dump())
        db.add(obj)
        try:
            db.commit()
            db.refresh(obj)
        except IntegrityError:
            db.rollback()
            raise Exception(f'Bad initial data for creating object with schema {schema}')
        return obj

    @classmethod
    def update_object(cls, db: Session, model: Type[ModelType], obj_id: Any, schema: SchemaType) -> ModelType:
        obj = db.query(model).get(obj_id)
        if obj:
            obj_data = schema.model_dump(exclude_unset=True)
            for key, value in obj_data.items():
                setattr(obj, key, value)
            try:
                db.commit()
                db.refresh(obj)
            except IntegrityError:
                db.rollback()
                raise Exception(f'Bad initial data for creating object with schema {schema}')
        else:
            raise ValueError(f"{model.__name__} with obj_id {obj_id} not found")
        return obj
