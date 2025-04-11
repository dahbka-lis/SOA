## Create a new post
    curl -X POST http://localhost:8080/posts \
        -H "Content-Type: application/json" \
        -d '{
            "title": "My First Post",
            "description": "This is a test post",
            "is_private": false,
            "tags": ["test", "grpc"]
            }'

## Get a post by id
    curl -X GET http://localhost:8080/posts/1

## Update a post by id
    curl -X PUT http://localhost:8080/posts/1 \
        -H "Content-Type: application/json" \
        -d '{
            "title": "Updated Post Title",
            "description": "Updated post content",
            "is_private": true,
            "tags": ["updated", "grpc"]
            }'

## Delete a post by id
    curl -X DELETE http://localhost:8080/posts/1

## Get 1 page with max 5 posts
    curl -X GET "http://localhost:8080/posts?page=1&page_size=5"
