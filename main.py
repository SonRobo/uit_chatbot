"""
Run the code in this file
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers import chat_router
from src.api.routers import file_router
from src.api.routers import suggestion_router
from src.api.routers import manually_file_router

app = FastAPI()

# app.include_router(root_router)
app.include_router(chat_router)
app.include_router(file_router)
app.include_router(suggestion_router)
app.include_router(manually_file_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Run the server
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8501
    )
