import heapq
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models import Edge, Node, RouteHistory


def get_node_by_name(db: Session, name: str) -> Optional[Node]:
    return db.query(Node).filter(Node.name == name).first()


def get_node_by_id(db: Session, node_id: int) -> Optional[Node]:
    return db.query(Node).filter(Node.id == node_id).first()


def create_node(db: Session, name: str) -> Node:
    node = Node(name=name)
    db.add(node)
    db.commit()
    db.refresh(node)
    return node


def list_nodes(db: Session) -> List[Node]:
    return db.query(Node).order_by(Node.id).all()


def delete_node(db: Session, node_id: int) -> bool:
    node = get_node_by_id(db, node_id)
    if not node:
        return False
    for edge in list(node.outgoing_edges) + list(node.incoming_edges):
        if edge.source_id == node.id:
            edge.source_id = None
        if edge.destination_id == node.id:
            edge.destination_id = None
    db.delete(node)
    db.commit()
    return True


def create_edge(db: Session, source_name: str, destination_name: str, latency: float) -> Edge:
    source = get_node_by_name(db, source_name)
    destination = get_node_by_name(db, destination_name)
    if not source or not destination:
        raise ValueError("Both nodes must exist")

    existing = (
        db.query(Edge)
        .filter(
            Edge.source_id == source.id,
            Edge.destination_id == destination.id,
        )
        .first()
    )
    if existing:
        raise ValueError("Edge already exists")

    edge = Edge(source_id=source.id, destination_id=destination.id, latency=latency)
    db.add(edge)
    db.commit()
    db.refresh(edge)
    return edge


def list_edges(db: Session) -> List[Edge]:
    return db.query(Edge).order_by(Edge.id).all()


def delete_edge(db: Session, edge_id: int) -> bool:
    edge = db.query(Edge).filter(Edge.id == edge_id).first()
    if not edge:
        return False
    db.delete(edge)
    db.commit()
    return True


def shortest_path(db: Session, source_name: str, destination_name: str) -> Tuple[Optional[float], Optional[List[str]]]:
    source = get_node_by_name(db, source_name)
    destination = get_node_by_name(db, destination_name)
    if not source or not destination:
        raise ValueError("Both nodes must exist")

    adjacency = {}
    for edge in list_edges(db):
        if edge.source is None or edge.destination is None:
            continue
        adjacency.setdefault(edge.source.name, []).append((edge.destination.name, edge.latency))

    distances = {source.name: 0.0}
    previous = {}
    heap: List[Tuple[float, str]] = [(0.0, source.name)]

    while heap:
        current_distance, node_name = heapq.heappop(heap)
        if current_distance > distances.get(node_name, float("inf")):
            continue
        if node_name == destination.name:
            break
        for neighbor, weight in adjacency.get(node_name, []):
            new_distance = current_distance + weight
            if new_distance < distances.get(neighbor, float("inf")):
                distances[neighbor] = new_distance
                previous[neighbor] = node_name
                heapq.heappush(heap, (new_distance, neighbor))

    if destination.name not in distances:
        return None, None

    path = []
    cursor = destination.name
    while cursor is not None:
        path.append(cursor)
        cursor = previous.get(cursor)
    path.reverse()

    return distances[destination.name], path


def log_route_history(
    db: Session,
    source: str,
    destination: str,
    total_latency: Optional[float],
    path: Optional[List[str]],
) -> RouteHistory:
    history = RouteHistory(
        source=source,
        destination=destination,
        total_latency=total_latency,
        path=",".join(path) if path else None,
        created_at=datetime.utcnow(),
    )
    db.add(history)
    db.commit()
    db.refresh(history)
    return history


def list_route_history(
    db: Session,
    source: Optional[str] = None,
    destination: Optional[str] = None,
    limit: Optional[int] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
) -> List[RouteHistory]:
    query = db.query(RouteHistory)
    if source:
        query = query.filter(RouteHistory.source == source)
    if destination:
        query = query.filter(RouteHistory.destination == destination)
    if date_from:
        query = query.filter(RouteHistory.created_at >= date_from)
    if date_to:
        query = query.filter(RouteHistory.created_at <= date_to)
    query = query.order_by(RouteHistory.created_at.desc(), RouteHistory.id.desc())
    if limit is not None:
        query = query.limit(limit)
    return query.all()
