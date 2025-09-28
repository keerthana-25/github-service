from fastapi import FastAPI
from routers.handle_routes import router as issues_router

app = FastAPI()
app.include_router(issues_router)
