<div align="center">
<img alt="license" src="https://img.shields.io/badge/License-MIT-lightgrey">
<img alt="black" src="https://img.shields.io/badge/code%20style-black-000000.svg">
</div>

## Introduction

`fastapi-query-tools` is a Python library designed to simplify filtering and sorting in FastAPI applications. 
It provides a set of utility functions and data models to help you filter, sort, and order your data to be returned to your clients.

`fastapi-query-tools` is built on top of the popular `fastapi` library. It is currently designed to work with `SQLAlchemy`, but support for other databases may be added in the future.
It is compatible with Python 3.10 and higher.

Features:
* Simplifies filtering and sorting in FastAPI applications.
* Supports a query, a sort by, and an order by system.
* Works with `SQLAlchemy`.
* Compatible with Python 3.10 and higher.

## Installation

```bash
pip install fastapi-query-tools
```

## Quickstart

All you need to do is to add the `Filter` dependency to the endpoint params and call `filter_and_sort` function
on data you want to filter and/or sort.

```py
from fastapi import FastAPI, Depends
from sqlalchemy import select

# import all you need from fastapi-query-tools
from fastapi_query_tools import Filter, filter_and_sort

app = FastAPI()  # create FastAPI app


@app.get('/items')
async def get_items(*, db: Session = Depends(get_db), filter: Filter) -> List[ItemOut]:
    stmt = select(Item)
    query = filter_and_sort(stmt, filter)
    return db.execute(query).scalars().all() # filter and sort data and return
```

## Example Request
    
```http
curl -X 'GET' \
  'http://localhost:8000/api/items?q=item&sort_by=name&order=desc' \
  -H 'accept: application/json' \
```

Where `q` is a query, `sort_by` is a field (column) to sort by, and `order` (asc, desc) is an order of sorting.
