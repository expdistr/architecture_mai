from fastapi import FastAPI, HTTPException, Query, Depends, status, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import hashlib
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi.security import OAuth2PasswordBearer, OAuth2, OAuth2PasswordRequestForm
import jwt


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
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

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
