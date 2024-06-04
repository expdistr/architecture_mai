from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List
import requests
from circuitbreaker import CircuitBreaker
import datetime

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth")

# Circuit Breaker configuration
cb_users = CircuitBreaker(fail_max=3, reset_timeout=60)
cb_orders = CircuitBreaker(fail_max=3, reset_timeout=60)
cb_services = CircuitBreaker(fail_max=3, reset_timeout=60)

# User Service
USER_SERVICE_URL = "http://localhost:8080"

class User(BaseModel):
    id: int
    login: str
    password: str
    name: str
    last_name: str
    mail: str

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int, token: str = Depends(oauth2_scheme)):
    with cb_users:
        response = requests.get(f"{USER_SERVICE_URL}/users/{user_id}", headers={"Authorization": f"Bearer {token}"})
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="User not found")
    return response.json()

# Orders Service
ORDERS_SERVICE_URL = "http://localhost:8082"

class Order(BaseModel):
    id_o: int
    id_us: int
    id_s: int
    price: float
    date: datetime
    status: str

@app.get("/orders/{order_id}", response_model=Order)
async def read_order(order_id: int, token: str = Depends(oauth2_scheme)):
    with cb_orders:
        response = requests.get(f"{ORDERS_SERVICE_URL}/orders/{order_id}", headers={"Authorization": f"Bearer {token}"})
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Order not found")
    return response.json()

# Services Service
SERVICES_SERVICE_URL = "http://localhost:8081"

class Service(BaseModel):
    id_s: int
    category: str
    name_ser: str
    price: float

@app.get("/services/{service_id}", response_model=Service)
async def read_service(service_id: int, token: str = Depends(oauth2_scheme)):
    with cb_services:
        response = requests.get(f"{SERVICES_SERVICE_URL}/services/{service_id}", headers={"Authorization": f"Bearer {token}"})
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Service not found")
    return response.json()