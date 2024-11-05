from aiohttp import web
from app.models import Task
from app.database import create_pool

async def create_task(request):
    data = await request.json()
    task = Task(**data)

    async with request.app['db'].acquire() as connection:
        await connection.execute(
            "INSERT INTO tasks (title, description, status, user_id) VALUES ($1, $2, $3, $4)",
            task.title, task.description, task.status, task.user_id
        )

    return web.json_response({"message": "Task created successfully"}, status=201)

async def get_tasks(request):
    status = request.query.get("status")
    query = "SELECT * FROM tasks"
    params = []

    if status:
        query += " WHERE status = $1"
        params.append(status)

    async with request.app['db'].acquire() as connection:
        tasks = await connection.fetch(query, *params)

    return web.json_response([dict(task) for task in tasks])

async def update_task(request):
    task_id = request.match_info['id']
    data = await request.json()

    async with request.app['db'].acquire() as connection:
        await connection.execute(
            "UPDATE tasks SET title = $1, description = $2, status = $3 WHERE id = $4",
            data['title'], data['description'], data['status'], task_id
        )

    return web.json_response({"message": "Task updated successfully"})

async def delete_task(request):
    task_id = request.match_info['id']

    async with request.app['db'].acquire() as connection:
        await connection.execute("DELETE FROM tasks WHERE id = $1", task_id)

    return web.json_response({"message": "Task deleted successfully"})
