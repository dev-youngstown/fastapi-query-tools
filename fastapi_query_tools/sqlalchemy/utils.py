from sqlalchemy import Select
from fastapi_query_tools.models import QueryModel


def filter_and_sort(stmt: Select, query_model: QueryModel) -> Select:
    if query_model.sort_by:
        # get column specified by sort_by
        column = getattr(stmt.column_descriptions[0]["entity"], query_model.sort_by)

        if not column:
            return stmt

        # apply filter
        if query_model.q:
            stmt = stmt.filter(column.icontains(query_model.q))

        # apply sort
        if query_model.order:
            stmt = (
                stmt.order_by(column.desc())
                if query_model.order == "desc"
                else stmt.order_by(column.asc())
            )

    return stmt
