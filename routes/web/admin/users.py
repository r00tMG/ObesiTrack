from typing import List

from fastapi import APIRouter, Depends, Request, status, Form
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates

from app import schemas_users, models
from app.database import get_db
from auth.auth_bearer import JWTBearer

router = APIRouter(
    prefix="/web/admin"
)

templates = Jinja2Templates(directory="templates")

@router.get(
    "/users",
    response_class=HTMLResponse,
    response_model=List[schemas_users.UserResponse],

)
async def index(request:Request,db:Session=Depends(get_db)):
    users = db.query(models.User).all()
    not_authorized = request.session.pop("not_authorized", None)
    error_delete = request.session.pop("error_delete", None)
    success_delete = request.session.pop("success_delete", None)
    return templates.TemplateResponse("/admin/users/index.html", {
        "request":request,
        "users":users,
        "not_authorized":not_authorized,
        "error_delete":error_delete,
        "success_delete":success_delete
    })

@router.post("/users/{id}")
async def destroy(request:Request, id:int, db:Session=Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:

        request.session['error_delete'] = {
            "status":status.HTTP_404_NOT_FOUND,
            "message":f"Impossible de trouver utilisateur avec cet id:{id}"
        }
        return RedirectResponse(url = "/web/admin/users", status_code=status.HTTP_303_SEE_OTHER)
    db.delete(user)
    db.commit()
    request.session['success_delete'] = {
        "status": status.HTTP_204_NO_CONTENT,
        "message": "Utilisateur supprimé avec succés"
    }
    return RedirectResponse(url="/web/admin/users", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/users/{id}")
async def update(request:Request, id:int, db:Session=Depends(get_db)):
    if not id:
        request.session["error_update"] = {
            "status":status.HTTP_404_NOT_FOUND,
            "message":f"Impossible de trouver un utilisateur avec id : {id}"
        }
        return RedirectResponse("/web/admin/users", status_code=status.HTTP_303_SEE_OTHER)
    user = db.query(models.User).filter(models.User.id == id).first()
    return templates.TemplateResponse("/admin/users/update.html", {
        "request":request,
        "user":user
    })

# Update role d'un utilisateurs
@router.post("/update/{id}", response_model=schemas_users.UserResponse)
async def update(request:Request, role:str=Form(...), id:int=2, db:Session=Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id)
    if not user:
        request.session['error_update'] = {
            "status": status.HTTP_404_NOT_FOUND,
            "message": f"Impossible de trouver utilisateur avec cet id:{id}"
        }
        return RedirectResponse(url="/web/admin/users", status_code=status.HTTP_303_SEE_OTHER)
    user.update({
        "role":role
    }, synchronize_session=False)
    db.commit()
    request.session['success_update'] = {
        "status": status.HTTP_201_CREATED,
        "message": "Utilisateur modifié avec succés"
    }
    return RedirectResponse(url="/web/admin/users", status_code=status.HTTP_303_SEE_OTHER)




