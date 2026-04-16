from datetime import datetime, timedelta, timezone
from typing import Annotated, Literal
from enum import Enum
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from database import SessionLocal
from models import Users
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWSError
from fastapi.templating import Jinja2Templates



router = APIRouter(
    prefix='/auth',
    tags=['auth']
)
bcrypt_context = CryptContext(schemes=['bcrypt'])
SECRETE_KEY = 'a84657120e7287dbba67b7cedb8edf938a4d79311ffdf96444b3420624bab42b5c2d633d0f71facb8e92e4f9c554283eef16dbd7'
ALGORITH = 'HS256'

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

class UserRole(str, Enum):
    admin = "admin"
    editor = "editor"
    viewer = "viewer"



class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: Literal["admin", "editor", "viewer"]

    
    model_config = {
        'json_schema_extra': {
            "example":{
                "username": "username",
                "email": "email@gmail.com",
                "first_name": "John",
                "last_name": "Mac",
                "password": "000",
                "role": "admin"
            }
        }
    }

class Token(BaseModel):
    access_token: str
    token_type: str


# creating DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

templated = Jinja2Templates(directory='templates')
#### Pages ###

# @router.get("/login-page")
# def render_login_page(request: Request):
#     return templated.TemplateResponse('login.html', {"request": request})

# @router.get("/register-page")
# def render_register_page(request: Request):
#     return templated.TemplateResponse('register.html', {"request": request})



### End Points ###

def authenticate_user(username: str, password: str, db: db_dependency):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password): 
        return False
    return user

def create_access_token(username: str, user_id: int, role: str, expire_delta: timedelta):
    encode = {'sub': username, 'id':user_id, 'role': role
    }
    expire =  datetime.now(timezone.utc) + expire_delta
    encode.update({'exp': expire})
    return jwt.encode(encode, SECRETE_KEY, algorithm=ALGORITH)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRETE_KEY, algorithms=[ALGORITH])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')

        if user_id is None or username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='could not validate user')
        return {'username': username, 'user_id': user_id, 'role': user_role}
    except JWSError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='could not validate user')


@router.post("/", status_code= status.HTTP_201_CREATED)
def create_user(db: db_dependency,
                 create_usaer_request: CreateUserRequest):
    existing = db.query(Users).filter(Users.username == create_usaer_request.username).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")
    user = Users(
            email = create_usaer_request.email,
            username = create_usaer_request.username,
            first_name = create_usaer_request.first_name,
            last_name = create_usaer_request.last_name,
            hashed_password = bcrypt_context.hash(create_usaer_request.password),
            is_active = True,
            role = create_usaer_request.role
        )
    db.add(user)
    db.commit()
 


@router.post("/token", response_model=Token)
def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='could not validate user')
    token = create_access_token(username=user.username, user_id=user.id, role=user.role, expire_delta=timedelta(minutes=24))
    return {'access_token': token, 'token_type': 'bearer'}