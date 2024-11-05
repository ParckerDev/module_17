import aiohttp
from aiohttp import web
import aioredis
from app.database import create_pool
from app.users import register_user, login_user, refresh_token
from app.tasks import create_task, get_tasks, update_task, delete_task

async def init_app():
    app = web.Application()

    # Подключение к базе данных
    app['db'] = await create_pool()

    # Подключение к Redis
    app['redis'] = await aioredis.from_url("redis://redis:6379")

    # Настройка маршрутов
    app.router.add_post('/auth/register', register_user)
    app.router.add_post('/auth/login', login_user)
    app.router.add_post('/auth/refresh', refresh_token)
    app.router.add_post('/tasks', create_task)
    app.router.add_get('/tasks', get_tasks)
    app.router.add_put('/tasks/{id}', update_task)
    app.router.add_delete('/tasks/{id}', delete_task)

    return app

if __name__ == '__main__':
    web.run_app(init_app(), port=8000)
