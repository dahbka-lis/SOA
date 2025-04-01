import grpc
from concurrent import futures
from grpc_reflection.v1alpha import reflection
import time
import post_pb2
import post_pb2_grpc

from sqlalchemy.orm import Session
import database, schemas, crud, models

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class PostServiceServicer(post_pb2_grpc.PostServiceServicer):
    def __init__(self):
        models.Base.metadata.create_all(bind=database.engine)
        self.db_session = database.SessionLocal()

    def CreatePost(self, request, context):
        post_create = schemas.PostCreate(
            title=request.title,
            description=request.description,
            creator_id=request.creator_id,
            is_private=request.is_private,
            tags=list(request.tags),
        )

        db_post = crud.create_post(self.db_session, post_create)
        return post_pb2.PostResponse(post=self._convert_post(db_post))

    def DeletePost(self, request, context):
        db_post = crud.get_post(self.db_session, int(request.post_id))
        if db_post is None:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Post not found")
            return post_pb2.EmptyResponse()

        if db_post.creator_id != request.requester_id:
            context.set_code(grpc.StatusCode.PERMISSION_DENIED)
            context.set_details("Not authorized to delete this post")
            return post_pb2.EmptyResponse()

        crud.delete_post(self.db_session, int(request.post_id))
        return post_pb2.EmptyResponse()

    def UpdatePost(self, request, context):
        db_post = crud.get_post(self.db_session, int(request.post_id))

        if db_post is None:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Post not found")
            return post_pb2.PostResponse()

        if db_post.creator_id != request.requester_id:
            context.set_code(grpc.StatusCode.PERMISSION_DENIED)
            context.set_details("Not authorized to update this post")
            return post_pb2.PostResponse()

        post_update = schemas.PostUpdate(
            title=request.title,
            description=request.description,
            is_private=request.is_private,
            tags=list(request.tags),
        )

        updated_post = crud.update_post(
            self.db_session, int(request.post_id), post_update
        )

        return post_pb2.PostResponse(post=self._convert_post(updated_post))

    def GetPost(self, request, context):
        db_post = crud.get_post(self.db_session, int(request.post_id))

        if db_post is None:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Post not found")
            return post_pb2.PostResponse()

        if db_post.is_private and db_post.creator_id != request.requester_id:
            context.set_code(grpc.StatusCode.PERMISSION_DENIED)
            context.set_details("Not authorized to view this post")
            return post_pb2.PostResponse()

        return post_pb2.PostResponse(post=self._convert_post(db_post))

    def ListPosts(self, request, context):
        skip = (request.page - 1) * request.page_size
        posts = crud.get_posts(self.db_session, skip=skip, limit=request.page_size)
        total = crud.count_posts(self.db_session)

        posts_list = [
            self._convert_post(p)
            for p in posts
            if not p.is_private or p.creator_id == request.requester_id
        ]

        return post_pb2.ListPostsResponse(posts=posts_list, total=total)

    def _convert_post(self, db_post):
        tags = db_post.tags.split(",") if db_post.tags else []
        return post_pb2.Post(
            id=str(db_post.id),
            title=db_post.title,
            description=db_post.description,
            creator_id=db_post.creator_id,
            created_at=db_post.created_at.isoformat(),
            updated_at=db_post.updated_at.isoformat(),
            is_private=db_post.is_private,
            tags=tags,
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    post_pb2_grpc.add_PostServiceServicer_to_server(PostServiceServicer(), server)

    SERVICE_NAMES = (
        post_pb2.DESCRIPTOR.services_by_name["PostService"].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)

    server.add_insecure_port("[::]:50051")
    server.start()
    print("gRPC сервер запущен на порту 50051")
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == "__main__":
    serve()
