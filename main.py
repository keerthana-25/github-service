# Author: Nitish Ratakonda (nitishsjsucs)
# Email: Nitish.ratakonda@sjsu.edu
# Assignment: GitHub Issue Service - Main Application
# Date: September 29, 2025
# Description: Main FastAPI application entry point with router configuration

from fastapi import FastAPI
from routers.handle_routes import router as issues_router
from routers.webhook_routes import router as webhook_router

app = FastAPI(
    title="GitHub Issue Service API",
    description="A FastAPI-based microservice for interacting with GitHub Issues API",
    version="1.0.0"
)

app.include_router(issues_router)
app.include_router(webhook_router)
