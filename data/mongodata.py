from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb://ladadmin:1234pass@mongo:27017/")
db = client.get_database("mongodb")
orders_collection = db.get_collection("orders")
services_collection = db.get_collection("services")

services_data = [
    {"id_s": 1, "category": "Cleaning", "name_ser": "Standard Cleaning", "price": 70.0},
    {"id_s": 2, "category": "IT", "name_ser": "Software Installation", "price": 100.0},
]

orders_data = [
    {"id_o": 1, "id_us": 101, "id_s": 1, "price": 70.0, "date": datetime.now(), "status": "new"},
    {"id_o": 2, "id_us": 102, "id_s": 2, "price": 100.0, "date": datetime.now(), "status": "new"},
]

def init_services_db():
    services_collection.delete_many({})
    if services_collection.count_documents({}) == 0:
        services_collection.insert_many(services_data)
        print("Services collection has been initialized with predefined data.")
    else:
        print("Services collection already contains data.")

def init_orders_db():
    orders_collection.delete_many({})
    if orders_collection.count_documents({}) == 0:
        orders_collection.insert_many(orders_data)
        print("Orders collection has been initialized with predefined data.")
    else:
        print("Orders collection already contains data.")

init_services_db()
init_orders_db()