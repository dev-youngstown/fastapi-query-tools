# FastAPI Query Tools Proposal

## Overview
The purpose of this project is to develop a standard way of filtering and sorting that integrates nicely with the orm. The initial supported orm for this project is intended to be [SQLAlchemy v1.4 - v2.0](https://www.sqlalchemy.org/)

## Goals
1. <b>Develop filtering utilities.</b> These utilites should apply filters to SQLAlchemy queries based on the params.
2. <b>Develop sorting utilities.</b> These utilites should apply order_by sorting to SQLAlchemy queries based on the params.
3. <b>Develop models for sort and filter.</b> These models should be able to be applied to any endpoint as [Annotated dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/#create-a-dependency-or-dependable).
4. <b>Provide ample documentation.</b> There is not really any nice way that filtering and sorting has been documented. The goal for this package is to provide the most comprehensive documentation.

## Methodology 

### Models

#### 1. Filter
Request model for accepting filter params

```python
from pydantic import BaseModel

class Filter(BaseModel):
        field: str
        value: Any

def get_filters(filters: Annotated[List[Filter] | None, Query()] = None) -> List[Dict[str, Any]]:
    return [{'field': f.field, 'value': f.value} for f in filters]

FilterDep = Annotated[List[Dict[str, Any]] , Depends(get_filters)]
```

#### 2. Sort
Request model for accepting sort params

```python
from pydantic import BaseModel

class Sort(BaseModel):
        field: str
        order: str # (This ideally will have validation and only accept "desc" or "asc" as the value)

def get_sorters(sorters: Annotated[List[Sort] | None, Query()] = None) -> List[Dict[str, str]]:
    return [{'field': s.field, 'order': s.order} for s in sorters]

SortDep = Annotated[List[Dict[str, str]], Depends(List[Sort])]
```

#### Model Usage

```python
@app.get("/some/endpoint")
async def some_endpoint(
      *,
      filters: FilterDep,
      sort: SortDep
):
     pass
```

### Query Functions

#### Query Filtering

This function utilizes an existing query and will apply filters onto this query based on the filters param and then return the query.
SQLAlchemy allows you to stack filters like so `query.filter(...).filter(...).filter(...)`

```python
def filter(query: Query, filters: List[Dict[str, Any]]) -> Query:
        if not filters:
                return query

        for filter in filters:
                query = query.filter(getattr(query.column_descriptions[0]['entity'], filter['field']) == filter['value'])

        return query
```

#### Query Sorting

This function utilizes an existing query and will apply the sorting based on the sorters param and then return the query. 
SQLAlchemy also allows you to stack order_by like so `query.order_by(...).order_by(...).order_by(...)`

```python
def sort(query: Query, sorters: List[Dict[str, str]]) -> Query:
        if not sorters:
                return query

        for sorter in sorters:
                column = getattr(query.column_descriptions[0]['entity'], sorter['field'])
                if sorter['order'] == 'desc':
                    query = query.order_by(column.desc())
                else:
                    query = query.order_by(column.asc())
        return query
```

#### Query Function Usage

```python
def get_multi(self, db: Session, filters: List[Dict[str, Any]] = [], sorters: List[Dict[str, str]] = []) -> Page[ModelType]:
    query = select(self.model)
    
    query = filter(query, filters)
    query = sort(query, sorters)
    
    return paginate(db, query)
```

### Testing
Please let me know if you think it would be worth adding unit tests to this project.
