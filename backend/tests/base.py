import asyncio
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from urllib.parse import urlencode

from app.db.base import Base
from app.db.session import build_engine, build_session_factory
from app.main import create_app
from seed import seed_demo_data


class ASGITestResponse:
    def __init__(self, status_code: int, body: bytes):
        self.status_code = status_code
        self._body = body
        self.text = body.decode("utf-8")

    def json(self):
        return json.loads(self.text)


class ASGITestClient:
    def __init__(self, app):
        self.app = app

    def close(self):
        return None

    def get(self, path: str, headers: dict[str, str] | None = None):
        return self.request("GET", path, headers=headers)

    def post(
        self,
        path: str,
        json_body: dict | None = None,
        data: dict | None = None,
        headers: dict[str, str] | None = None,
        **kwargs,
    ):
        if "json" in kwargs:
            json_body = kwargs["json"]
        return self.request("POST", path, json_body=json_body, data=data, headers=headers)

    def request(
        self,
        method: str,
        path: str,
        json_body: dict | None = None,
        data: dict | None = None,
        headers: dict[str, str] | None = None,
    ):
        raw_headers = []
        body = b""
        headers = headers or {}

        if json_body is not None:
            body = json.dumps(json_body).encode("utf-8")
            headers.setdefault("content-type", "application/json")
        elif data is not None:
            body = urlencode(data).encode("utf-8")
            headers.setdefault("content-type", "application/x-www-form-urlencoded")

        if body:
            headers.setdefault("content-length", str(len(body)))

        for key, value in headers.items():
            raw_headers.append((key.lower().encode("utf-8"), value.encode("utf-8")))

        async def receive():
            if getattr(receive, "done", False):
                return {"type": "http.disconnect"}
            receive.done = True
            return {"type": "http.request", "body": body, "more_body": False}

        receive.done = False
        messages = []

        async def send(message):
            messages.append(message)

        if "?" in path:
            path_part, qs_part = path.split("?", 1)
        else:
            path_part, qs_part = path, ""

        scope = {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": method,
            "scheme": "http",
            "path": path_part,
            "raw_path": path_part.encode("utf-8"),
            "query_string": qs_part.encode("utf-8"),
            "headers": raw_headers,
            "client": ("testclient", 50000),
            "server": ("testserver", 80),
            "app": self.app,
        }

        asyncio.run(self.app(scope, receive, send))

        status_code = 500
        body_parts = []
        for message in messages:
            if message["type"] == "http.response.start":
                status_code = message["status"]
            elif message["type"] == "http.response.body":
                body_parts.append(message.get("body", b""))

        return ASGITestResponse(status_code, b"".join(body_parts))


class BackendTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        db_path = Path(self.temp_dir.name) / "test.db"
        database_url = f"sqlite:///{db_path}"

        self.engine = build_engine(database_url)
        self.SessionLocal = build_session_factory(self.engine)
        Base.metadata.create_all(bind=self.engine)

        with self.SessionLocal() as db:
            seed_demo_data(db)

        self.app = create_app(session_factory=self.SessionLocal, engine=self.engine)
        self.client = ASGITestClient(self.app)

    def tearDown(self):
        self.client.close()
        self.engine.dispose()
        self.temp_dir.cleanup()

    def login(self, email: str, password: str) -> str:
        response = self.client.post(
            "/auth/login",
            data={"username": email, "password": password},
        )
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()["access_token"]

    def auth_headers(self, email: str, password: str) -> dict[str, str]:
        token = self.login(email, password)
        return {"Authorization": f"Bearer {token}"}
