from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from typing import List

app = FastAPI()

# Параметры подключения к MongoDB
client = MongoClient("mongodb://ladadmin:1234pass@mongo:27017")
db = client.mongodb

# Модель Pydantic для услуги
class Service(BaseModel):
    id_s: int
    category: str
    name_ser: str
    price: float

# REST API эндпоинты
@app.post("/services/", response_model=Service)
def create_service(service: Service):
    d = dict(service)
    existing_service = list(db.services.find({"id_s": d["id_s"]}, {"_id": 0}))
    if not len(existing_service):
        raise HTTPException(status_code=400, detail="Service already exists")
    db.services.insert_one(service.dict())
    return service

@app.get("/services/", response_model=List[Service])
def read_services():
    services = list(db.services.find({}, {"_id": 0}))
    print(services)
    return [Service(**service) for service in services ]

@app.get("/services/{service_id}", response_model=Service)
def read_service(service_id: int):
    service = list(db.services.find({"id_s": service_id}, {"_id": 0}))[0]
    if not len(service):
        raise HTTPException(status_code=404, detail="Service not found")
    return service

@app.put("/services/{service_id}", response_model=Service)
def update_service(service_id: int, service: Service):
    result = db.services.replace_one({"id_s": service_id}, service.dict())
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Service not found")
    return service

@app.delete("/services/{service_id}", response_model=Service)
def delete_service(service_id: int):
    service = db.services.find_one_and_delete({"id_s": service_id})
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return service