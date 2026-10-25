from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.exceptions import HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import get_database_url
from app.db.session import create_session_factory
from app.dependencies import get_session
from app.models.ticket import Ticket


@asynccontextmanager
async def lifespan(app: FastAPI):
    database_url = get_database_url()
    engine, session_factory = create_session_factory(database_url=database_url)

    try:
        Ticket.metadata.create_all(engine)

        app.state.engine = engine
        app.state.session_factory = session_factory

        yield
    finally:
        engine.dispose()


VERSION = "0.1.0"
app = FastAPI(title="Equipment Helpdesk", version=VERSION, lifespan=lifespan)


@app.get("/health")
def health(session: Annotated[Session, Depends(get_session)]):
    try:
        session.execute(text("SELECT 1"))
    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable",
        ) from None

    return {"status": "ok"}


@app.get("/version")
def version():
    return {"version": VERSION}
