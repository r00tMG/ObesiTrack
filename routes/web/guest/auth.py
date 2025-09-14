import json

from fastapi import APIRouter, Body, Depends, HTTPException, status, Request, Form
from matplotlib.font_manager import json_load
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from starlette.templating import Jinja2Templates

from app import schemas_users, models
from app.database import get_db
from app.hash import verify_password, hash_password
from auth.auth_handler import sign_jwt

router = APIRouter(prefix="/web/guest")
templates=Jinja2Templates(directory="templates")

@router.get("/login",  response_class=HTMLResponse)
async def login(request:Request):
    token_expired = request.session.pop("token_expired", None)
    not_authorized = request.session.pop("not_authorized", None)
    not_authenticated = request.session.pop("not_authenticated", None)
    form_vide = request.session.pop("form_vide", None)
    user_not_found = request.session.pop("user_not_found", None)
    register_success = request.session.pop('register_success', None)
    return templates.TemplateResponse("guest/login.html", {
            "request":request,
            "token_expired":token_expired,
            "not_authorized":not_authorized,
            "not_authenticated":not_authenticated,
            "form_vide":form_vide,
            "user_not_found":user_not_found,
            "register_success":register_success
        })

@router.post("/login", response_class=HTMLResponse)
async def login(request:Request, email:str=Form(...), password:str=Form(...), db: Session=Depends(get_db)):
    if not email or not password:
        request.session["form_vide"] = {
            "status": status.HTTP_404_NOT_FOUND,
            "message": "Veuillez remplir le formulaire"
        }
        response = RedirectResponse(
            url="/web/guest/login",
            status_code=status.HTTP_303_SEE_OTHER
        )
        return response

    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not verify_password(password, user.password):
        request.session["user_not_found"] = {
            "status": status.HTTP_404_NOT_FOUND,
            "message": "Vos données sont incorrectes"
        }
        response = RedirectResponse(
            url="/web/guest/login",
            status_code=status.HTTP_303_SEE_OTHER,
        )
        return response
    if (email == user.email) and verify_password(password, user.password) and (user.role.value == "user"):
        token = sign_jwt(user.email)
        id_user = user.id
        response = RedirectResponse(url = "/", status_code=status.HTTP_303_SEE_OTHER)
        request.session['success_login'] = {
            "status": status.HTTP_404_NOT_FOUND,
            "message": "Vous êtes connecté avec succés"
        }
        response.set_cookie(key="token", value=token.get("access_token"), secure=True, httponly=True)
        response.set_cookie(key="id_user", value=id_user, secure=True, httponly=True)
        return response
    elif (email == user.email) and verify_password(password, user.password) and (user.role.value == "admin"):
        token = sign_jwt(user.email)
        response = RedirectResponse(url = "/web/admin/users", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="token", value=token.get("access_token"), secure=True, httponly=True)
        return response
    else:
        request.session["not_authenticated"] = {
            "status": status.HTTP_403_FORBIDDEN,
            "message": "Impossible de vous connecté, veuillez remplir les valeurs correctes"
        }
        response = RedirectResponse(
            url="/web/guest/login",
            status_code=status.HTTP_303_SEE_OTHER
        )
        return response

@router.get("/register")
async def register(request:Request):
    password_no_conform = request.session.pop("password_no_conform", None)
    form_vide = request.session.pop("form_vide", None)
    return templates.TemplateResponse("/guest/register.html", {
        "request":request,
        "form_vide":form_vide ,
        "password_no_conform":password_no_conform,
    })

@router.post("/register")
async def register(
        request:Request,
        fullname:str=Form(...),
        email:str=Form(...),
        password:str=Form(...),
        confirm_password:str=Form(...),
        db:Session=Depends(get_db)
):
    if not fullname or not email or not password or not confirm_password:
        request.session['form_vide'] = {
            "status":status.HTTP_400_BAD_REQUEST,
            "message":"Veuillez verifier vos requêtes"
        }
        response = RedirectResponse(url="/web/guest/register", status_code=status.HTTP_303_SEE_OTHER)
        return response
    if password != confirm_password:
        request.session["password_no_conform"] = {
            "status": status.HTTP_400_BAD_REQUEST,
            "message": "Vos mots de passe ne sont pas conformes"
        }
        response = RedirectResponse(url="/web/guest/register", status_code=status.HTTP_303_SEE_OTHER)
        return response
    new_user = models.User(
        fullname=fullname,
        email=email,
        password=hash_password(password)
    )
    if not new_user:
        request.session['form_vide'] = {
            "status": status.HTTP_204_NO_CONTENT,
            "message": "Aucun utilisateur n'est soumis"
        }
        response = RedirectResponse(url="/web/guest/register", status_code=status.HTTP_303_SEE_OTHER)
        return response
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    request.session["register_success"] = {
        "status": status.HTTP_204_NO_CONTENT,
        "message": "Votre enregistrement a réussi"
    }
    response = RedirectResponse(url="/web/guest/login", status_code=status.HTTP_303_SEE_OTHER)
    return response
