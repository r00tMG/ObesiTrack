import os

import joblib
import pandas as pd
from fastapi import APIRouter, Request, Depends, Form, status
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from app import models
from app.database import get_db

router = APIRouter(
    prefix="/web/users"
)

templates = Jinja2Templates(directory="templates")
model = joblib.load("./modelisations/models/best_model.pkl")
#print(model)
@router.post("/predict")
async def predict(
        request:Request,
        genre:str = Form(...),
        age:int = Form(...),
        height:int = Form(...),
        weight:int = Form(...),
        family_history_with_overweight:str = Form(...),
        favc:str = Form(...),
        fcvc:int = Form(...),
        ncp:int = Form(...),
        caec:str = Form(...),
        smoke:str = Form(...),
        ch2o:int = Form(...),
        scc:str = Form(...),
        faf:int = Form(...),
        tue:int = Form(...),
        calc:str = Form(...),
        mtrans:str = Form(...),
        db:Session=Depends(get_db)):
    data = pd.DataFrame({
        "Genre" : genre,
        "Age" : age,
        "IMC" : weight / (height ** 2),
        "family_history_with_overweight" : family_history_with_overweight,
        "FAVC" : favc,
        "FCVC" : fcvc,
        "NCP" : ncp,
        "caec" : caec,
        "smoke" : smoke,
        "ch2o" : ch2o,
        "scc" : scc,
        "faf" : faf,
        "tue" : tue,
        "calc" : calc,
        "mtrans" : mtrans
    }, index = [0])
    for col in data.select_dtypes(include="object").columns:
        le = LabelEncoder()
        data[col] = le.fit_transform(data[col])

    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(data)
    prediction = model.predict(data_scaled)
    proba = model.predict_proba(data_scaled).tolist()
    print(prediction, max(proba))
    id_user = request.session.get("id_user")
    print("Id user", id_user)
    if not prediction or not proba:
        request.session['error_predict'] = {
            "status":status.HTTP_404_NOT_FOUND,
            "message":"Veuillez réessayer votre prediction"
        }
        return RedirectResponse("/web/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    new_prediction = models.Prediction(
        user_id = id_user,
        result=prediction[0],
        score=round(max(proba[0]) * 100, 2)
    )
    db.add(new_prediction)
    db.commit()
    db.refresh(new_prediction)
    request.session['success_add_prediction'] = {
        "status" : status.HTTP_201_CREATED,
        "message": "La prediction a été ajouté à votre historique"
    }

    return RedirectResponse(url="/web/dashboard", status_code=status.HTTP_303_SEE_OTHER)
