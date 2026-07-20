from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from app.database import Base, engine
from app.models import Edge, Node, RouteHistory  # noqa: F401
from app.routers import edges, nodes, routes

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Network Route Optimization API")


@app.exception_handler(RequestValidationError)
async def request_validation_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"error": "Validation error"})


app.include_router(nodes.router)
app.include_router(edges.router)
app.include_router(routes.router)
