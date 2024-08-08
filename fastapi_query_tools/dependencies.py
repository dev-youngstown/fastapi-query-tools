from typing import Annotated
from fastapi import Depends
from models import QueryModel

Filter = Annotated[QueryModel, Depends(QueryModel)]
