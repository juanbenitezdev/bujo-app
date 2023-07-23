from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import crud
import models
import schemas
from db import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/entries/", response_model=schemas.Entry)
def create_entries_for_user(
    user_id: int, entry: schemas.EntryCreate, db: Session = Depends(get_db)
):
    if entry.project_id:
        db_project = crud.get_project(db, project_id=entry.project_id)

        if not db_project:
            raise HTTPException(status_code=404, detail=f"Project {entry.project_id} not found")

    if entry.parent_entry_id:
        db_entry = crud.get_entry(db, entry_id=entry.parent_entry_id)

        if not db_entry:
            raise HTTPException(status_code=404, detail=f"Entry {entry.parent_entry_id} not found")

    return crud.create_entry(db=db, entry=entry, user_id=user_id)


@app.get("/entries/", response_model=list[schemas.Entry])
def read_entries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    entries = crud.get_entries(db, skip=skip, limit=limit)
    return entries


@app.post("/users/{user_id}/projects/", response_model=schemas.Project)
def create_projects_for_user(
        user_id: int, project: schemas.ProjectCreate, db: Session = Depends(get_db)
):
    return crud.create_project(db=db, project=project, user_id=user_id)


@app.get("/projects/", response_model=list[schemas.Project])
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    projects = crud.get_projects(db, skip=skip, limit=limit)
    return projects
