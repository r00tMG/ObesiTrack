import os

from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from starlette.middleware.sessions import SessionMiddleware
from app import models, database
from app.dependencies import get_admin_user, get_current_user
from routes.api.guest import auth
from routes.api.admin import users
from routes.web import dash
from routes.web.guest import auth as auth_web
from routes.web.admin import users as users_web
from app.dependencies_web import get_current_user as get_current_user_web
from app.dependencies_web import get_admin_user as get_admin_user_web
from routes.web.user import prediction

load_dotenv()

SECRET_KEY_MIDDLEWARE = os.getenv("SECRET_KEY_MIDDLEWARE")

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()


app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY_MIDDLEWARE)

# API
app.include_router(users.router, dependencies=[Depends(get_admin_user)])
app.include_router(auth.router, dependencies=[Depends(get_current_user)])

# WEB
app.include_router(users_web.router, dependencies=[Depends(get_admin_user_web)])
app.include_router(dash.router, dependencies=[Depends(get_current_user_web)])
app.include_router(prediction.router, dependencies=[Depends(get_current_user_web)])
app.include_router(auth_web.router)

