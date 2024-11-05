from aiohttp import web
from app.models import User
from app.database import create_pool
from app.auth import get_password_hash, verify_password, create_access_token, create_refresh_token
import redis

async def register_user(request):
    data = await request.json()
    username = data['username']
    password = data['password']
    password_hash = await get_password_hash(password)

    async with request.app['db'].acquire() as connection:
        await connection.execute("INSERT INTO users (username, password_hash) VALUES ($1, $2)", username, password_hash)

    return web.json_response({"message": "User registered successfully"})

async def login_user(request):
    data = await request.json()
    username = data['username']
    password = data['password']

    async with request.app['db'].acquire() as connection:
        user = await connection.fetchrow("SELECT * FROM users WHERE username = $1", username)

    if user and await verify_password(password, user['password_hash']):
        access_token = await create_access_token({"sub": user['id']})
        refresh_token = await create_refresh_token({"sub": user['id']})

        # Сохранение refresh токена в Redis
        redis_client = request.app['redis']
        await redis_client.set(f"refresh_token:{user['id']}", refresh_token)

        return web.json_response({"access_token": access_token, "refresh_token": refresh_token})

    return web.json_response({"error": "Invalid credentials"}, status=401)

async def refresh_token(request):
    data = await request.json()
    refresh_token = data.get("refresh_token")

    # Проверка refresh токена в Redis
    redis_client = request.app['redis']
    user_id = await redis_client.get(f"refresh_token:{refresh_token}")

    if user_id:
        access_token = await create_access_token({"sub": user_id})
        return web.json_response({"access_token": access_token})

    return web.json_response({"error": "Invalid refresh token"}, status=401)
