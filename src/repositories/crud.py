# Inspired by https://github.com/aminalaee/sqladmin/blob/main/sqladmin/_queries.py#L51
# and https://github.com/awtkns/fastapi-crudrouter/blob/master/fastapi_crudrouter/core/sqlalchemy.py

__all__ = ["CRUDFactory", "AbstractCRUD"]

from abc import ABCMeta, abstractmethod
from typing import TypeVar, Generic, Union, Any, Optional, Sequence, TypeAlias, cast, Iterable

from pydantic import BaseModel
from sqlalchemy import select, Select, Column, inspect, func, ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import RelationshipProperty, RelationshipDirection, Mapper, joinedload
from sqlalchemy.orm.interfaces import ORMOption
from sqlalchemy.sql.base import ExecutableOption

from src.storage.sql.models.base import Base

DbCreate = TypeVar("DbCreate", bound=Union[BaseModel, dict])
DbView = TypeVar("DbView", bound=BaseModel)
DbUpdate = TypeVar("DbUpdate", bound=Union[BaseModel, dict])
Identifier: TypeAlias = Union[int, str]


class AbstractCRUD(Generic[DbCreate, DbView, DbUpdate], metaclass=ABCMeta):
    @abstractmethod
    async def create(self, session: AsyncSession, data: DbCreate) -> DbView:
        raise NotImplementedError

    @abstractmethod
    async def read(self, session: AsyncSession, ident: Identifier) -> Optional[DbView]:
        raise NotImplementedError

    @abstractmethod
    async def read_many(
        self,
        session: AsyncSession,
        order_by: Optional[list[tuple[Column, bool]]] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> list[DbView]:
        raise NotImplementedError

    @abstractmethod
    async def read_all(
        self, session: AsyncSession, order_by: Optional[list[tuple[Column, bool]]] = None
    ) -> list[DbView]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, session: AsyncSession, ident: Identifier, data: DbUpdate) -> Optional[DbView]:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, session: AsyncSession, ident: Identifier) -> None:
        raise NotImplementedError

    @abstractmethod
    async def count(self, session: AsyncSession) -> int:
        raise NotImplementedError

    @abstractmethod
    def translate_order_by(self, order_by: list[tuple[str, bool]]) -> list[tuple[Column, bool]]:
        raise NotImplementedError


class CRUDFactory(AbstractCRUD[DbCreate, DbView, DbUpdate]):
    model: type[Base]
    out_scheme: type[DbView]
    options: tuple[ExecutableOption | ORMOption, ...]
    _mapper: Mapper
    _primary_key: Column
    _primary_key_type: type
    _columns: dict[str, Column]

    def __init__(
        self,
        model: type[Base],
        out_scheme: type[DbView],
        options: Optional[Sequence[ExecutableOption]] = None,
    ):
        self.model = model
        self._mapper = inspect(model)
        self._primary_key = tuple(self._mapper.primary_key)[0]
        self._primary_key_type = get_column_python_type(self._primary_key)
        self._columns = {column.key: column for column in self._mapper.columns}
        self.out_scheme = out_scheme
        self.options = tuple(options) if options else tuple()

    async def create(self, session: AsyncSession, data: DbCreate) -> DbView:
        if isinstance(data, BaseModel):
            data = data.model_dump()
        data: dict[str, Any]
        obj = self.model()
        obj = await self._set_attributes(session, obj, data)
        session.add(obj)
        await session.commit()
        await session.merge(obj, options=self.options)
        return self.out_scheme.model_validate(obj)

    async def read(self, session: AsyncSession, ident: Identifier) -> Optional[DbView]:
        result = await session.get(self.model, ident, options=self.options)
        if result:
            return self.out_scheme.model_validate(result)

    async def read_many(
        self,
        session: AsyncSession,
        order_by: Optional[list[tuple[Column, bool]]] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> list[DbView]:
        query: Select = select(self.model).options(*self.options)

        if order_by:
            for column, is_asc in order_by:
                query = query.order_by(column.asc()) if is_asc else query.order_by(column.desc())
        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        objs = (await session.scalars(query)).all()
        if not objs:
            return []
        return [self.out_scheme.model_validate(obj) for obj in objs]

    async def read_all(
        self, session: AsyncSession, order_by: Optional[list[tuple[Column, bool]]] = None
    ) -> list[DbView]:
        query = select(self.model).options(*self.options)
        if order_by:
            for column, is_asc in order_by:
                query = query.order_by(column.asc()) if is_asc else query.order_by(column.desc())
        objs = (await session.scalars(query)).all()
        if not objs:
            return []
        return [self.out_scheme.model_validate(obj) for obj in objs]

    async def update(self, session: AsyncSession, ident: Identifier, data: DbUpdate) -> Optional[DbView]:
        if isinstance(data, BaseModel):
            data = data.model_dump()
        data: dict[str, Any]
        clause = cast(ColumnElement[bool], self._primary_key == ident)
        stmt: Select = select(self.model).where(clause)

        for relation in cast(Iterable, self._mapper.relationships):
            relation: RelationshipProperty
            stmt = stmt.options(joinedload(getattr(self.model, relation.key)))

        obj = await session.scalar(stmt)

        if obj is None:
            return None

        obj = await self._set_attributes(session, obj, data)
        await session.commit()
        await session.merge(obj, options=self.options)
        return self.out_scheme.model_validate(obj)

    async def delete(self, session: AsyncSession, ident: Identifier) -> bool:
        clause = self._primary_key == ident
        stmt = select(self.model).where(clause)  # type: ignore
        obj = await session.scalar(stmt)
        if obj is None:
            return False
        await session.delete(obj)
        await session.commit()
        return True

    async def count(self, session: AsyncSession) -> int:
        query = select(func.count(self._primary_key))
        return (await session.execute(query)).scalar_one()

    def translate_order_by(self, order_by: list[tuple[str, bool]]) -> list[tuple[Column, bool]]:
        return [(self._columns[column], is_asc) for column, is_asc in order_by]

    async def _set_attributes(self, session: AsyncSession, obj: Base, data: dict[str, Any]) -> Base:
        for key, value in data.items():
            if not hasattr(obj, key):
                continue

            column = self._mapper.columns.get(key)
            relation = self._mapper.relationships.get(key)

            # Set falsy values to None, if column is Nullable
            if not value:
                if not value and not relation and column.nullable:
                    value = None
                setattr(obj, key, value)
                continue

            if relation is None:
                setattr(obj, key, value)
            else:
                relation: RelationshipProperty
                direction = relation.direction

                if direction == RelationshipDirection.ONETOMANY or direction == RelationshipDirection.MANYTOMANY:
                    # Many-to-many relation
                    related_stmt = self._get_to_many_stmt(relation, value)
                    result = await session.execute(related_stmt)
                    related_objs = result.scalars().all()
                    setattr(obj, key, related_objs)
                elif direction == RelationshipDirection.ONETOMANY and not relation.uselist:
                    # One-to-one relation
                    related_stmt = self._get_to_one_stmt(relation, value)
                    result = await session.execute(related_stmt)
                    related_obj = result.scalars().first()
                    setattr(obj, key, related_obj)
                else:
                    # Many-to-one relation
                    obj = _set_many_to_one(obj, relation, value)
        return obj

    def _get_to_many_stmt(self, relation: RelationshipProperty, idents: list[Identifier]) -> Select:
        target = relation.mapper.class_
        clause = self._primary_key.in_(idents)
        return select(target).where(clause)

    def _get_to_one_stmt(self, relation: RelationshipProperty, ident: Identifier) -> Select:
        target: Mapper = relation.mapper.class_
        clause = cast(ColumnElement[bool], self._primary_key == ident)
        return select(target).where(clause)


def _set_many_to_one(obj: Base, relation: RelationshipProperty, foreign_key: Any) -> Base:
    if relation.local_remote_pairs is None:
        return obj

    if len(relation.local_remote_pairs) > 1:
        raise NotImplementedError("Composite primary keys are not supported")

    for fk, pk in relation.local_remote_pairs:
        setattr(obj, fk.name, foreign_key)
    return obj


def get_column_python_type(column: Column) -> type:
    try:
        if hasattr(column.type, "impl"):
            return column.type.impl.python_type
        return column.type.python_type
    except NotImplementedError:
        return str
