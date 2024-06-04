from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List
import requests
from circuitbreaker import CircuitBreaker
from datetime import datetime

app = FastAPI()


cb_users = CircuitBreaker(failure_threshold=3, recovery_timeout=60)
cb_orders = CircuitBreaker(failure_threshold=3, recovery_timeout=60)
cb_services = CircuitBreaker(failure_threshold=3, recovery_timeout=60)

USER_SERVICE_URL = "http://users6:8080"

class User(BaseModel):
    id: int
    login: str
    password: str
    name: str
    last_name: str
    mail: str
    
    class Config:
        arbitrary_types_allowed=True

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    with cb_users:
        response = requests.get(f"{USER_SERVICE_URL}/users/{user_id}")
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="User not found")
    return response.json()

ORDERS_SERVICE_URL = "http://orders6:8080"

class Order(BaseModel):
    id_o: int
    id_us: int
    id_s: int
    price: float
    date: datetime
    status: str

@app.get("/orders/{order_id}", response_model=Order)
async def read_order(order_id: int):
    with cb_orders:
        response = requests.get(f"{ORDERS_SERVICE_URL}/orders/{order_id}")
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Order not found")
    return response.json()

# Services Service
SERVICES_SERVICE_URL = "http://services6:8080"

class Service(BaseModel):
    id_s: int
    category: str
    name_ser: str
    price: float

@app.get("/services/{service_id}", response_model=Service)
async def read_service(service_id: int):
    with cb_services:
        response = requests.get(f"{SERVICES_SERVICE_URL}/services/{service_id}")
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Service not found")
    return response.json()