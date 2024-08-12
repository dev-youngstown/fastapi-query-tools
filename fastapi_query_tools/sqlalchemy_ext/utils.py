from typing import Any
from sqlalchemy import Select, inspect, func, FromClause, ColumnElement, String, cast, Enum
from sqlalchemy.orm import (
    RelationshipProperty,
    aliased,
)
from sqlalchemy.orm.util import AliasedClass
from fastapi_query_tools import QueryModel


def is_nested(entity: Any, attribute_name: str) -> bool:
    """
    Checks if column is nested in the entity
    """
    mapper = inspect(entity)

    attr = mapper.attrs.get(attribute_name)

    return isinstance(attr, RelationshipProperty)


def get_column_attributes(
        entity: Any, relationship_name: str
) -> tuple[ColumnElement, AliasedClass | FromClause]:
    """
    Concat attributes of the nested entity to be used in filtering
    """

    # Get the mapper for the entity
    mapper = inspect(entity)

    # Get the relationship property
    relationship_prop = mapper.relationships[relationship_name]

    # Alias the related table
    related_entity = aliased(relationship_prop.mapper.class_)

    # List all columns from the related entity
    nested_columns = [
        getattr(related_entity, column.name)
        for column in related_entity.__table__.columns
    ]

    # Concatenate all the columns
    combined_column = func.concat(*nested_columns)

    return combined_column, related_entity


def handle_column_enum(column: Any, stmt: Select, query_model: QueryModel) -> Select | None:
    """
    Apply filter for enum column
    """
    if isinstance(column.type, Enum):
        enum_class = column.type.enum_class
        enum_val = enum_class(query_model.q)
        return stmt.filter(column == enum_val)
    else:
        return None


def filter(entity: Any, column: Any, stmt: Select, query_model: QueryModel) -> Select:
    """
    add filters to select statement
    """
    if is_nested(entity, query_model.sort_by):
        # Handle nested filtering
        combined_column, related_entity = get_column_attributes(
            entity, query_model.sort_by
        )

        # Join the related entity in the query
        stmt = stmt.join(related_entity).select_from(entity).select_from(related_entity)

        # Filter using the combined column
        return stmt.filter(cast(combined_column, String).ilike(f"%{query_model.q}%"))

    else:
        # Handle enum column
        return handle_column_enum(column, stmt, query_model) if handle_column_enum(column, stmt,
                                                                                   query_model) else stmt.filter(
            cast(column, String).ilike(f"%{query_model.q}%")
        )


def sort(entity: Any, column: Any, stmt: Select, query_model: QueryModel) -> Select:
    """
    add order by to select statement
    """
    if is_nested(entity, query_model.sort_by):
        # Handle nested filtering
        combined_column, related_entity = get_column_attributes(
            entity, query_model.sort_by
        )

        # Join the related entity in the query
        stmt = stmt.join(related_entity).select_from(entity).select_from(related_entity)

        # Filter using the combined column
        return (
            stmt.order_by(combined_column.desc())
            if query_model.order == "desc"
            else stmt.order_by(combined_column.asc())
        )
    else:
        return (
            stmt.order_by(column.desc())
            if query_model.order == "desc"
            else stmt.order_by(column.asc())
        )


def filter_and_sort(stmt: Select, query_model: QueryModel) -> Select:
    if query_model.sort_by:

        # get column specified by sort_by
        entity = stmt.column_descriptions[0]["entity"]
        column = getattr(entity, query_model.sort_by)

        if not column:
            return stmt

        # apply filter
        if query_model.q:
            stmt = filter(entity, column, stmt, query_model)

        # apply sort
        if query_model.order:
            stmt = sort(entity, column, stmt, query_model)

    return stmt
