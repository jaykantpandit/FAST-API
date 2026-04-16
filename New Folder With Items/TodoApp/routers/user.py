from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel, Field
from models import Users
from typing import Annotated
from database import SessionLocal
from sqlalchemy.orm import Session
from routers import auth
from .auth import get_current_user
from passlib.context import CryptContext


router = APIRouter(
    prefix='/user',
    tags=['user']
)


# creating DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

class UpdatePasswordRequest(BaseModel):
    old_password: str
    new_password: str

@router.get('/')
def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    users = db.query(Users).filter(Users.id == user.get('user_id')).first()
    result = []
    data = users.__dict__.copy()
    data.pop("hashed_password", None)
    sorted_data = dict(sorted(data.items()))
    result.append(sorted_data)
    return result
        
@router.put('/update_password', status_code=status.HTTP_204_NO_CONTENT)
def update_password(user: user_dependency, db: db_dependency, password_request: UpdatePasswordRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    user_model = db.query(Users).filter(Users.id == user.get('user_id')).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail='User not found')
    
    if not verify_password(password_request.old_password, user_model.hashed_password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")
    user_model.hashed_password = hash_password(password_request.new_password)
    db.commit()