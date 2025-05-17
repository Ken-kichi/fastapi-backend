from fastapi.middleware.cors import CORSMiddleware
from routes import auth_routes, task_routes,user_routes
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware


load_dotenv()

app = FastAPI(
    title="Task App",
    description="This is Task Management App",
    version="1.0.0"
)

class EnforceHTTPSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # プロキシ経由のプロトコルをチェック
        forwarded_proto = request.headers.get("X-Forwarded-Proto", request.url.scheme)
        if forwarded_proto != "https":
            # HTTPS URLを構築
            url = request.url.replace(scheme="https")
            return RedirectResponse(url, status_code=307)  # 一時的なリダイレクト
        return await call_next(request)

app.include_router(auth_routes.router)
app.include_router(task_routes.router)
app.include_router(user_routes.router)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(EnforceHTTPSMiddleware)
