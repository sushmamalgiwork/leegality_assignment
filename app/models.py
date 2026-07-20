from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    outgoing_edges = relationship("Edge", foreign_keys="Edge.source_id", back_populates="source")
    incoming_edges = relationship("Edge", foreign_keys="Edge.destination_id", back_populates="destination")


class Edge(Base):
    __tablename__ = "edges"
    __table_args__ = (UniqueConstraint("source_id", "destination_id", name="uq_edge_pair"),)

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("nodes.id", ondelete="SET NULL"), nullable=True)
    destination_id = Column(Integer, ForeignKey("nodes.id", ondelete="SET NULL"), nullable=True)
    latency = Column(Float, nullable=False)

    source = relationship("Node", foreign_keys=[source_id], back_populates="outgoing_edges")
    destination = relationship("Node", foreign_keys=[destination_id], back_populates="incoming_edges")

    @property
    def source_name(self) -> str:
        return self.source.name if self.source else ""

    @property
    def destination_name(self) -> str:
        return self.destination.name if self.destination else ""


class RouteHistory(Base):
    __tablename__ = "route_history"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    total_latency = Column(Float, nullable=True)
    path = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False)
