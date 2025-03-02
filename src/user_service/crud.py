from sqlalchemy.orm import Session
from datetime import datetime

import models, schemas


def get_user_by_login(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_profile_by_user(db: Session, user_id: int):
    return db.query(models.Profile).filter(models.Profile.user_id == user_id).first()


def get_session_by_token(db: Session, token: str):
    return db.query(models.Session).filter(models.Session.token == token).first()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        username=user.username, password=user.password, email=user.email
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_profile(db: Session, user_id: int):
    db_profile = models.Profile(user_id=user_id)
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile


def create_session(db: Session, user_id: int, token: str, expires_at: datetime):
    session = db.query(models.Session).filter(models.Session.user_id == user_id).first()
    if session:
        session.token = token
        session.expires_at = expires_at
    else:
        session = models.Session(user_id=user_id, token=token, expires_at=expires_at)
        db.add(session)
    db.commit()
    db.refresh(session)
    return session


def update_user(db: Session, user: schemas.UserUpdate):
    db_user = (
        db.query(models.User).filter(models.User.username == user.username).first()
    )
    if not db_user:
        return None

    for key, value in user.dict(exclude_unset=True).items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user


def update_profile(db: Session, profile: schemas.ProfileUpdate):
    db_profile = (
        db.query(models.Profile).filter(models.Profile.id == profile.user_id).first()
    )
    if not db_profile:
        return None

    for key, value in profile.dict(exclude_unset=True).items():
        setattr(db_profile, key, value)

    db.commit()
    db.refresh(db_profile)
    return db_profile


# crud without rd ;)
