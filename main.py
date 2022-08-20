from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import courses_router, subject_router, module_router, user_router
from models.session import engine, Base

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5050",
]

app = FastAPI()

app.include_router(courses_router)
app.include_router(subject_router)
app.include_router(module_router)
app.include_router(user_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create the database tables
Base.metadata.create_all(bind=engine)
