# Python: the same app with plain def handlers (slower setup)
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    price: float
    qty: int


class Order(BaseModel):
    items: list[Item]


@app.get("/api/user/{id}")
def user(id: int):
    return {"id": id, "name": f"user{id}", "email": f"user{id}@example.com", "roles": ["reader", "writer"]}


@app.post("/api/orders")
def order(o: Order):
    total = sum(i.price * i.qty for i in o.items)
    return {"items": len(o.items), "total": total}
