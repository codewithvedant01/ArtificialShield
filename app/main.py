"""Application entrypoint for ArtificialShield."""
import uvicorn
from app.gateway import app
from config import settings

__all__ = ["app"]

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=True)