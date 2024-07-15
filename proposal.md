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

FilterDep = Annotated[List[Filter], Depends(List[Filter])]
```

#### 2. Sort
Request model for accepting sort params

```python
from pydantic import BaseModel

class Sort(BaseModel):
        field: str
        order: str # (This ideally will have validation and only accept "desc" or "asc" as the value)

SortDep = Annotated[List[Sort], Depends(List[Sort])]
```

### Model Usage

```python
@app.get("/some/endpoint")
async def some_endpoint(
      *,
      filters: FilterDep,
      sort: SortDep
):
     pass
```
