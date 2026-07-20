from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas import EdgeCreate, EdgeOut

router = APIRouter()


@router.post("/edges", response_model=EdgeOut, status_code=status.HTTP_201_CREATED)
def create_edge(payload: EdgeCreate, db: Session = Depends(get_db)):
    if payload.latency <= 0:
        raise HTTPException(status_code=400, detail="latency must be greater than 0")
    try:
        edge = crud.create_edge(db, payload.source, payload.destination, payload.latency)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return EdgeOut.from_orm(edge)


@router.get("/edges", response_model=list[EdgeOut])
def list_edges(db: Session = Depends(get_db)):
    return [EdgeOut.from_orm(edge) for edge in crud.list_edges(db)]


@router.delete("/edges/{edge_id}", status_code=status.HTTP_200_OK)
def delete_edge(edge_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_edge(db, edge_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Edge not found")
    return {"ok": True}
