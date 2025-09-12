from fastapi import APIRouter, Body, Depends, HTTPException, status, Request, Form
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse, RedirectResponse
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
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail="Veuillez remplir le formulaire",
            headers={"Location": "/web/guest/login"}
        )
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not verify_password(password, user.password):
        request.session["user_not_found"] = {
            "status": status.HTTP_404_NOT_FOUND,
            "message": "Vos données sont incorrectes"
        }
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail="Vos données sont incorrectes",
            headers={"Location": "/web/guest/login"}
        )
    if (email == user.email) and verify_password(password, user.password) and (user.role.value == "user"):
        request.session['token'] = sign_jwt(user.email)
        request.session['id_user'] = user.id
        return RedirectResponse(url = "/", status_code=status.HTTP_303_SEE_OTHER)
    elif (email == user.email) and verify_password(password, user.password) and (user.role.value == "admin"):
        request.session['token'] = sign_jwt(user.email)
        return RedirectResponse(url = "/web/admin/users", status_code=status.HTTP_303_SEE_OTHER)
    else:
        request.session["not_authenticated"] = {
            "status": status.HTTP_403_FORBIDDEN,
            "message": "Impossible de vous connecté, veuillez remplir les valeurs correctes"
        }
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail="Impossible de vous connecté, veuillez remplir les valeurs correctes",
            headers={"Location": "/web/guest/login"}
        )

@router.get("/register")
async def register(request:Request):
    password_no_conform = request.session.pop("password_no_conform", None)
    form_vide = request.session.pop("form_vide", None)
    return templates.TemplateResponse("/guest/register.html", {
        "request":request,
        "form_vide":form_vide,
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
        return RedirectResponse(url="/web/guest/register", status_code=status.HTTP_303_SEE_OTHER)
    if password != confirm_password:
        request.session['password_no_conform'] = {
            "status": status.HTTP_400_BAD_REQUEST,
            "message": "Vos mots de passe ne sont pas conformes"
        }
        return RedirectResponse(url="/web/guest/register", status_code=status.HTTP_303_SEE_OTHER)
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
        return RedirectResponse(url="/web/guest/register", status_code=status.HTTP_303_SEE_OTHER)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    request.session['register_success'] = {
        "status": status.HTTP_204_NO_CONTENT,
        "message": "Votre enregistrement a réussi"
    }
    return RedirectResponse(url="/web/guest/login", status_code=status.HTTP_303_SEE_OTHER)
