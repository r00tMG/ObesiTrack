from fastapi import APIRouter, Request, Depends
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.dependencies_web import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="templates")
@router.get("/", response_class=HTMLResponse, dependencies=[Depends(get_current_user)])
async def dash(request:Request, db:Session=Depends(get_db)):
    id_user = request.session.get("id_user")
    predictions = db.query(models.Prediction).filter(models.Prediction.user_id == id_user).all()

    success_add_prediction = request.session.pop("success_add_prediction", None)
    not_authorized = request.session.pop("not_authorized", None)
    return templates.TemplateResponse("dashboard.html", {
        "request":request,
        "not_authorized":not_authorized,
        "success_add_prediction":success_add_prediction,
        "predictions":predictions
    })

