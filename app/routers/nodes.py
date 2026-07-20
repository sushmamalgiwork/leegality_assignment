from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas import NodeCreate, NodeOut

router = APIRouter()


@router.post("/nodes", response_model=NodeOut, status_code=status.HTTP_201_CREATED)
def create_node(payload: NodeCreate, db: Session = Depends(get_db)):
    existing = crud.get_node_by_name(db, payload.name)
    if existing:
        raise HTTPException(status_code=400, detail="Node already exists")
    node = crud.create_node(db, payload.name)
    return node


@router.get("/nodes", response_model=list[NodeOut])
def list_nodes(db: Session = Depends(get_db)):
    return crud.list_nodes(db)


@router.delete("/nodes/{node_id}", status_code=status.HTTP_200_OK)
def delete_node(node_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_node(db, node_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Node not found")
    return {"ok": True}
