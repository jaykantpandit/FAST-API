from fastapi import FastAPI, Request
import models
from database import SessionLocal, engine
from routers import auth, todos, admin, user
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
app = FastAPI()


models.Base.metadata.create_all(bind=engine)
template = Jinja2Templates(directory='templates')
app.mount('/static', StaticFiles(directory='static'), name='static')
@app.get("/")
def test(request: Request):
    return template.TemplateResponse('home.html', {"request": request})

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(user.router)

