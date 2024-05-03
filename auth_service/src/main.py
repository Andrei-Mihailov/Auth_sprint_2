import multiprocessing
import gunicorn.app.base
import click
import asyncio
import functools as ft
import sys

from fastapi import FastAPI, Depends, Request, status
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis
from contextlib import asynccontextmanager
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME

from api.v1 import users, roles, permissions
from db import postgres_db
from db import redis_db
from core.config import settings
from api.v1.service import check_jwt


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_db.redis = Redis(host=settings.redis_host, port=settings.redis_port)
    yield
    await redis_db.redis.close()


def configure_tracer() -> None:
    trace.set_tracer_provider(
        TracerProvider(
            resource=Resource.create({SERVICE_NAME: "Auth-service"})
        )
    )
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name='jaeger',
                agent_port=6831,
            )
        )
    )
    # Чтобы видеть трейсы в консоли
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))


configure_tracer()


app = FastAPI(
    lifespan=lifespan,
    title="Сервис авторизации",
    description="Реализует методы идентификации, аутентификации, авторизации",
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)


FastAPIInstrumentor.instrument_app(app)


@app.middleware('http')
async def before_request(request: Request, call_next):
    request_id = request.headers.get('X-Request-Id')
    if not request_id:
        return ORJSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={'detail': 'X-Request-Id is required'})

    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span('http', attributes={'http.request_id': request_id}):
        response = await call_next(request=request)

    return response


def number_of_workers():
    return (multiprocessing.cpu_count() * 2) + 1


class StandaloneApplication(gunicorn.app.base.BaseApplication):

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


app.include_router(users.router, prefix="/api/v1/users")
app.include_router(roles.router, prefix="/api/v1/roles", dependencies=[Depends(check_jwt)])
app.include_router(permissions.router, prefix="/api/v1/permissions", dependencies=[Depends(check_jwt)])


def async_cmd(func):
    @ft.wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return wrapper


@click.command()
@click.option(
    "--email",
    default="test",
    prompt="Enter email",
    help="email for the superuser",
)
@click.option(
    "--password",
    default="test",
    prompt="Enter password",
    help="Password for the superuser",
)
@async_cmd
async def create_superuser(email, password):
    from models.entity import User
    from sqlalchemy.future import select

    async with postgres_db.async_session() as session:
        result = await session.execute(select(User).filter(User.email == email))
        existing_user = result.scalars().first()
        if existing_user:
            click.echo("User with this email already exists!")
            return

        # Создаем суперпользователя
        superuser_data = {"email": email, "password": password, "is_superuser": True}
        instance = User(**superuser_data)
        session.add(instance)
        try:
            await session.commit()
        except Exception as e:
            print(f"Ошибка при создании объекта: {e}")
            return None

        click.echo(f"Superuser {email} created successfully!")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        create_superuser()
    else:
        options = {
            "bind": "%s:%s" % ("0.0.0.0", "8000"),
            "workers": number_of_workers(),
            "worker_class": "uvicorn.workers.UvicornWorker",
        }

        StandaloneApplication(app, options).run()
