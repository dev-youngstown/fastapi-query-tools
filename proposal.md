# FastAPI Query Tools Proposal

## Overview
The purpose of this project is to develop a standard way of filtering and sorting that integrates nicely with the orm. The initial supported orm for this project is intended to be [SQLAlchemy v1.4 - v2.0](https://www.sqlalchemy.org/)

## Goals
1. <b>Develop filtering utilities.</b> These utilites should apply filters to SQLAlchemy queries based on the params.
2. <b>Develop sorting utilities.</b> These utilites should apply order_by sorting to SQLAlchemy queries based on the params.
3. <b>Develop models for sort and filter.</b> These models should be able to be applied to any endpoint as [Annotated dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/#create-a-dependency-or-dependable).
4. <b>Provide ample documentation.</b> There is not really any nice way that filtering and sorting has been documented. The goal for this package is to provide the most comprehensive documentation.

## Methodology 

### Query Model


```python
class QueryModel(BaseModel):
    q: Optional[Any] = Field(None)
    sort_by: Optional[str] = Field(None)
    order: Optional[str] = Field(None)

```
Where `q` is the search string, `sort_by` is the column to reference, and `order` is the sort direction (asc, desc).

#### Model Usage

```python
@app.get("/some/endpoint")
async def some_endpoint(
     query: Annotated[QueryModel, Depends()],
):
     pass
```

### Query Functions

#### Query Filtering and Sorting

This function utilizes an existing query and will apply a filter and an order_by clause onto this query based on the query_model param and then return the query.

```python
def filter_and_sort(query: Query, query_model: QueryModel) -> Query:
        if query_model.sort_by:
                # get column specified by sort_by
                column = getattr(query.column_descriptions[0]['entity'], queryModel.sort_by)

                if not column:
                        return query
                
                # apply filter
                if query_model.q:
                        query = query.filter(column.icontains(query_model.q))
        
                # apply sort
                if query_model.order:
                        query = query.order_by(column.desc()) if query_model.order == 'desc' else query.order_by(column.asc())

        return query
```


#### Query Function Usage

```python
def get_multi(self, db: Session, query_model: QueryModel) -> Page[ModelType]:
    query = select(self.model)
    
    query = filter_and_sort(query, query_model)
    
    return paginate(db, query)
```

### Example Endpoint

```python
@router.get("/items", response_model=Page[schemas.Item])
def get_items(db: db_dep, query: Annotated[QueryModel, Depends()]):
    return crud.items.get_multi(db, query_model=query)
```

#### Request Query Params

```
q: 1
sort_by: "id"
order: "desc"
```


#### Request URL

```
http://localhost:8000/api/v1/resource/items?q=1&sort_by=id&order=desc
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
