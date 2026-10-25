

from fastapi import Request


def get_session(request: Request):
    session_factory = request.app.state.session_factory

    with session_factory() as session:
        yield session
