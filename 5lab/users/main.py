from fastapi import FastAPI, HTTPException, Query, Depends, status, Request
from pydantic import BaseModel
import hashlib
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi.security import OAuth2PasswordBearer, OAuth2, OAuth2PasswordRequestForm
import jwt
import redis
from redis.exceptions import ConnectionError, TimeoutError
import json

REDIS_HOST = 'redis'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_TIMEOUT = 1
REDIS_POOL_SIZE = 10

redis_client = redis.StrictRedis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    socket_timeout=REDIS_TIMEOUT,
    socket_connect_timeout=REDIS_TIMEOUT,
    connection_pool=redis.ConnectionPool(max_connections=REDIS_POOL_SIZE)
)

SQLALCHEMY_DATABASE_URL = "postgresql://lada:lada@postgres:5432/archdb"

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    login = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    last_name = Column(String(255))
    mail = Column(String(255))

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth")

SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"

class UserAuth(BaseModel):
    username: str
    password: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_from_cache(user_id: int):
    cache_key = f"user:{user_id}"
    try:
        user_data = redis_client.get(cache_key)
        if user_data:
            return User(**json.loads(user_data))
    except (ConnectionError, TimeoutError):
        pass
    return None

def set_user_in_cache(user: User):
    cache_key = f"user:{user.id}"
    user_data = {
        "id": user.id,
        "login": user.login,
        "password": user.password,
        "name": user.name,
        "last_name": user.last_name,
        "mail": user.mail
    }
    try:
        redis_client.set(cache_key, json.dumps(user_data), ex=3600)  # 1 hour
    except (ConnectionError, TimeoutError):
        pass


@app.post("/auth")
async def authenticate_user(user: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    db_user = db.query(User).filter(User.login == user.username).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    if not hashlib.sha256(user.password.encode()).hexdigest() == db_user.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = jwt.encode({"user_id": db_user.id}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

class UserCreate(BaseModel):
    login: str
    name: str
    last_name: str = None
    mail: str = None
    password: str

class UserUpdate(BaseModel):
    id: int
    login: str = None
    name: str = None
    last_name: str = None
    mail: str = None


@app.post("/users/")
def create_user(user: UserCreate, db=Depends(get_db)):
    db_user = User(
        login=user.login,
        name=user.name,
        last_name=user.last_name,
        mail=user.mail,
        password=hashlib.sha256(user.password.encode()).hexdigest()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"id": db_user.id}

@app.put("/users/{user_id}")
async def update_user(user_id: int, user: UserUpdate, db=Depends(get_db), token: str = Depends(oauth2_scheme)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    update_data = user.dict(exclude_unset=True)
    if 'password' in update_data:
        update_data['password'] = hashlib.sha256(update_data['password'].encode()).hexdigest()
    for key, value in update_data.items():
        setattr(db_user, key, value)
    db.commit()
    return {"message": "User updated successfully"}

@app.get("/users/{user_id}")
async def get_user(user_id: int, db=Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = get_user_from_cache(user_id)
    if user:
        return user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    set_user_in_cache(user)
    return user

@app.delete("/users/{user_id}")
async def delete_user(user_id: int, db=Depends(get_db), token: str = Depends(oauth2_scheme)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"message": "User successfully removed"}

@app.get("/search_by_name")
async def search_by_name(name: str = Query(None, min_length=1), last_name: str = Query(None, min_length=1), db=Depends(get_db), token: str = Depends(oauth2_scheme)):
    results = db.query(User).filter(User.name.ilike(f'{name}%'), User.last_name.ilike(f'{last_name}%')).all()
    return results

@app.get("/search_by_login")
async def search_by_login(login: str = Query(None, min_length=1), db=Depends(get_db), token: str = Depends(oauth2_scheme)):
    results = db.query(User).filter(User.login.ilike(f'{login}%')).all()
    return results