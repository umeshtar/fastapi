from typing import Union, Annotated

from fastapi import FastAPI, Query
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    model_config = {
        'json_schema_extra': {
            'examples': [
                {
                    "name": "Foo",
                    "price": 35.4,
                    "is_offer": True,
                }
            ]
        }
    }
    name: str
    price: float
    is_offer: Union[bool, None] = None


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Annotated[Union[str, None], Query()] = None, item: Item = None):
    return {"item_id": item_id, "q": q}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.price, "item_id": item_id}
