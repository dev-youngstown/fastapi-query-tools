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

def get_filters(filters: Annotated[str | None, Query()] = None) -> list[Filter]:
        if filters is None:
                return []

        # Will need to add some validation to make sure json is valid

        loaded_filters = json.loads(filters)
        filters = TypeAdapter(List[Filter]).validate_python(loaded_filters)
        return filters

FilterDep = Annotated[List[Filter], Depends(get_filters)]
```

#### 2. Sort
Request model for accepting sort params

```python
from pydantic import BaseModel

class Sort(BaseModel):
        field: str
        order: str # (This ideally will have validation and only accept "desc" or "asc" as the value)

def get_sorters(sorters: Annotated[str | None, Query()] = None) -> List[Sort]:
        if sorters is None:
                return []

        # Will need to add some validation to make sure json is valid
    
        loaded_sorters = json.loads(sorters)
        sorters = TypeAdapter(List[Sort]).validate_python(loaded_sorters)
        return sorters

SortDep = Annotated[List[Sort], Depends(get_sorters)]

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
def filter(query: Query, filters: List[Filter]) -> Query:
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
def sort(query: Query, sorters: List[Sort]) -> Query:
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
def get_multi(self, db: Session, filters: List[Filter] = [], sorters: List[Sort] = []) -> Page[ModelType]:
    query = select(self.model)
    
    query = filter(query, filters)
    query = sort(query, sorters)
    
    return paginate(db, query)
```

### Example Endpoint

```python
@router.get("items", response_model=Page[schemas.Item])
def get_items(db: db_dep, filters: FilterDep, sorters: SortDep):
    return crud.items.get_multi(db, filters, sorters)
```

#### Request Query Params
The query params should be sent over as stringified json

filters
```
'[{"field":"id","value":1}, {"field":"name","value":"Item 1"}]'
```

sorters
```
'[{"field":"id","order":"desc"}]'
```

#### Request URL

```
http://localhost:8000/api/v1/resource/items?filters=%5B%20%20%20%20%20%7B%22field%22%3A%22value1%22%2C%22value%22%3A1%7D%2C%20%20%20%20%20%7B%22field%22%3A%22value2%22%2C%22value%22%3A%22value2%22%7D%20%5D&sorters=%5B%7B%22field%22%3A%22id%22%2C%22order%22%3A%22desc%22%7D%5D
```


#### Response

```
{
  "total": 1,
  "items": [
    {
      "id": 1,
      "name": "Item 1",
      "description": "Description 1"
    }
  ],
  "page": 1,
  "size": 10,
  "pages": 1,      
}
```

### Testing
Please let me know if you think it would be worth adding unit tests to this project.
