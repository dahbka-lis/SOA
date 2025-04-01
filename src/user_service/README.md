## Register new profile
    curl -X POST "http://localhost:8080/register" \
        -H "Content-Type: application/json" \
        -d '{
            "username": "testuser",
            "password": "testpass",
            "email": "test@example.com"
            }'

## Login by profile password
    curl -X POST "http://localhost:8080/login" \
        -H "Content-Type: application/json" \
        -d '{
            "username": "testuser",
            "password": "testpass"
            }'

## Get profile by login
    curl -X GET "http://localhost:8080/profile?username=testuser"

## Update proile with token
    curl -X PUT http://localhost:8080/profile \
        -H "Content-Type: application/json" \
        -d '{
            "token": "TOKEN",
            "phone": "+123456",
            "email": "new@ya.ru",
            "first_name": "John",
            "last_name": "Doe",
            "bio": "new bio",
            "date_of_birth": "1990-01-01T00:00:00",
            "avatar": "empty",
            "updated_at": "1990-01-01T00:00:00" 
            }'
