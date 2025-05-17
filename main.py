from fastapi.middleware.cors import CORSMiddleware
from routes import auth_routes, task_routes,user_routes
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse



load_dotenv()

app = FastAPI(
    title="Task App",
    description="This is Task Management App",
    version="1.0.0"
)

@app.middleware("http")
async def enforce_https(request: Request, call_next):
    if not request.url.scheme == "https":
        url = request.url._replace(scheme="https")
        return RedirectResponse(url)
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
