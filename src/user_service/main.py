from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

import os
import jwt

import database, schemas, crud, models


load_dotenv()

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
TOKEN_EXPIRATION_HOURS = int(os.environ.get("TOKEN_EXPIRATION_HOURS"))


models.Base.metadata.create_all(bind=database.engine)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()
db = database.SessionLocal()


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_login(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    user.password = pwd_context.hash(user.password)
    new_user = crud.create_user(db, user)
    new_profile = crud.create_profile(db, new_user.id)
    return new_profile


@app.post("/login", response_model=schemas.SessionResponse)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_login(db, username=user.username)
    if not db_user or not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    expiration = datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRATION_HOURS)
    token = jwt.encode(
        {"user_id": db_user.id, "exp": expiration}, SECRET_KEY, algorithm=ALGORITHM
    )

    session = crud.create_session(db, db_user.id, token, expiration)
    return schemas.SessionResponse(token=session.token, expires_at=session.expires_at)


@app.get("/profile")
def get_profile(username: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_login(db, username=username)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_profile = crud.get_profile_by_user(db, user_id=db_user.id)
    return db_profile


@app.put("/profile")
def update_profile(
    user: schemas.UserProfileUpdate,
    db: Session = Depends(get_db),
):
    session = crud.get_session_by_token(db, user.token)
    if not session or session.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    user_update = schemas.UserUpdate(
        user_id=session.user_id, phone=user.phone, email=user.email
    )

    profile_update = schemas.ProfileUpdate(
        user_id=session.user_id,
        first_name=user.first_name,
        last_name=user.last_name,
        bio=user.bio,
        date_of_birth=user.date_of_birth,
        avatar=user.avatar,
        updated_at=datetime.now(timezone.utc),
    )

    crud.update_user(db, user_update)
    return crud.update_profile(db, profile_update)
