import os

from dotenv import load_dotenv
from fastapi import FastAPI

from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from ai_recommend.api import endpoints
from ai_recommend.container import ApplicationContainer


def create_app() -> FastAPI:

    # Load environment variables from .env file in the same directory
    load_dotenv()

    # Initialize application container
    container = ApplicationContainer()

    # Configure database settings from environment using from_dict()

    container.config.from_dict(
        {
            "database": {
                "graph": {
                    "host": os.getenv("GRAPH_DB_HOST"),
                    "port": os.getenv("GRAPH_DB_PORT", "5432"),
                    "username": os.getenv("GRAPH_DB_USER"),
                    "password": os.getenv("GRAPH_DB_PASSWORD"),
                    "database": os.getenv("GRAPH_DB_DATABASE_NAME"),
                }
            },
            "ai": {
                "openai_api_key": os.getenv("OPENAI_API_KEY"),
                "ai_provider": os.getenv("AI_PROVIDER"),
                "ai_model": os.getenv("AI_MODEL"),
            },
        }
    )

    # Initialize resources after configuration is set
    container.init_resources()

    # Wire the application for dependency injection
    container.wire(modules=[__name__])

    app = FastAPI()
    app.container = container
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allows all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allows all methods
        allow_headers=["*"],  # Allows all headers
    )

    app.include_router(endpoints.router)

    # Serve static files
    app.mount("/static", StaticFiles(directory="."), name="static")

    return app



if __name__ == "__main__":
    import uvicorn
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8001)