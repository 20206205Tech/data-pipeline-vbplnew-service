import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi_voyager import create_voyager
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from scalar_fastapi import get_scalar_api_reference

import env
from database.config import engine
from index_router import index_router
from lifespan.lifespan import lifespan
from middlewares.log_request_and_response_middleware import (
    LogRequestAndResponseMiddleware,
)
from tracing import init_tracing
from utils.log_function import log_function

init_tracing()


app = FastAPI(
    lifespan=lifespan,
    title=f"{env.SERVICE_NAME} ({env.ENVIRONMENT})",
    description=env.DESCRIPTION,
    root_path=f"/{env.SERVICE_NAME}",
    swagger_ui_parameters={"persistAuthorization": True},
)


# Instrument SQLAlchemy (Để xem query DB mất bao lâu)
SQLAlchemyInstrumentor().instrument(engine=engine)

# Instrument FastAPI (Để bắt các HTTP request)
FastAPIInstrumentor.instrument_app(app)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LogRequestAndResponseMiddleware)


app.include_router(index_router)


@app.get("/")
@log_function
def root():
    return {
        "message": "Hello World",
        "docs": f"/{env.SERVICE_NAME}/docs",
    }


app.mount(
    "/voyager",
    create_voyager(
        app,
        module_color={"common": "blue", "app": "red", "app": "green"},
        swagger_url="/docs",
    ),
)


@app.get("/scalar", response_class=HTMLResponse, include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
    )


def main():
    uvicorn.run("main:app", host=env.HOST, port=env.PORT, reload=env.RELOAD)


if __name__ == "__main__":
    main()
