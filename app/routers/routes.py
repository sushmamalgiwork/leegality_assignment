from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app import crud
from app.database import get_db
from app.schemas import RouteHistoryOut, RouteQuery, RouteResult

router = APIRouter()


@router.post("/routes/shortest", response_model=RouteResult)
def shortest_route(payload: RouteQuery, db: Session = Depends(get_db)):
    try:
        total_latency, path = crud.shortest_path(db, payload.source, payload.destination)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if total_latency is None or path is None:
        crud.log_route_history(db, payload.source, payload.destination, None, None)
        return JSONResponse(
            status_code=404,
            content={"error": f"No path exists between {payload.source} and {payload.destination}"},
        )

    crud.log_route_history(db, payload.source, payload.destination, total_latency, path)
    return {"total_latency": total_latency, "path": path}


@router.get("/routes/history", response_model=list[RouteHistoryOut])
def route_history(
    source: Optional[str] = None,
    destination: Optional[str] = None,
    limit: Optional[int] = Query(default=None, ge=1),
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    return [RouteHistoryOut.from_orm(entry) for entry in crud.list_route_history(db, source=source, destination=destination, limit=limit, date_from=date_from, date_to=date_to)]
