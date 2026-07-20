from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class NodeCreate(BaseModel):
    name: str = Field(min_length=1)


class NodeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class EdgeCreate(BaseModel):
    source: str = Field(min_length=1)
    destination: str = Field(min_length=1)
    latency: float


class EdgeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source: str
    destination: str
    latency: float

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=obj.id,
            source=obj.source_name,
            destination=obj.destination_name,
            latency=obj.latency,
        )


class RouteQuery(BaseModel):
    source: str
    destination: str


class RouteResult(BaseModel):
    total_latency: Optional[float]
    path: Optional[List[str]]


class RouteHistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source: str
    destination: str
    total_latency: Optional[float]
    path: Optional[List[str]]
    created_at: datetime

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=obj.id,
            source=obj.source,
            destination=obj.destination,
            total_latency=obj.total_latency,
            path=obj.path.split(",") if obj.path else None,
            created_at=obj.created_at,
        )
