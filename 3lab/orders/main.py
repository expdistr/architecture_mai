from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from typing import List
from datetime import datetime

app = FastAPI()

# Параметры подключения к MongoDB
client = MongoClient("mongodb://ladadmin:1234pass@mongo:27017")
db = client.mongodb

class Order(BaseModel):
    id_o: int
    id_us: int
    id_s: int
    price: float
    date: datetime
    status: str

@app.post("/orders/", response_model=Order)
def create_order(order: Order):
    d = dict(order)
    existing_order = list(db.orders.find({"id_o": d["id_o"]}, {"_id": 0}))
    if not len(existing_order):
        raise HTTPException(status_code=400, detail="Order already exists")
    db.orders.insert_one(order.dict())
    return order

@app.get("/orders/{order_id}", response_model=Order)
def read_order(order_id: int):
    order = list(db.orders.find({"id_o": order_id}, {"_id": 0}))[0]
    if not len(order):
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.get("/orders/service/{service_id}", response_model=List[Order])
def read_orders_by_service(service_id: int):
    orders = list(db.orders.find({"id_s": service_id}))
    if not orders:
        raise HTTPException(status_code=404, detail="Orders for the given service not found")
    return orders

@app.get("/orders/user/{user_id}", response_model=List[Order])
def read_orders_by_user(user_id: int):
    orders = list(db.orders.find({"id_us": user_id}))
    if not orders:
        raise HTTPException(status_code=404, detail="Orders for the given user not found")
    return orders

@app.get("/orders/")
async def get_all_orders():
    results = list(db.orders.find({}, {"_id": 0}))
    print(results)
    return results