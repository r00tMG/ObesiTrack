from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session

from app import schemas_users, models
from app.database import get_db
from auth.auth_bearer import JWTBearer

router = APIRouter(
    tags=["User"],
    prefix="/api/admin"
)


# Liste des utilisateurs
@router.get("/users", dependencies=[Depends(JWTBearer())], response_model=List[schemas_users.UserResponse])
async def index(db:Session=Depends(get_db)):
    users = db.query(models.User).all()
    return users

# Delete d'un utlissateur
@router.delete("/users/{id}", dependencies=[Depends(JWTBearer())])
async def destroy(id : int ,db:Session=Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    print(user)
    if not user:
        print('vrai')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Impossible de trouver utilisateur avec cet id:{id}")
    db.delete(user)
    db.commit()
    return {
        "status":status.HTTP_204_NO_CONTENT,
        "message":"Utilisateur supprimé avec succés"
    }

# Update role d'un utilisateurs
@router.post("/users/{id}", dependencies=[Depends(JWTBearer())], response_model=schemas_users.UserResponse)
async def update(request:schemas_users.UserUpdateSchemas = Body(...), id:int=2, db:Session=Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Impossible de trouver utilisateur avec cet id:{id}")
    user.update({
        "role":request.role
    }, synchronize_session=False)
    db.commit()
    return {
        "status":status.HTTP_201_CREATED,
        "message":"Utilisateur modifié avec succés",
        "guest":user.first()
    }




