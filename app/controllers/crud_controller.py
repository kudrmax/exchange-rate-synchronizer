from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from typing import Type, TypeVar, Any, Optional

SchemaType = TypeVar('SchemaType', bound=BaseModel)
ModelType = TypeVar('ModelType')


class CRUDController:

    @classmethod
    def create_object(cls, db: Session, model: Type[ModelType], schema: SchemaType) -> ModelType:
        """
        Создание нового объекта в базе данных.

        Parameters
        ----------
        db : Session
            Сессия базы данных.
        model : Type[ModelType]
            Модель, по которой создается объект.
        schema : SchemaType
            Схема данных для создания объекта.


        Returns
        -------
        ModelType
            Созданный объект.
        """
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
        """
        Обновление существующего объекта в базе данных.

        Parameters
        ----------
        db : Session
            Сессия базы данных.
        model : Type[ModelType]
            Модель объекта для обновления.
        obj_id : Any
            Идентификатор объекта для обновления.
        schema : SchemaType
            Схема данных для обновления объекта.


        Returns
        -------
        ModelType
            Обновленный объект.
        """
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
