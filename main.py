from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models.session import Base, engine
from routers import courses_router, module_router, subject_router, user_router

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
