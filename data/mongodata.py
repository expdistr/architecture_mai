from pymongo import MongoClient
from datetime import datetime

# Инициализация клиента MongoDB для servicesdb
client = MongoClient("mongodb://ladadmin:1234pass@mongo:27017/")
db = client.get_database("mongodb")
orders_collection = db.get_collection("orders")
services_collection = db.get_collection("services")

# Данные для начального заполнения servicesdb
services_data = [
    {"id_s": 1, "category": "Cleaning", "name_ser": "Standard Cleaning", "price": 70.0},
    {"id_s": 2, "category": "IT", "name_ser": "Software Installation", "price": 100.0},
    # Добавьте дополнительные услуги здесь
]

# Данные для начального заполнения ordersdb
orders_data = [
    {"id_o": 1, "id_us": 101, "id_s": 1, "price": 70.0, "date": datetime.now(), "status": "new"},
    {"id_o": 2, "id_us": 102, "id_s": 2, "price": 100.0, "date": datetime.now(), "status": "new"},
    # Добавьте дополнительные заказы здесь
]

# Функция для инициализации и заполнения базы данных services
def init_services_db():
    services_collection.delete_many({})
    if services_collection.count_documents({}) == 0:
        services_collection.insert_many(services_data)
        print("Services collection has been initialized with predefined data.")
    else:
        print("Services collection already contains data.")

# Функция для инициализации и заполнения базы данных orders
def init_orders_db():
    orders_collection.delete_many({})
    if orders_collection.count_documents({}) == 0:
        orders_collection.insert_many(orders_data)
        print("Orders collection has been initialized with predefined data.")
    else:
        print("Orders collection already contains data.")

# Вызов функций инициализации
init_services_db()
init_orders_db()