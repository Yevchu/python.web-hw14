from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_redis_rate_limiter import RedisRateLimiterMiddleware, RedisClient

from src.routes import contacts, auth, users

app = FastAPI()

# Initialize the Redis client
redis_client = RedisClient(host='localhost', port='6379', db=0)
# Apply the rate limiter middleware to the app
app.add_middleware(RedisRateLimiterMiddleware, redis_client=redis_client, limit=30, window=60)
# add CORS origins
origins = [
    "http://localhost:3000",
    "https://www.google.com/"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

app.include_router(auth.router, prefix='/api')
app.include_router(contacts.router, prefix='/api')
app.include_router(users.router, prefix='/api')

@app.get('/')
def read_root():
    return {'message': 'Some messages'}