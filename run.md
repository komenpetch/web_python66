.\.venv\Scripts\activate.bat

pytest test_main.py -v -s

docker run -d redis -p 6379:6379 redis

docker exec -it redis redis-cli ping

docker exec -it redis redis-cli

KEYS *
GET "LIMITS:LIMITER/127.0.0.1//login/5/1/minute"
TTL "LIMITS:LIMITER/127.0.0.1//login/5/1/minute"