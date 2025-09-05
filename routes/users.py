from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session

from app import schemas, models
from app.database import get_db
from app.hash import hash_password, verify_password
from auth.auth_bearer import JWTBearer
from auth.auth_handler import sign_jwt

router = APIRouter(
    tags=["User"]
)

@router.post("/register")
async def register(request:schemas.UserRegisterSchemas=Body(...), db:Session=Depends(get_db)):
    if not request:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Veuillez verifier vos requêtes")
    if request.password != request.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Vos mots de passe ne sont pas conformes")
    new_user = models.User(
        fullname=request.fullname,
        email=request.email,
        password=hash_password(request.password)
    )
    if not new_user:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="Aucun utilisateur n'est soumis")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return sign_jwt(new_user.email)

@router.post("/login")
async def login(request:schemas.UserLoginSchemas=Body(...), db: Session=Depends(get_db)):
    print("test1")
    user = db.query(models.User).filter(models.User.email == request.email).first()
    print("test2")
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Vos données sont incorrectes")
    if not request.email or not request.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Veuillez remplir les champs")
    if (request.email == user.email) and verify_password(request.password, user.password):
        return sign_jwt(user.email)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Impossible de vous connecté, veuillez remplir les valeurs correctes")

@router.get("/users", dependencies=[Depends(JWTBearer())], response_model=List[schemas.UserResponse])
async def index(db:Session=Depends(get_db)):
    users = db.query(models.User).all()
    return users