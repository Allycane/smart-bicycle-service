from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.connection import engine, Base
import os

from routers.member import member_router
from routers.dashboard import dashboard_router
from routers.route import route_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = os.getenv(
    "FRONT_ORIGINS",
    "http://localhost:5173, http://localhost:5174"
).split(',')

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"]
)

app.include_router(member_router, prefix='/api/member')
app.include_router(dashboard_router, prefix='/api/dashboard')
app.include_router(route_router, prefix='/api/routes')

