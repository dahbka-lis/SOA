from sqlalchemy.orm import Session
from datetime import datetime

import models, schemas


def create_post(db: Session, post: schemas.PostCreate):
    db_post = models.Post(
        title=post.title,
        description=post.description,
        creator_id=post.creator_id,
        is_private=post.is_private,
        tags=",".join(post.tags) if post.tags else "",
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


def get_post(db: Session, post_id: int):
    return db.query(models.Post).filter(models.Post.id == post_id).first()


def delete_post(db: Session, post_id: int):
    db_post = get_post(db, post_id)
    if db_post:
        db.delete(db_post)
        db.commit()
    return db_post


def update_post(db: Session, post_id: int, post_data: schemas.PostUpdate):
    db_post = get_post(db, post_id)
    if db_post:
        db_post.title = post_data.title
        db_post.description = post_data.description
        db_post.is_private = post_data.is_private
        db_post.tags = ",".join(post_data.tags) if post_data.tags else ""
        db_post.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_post)
    return db_post


def get_posts(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Post).offset(skip).limit(limit).all()


def count_posts(db: Session):
    return db.query(models.Post).count()
