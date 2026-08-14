"""CORS middleware configuration.

Configures Cross-Origin Resource Sharing for the frontend React app.
Origins are configurable via the CORS_ORIGINS environment variable.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from config import CORS_ORIGINS


def setup_cors(app: FastAPI) -> None:
    """
    Configure CORS middleware on the FastAPI application.

    Allows:
    - Origins: from CORS_ORIGINS config (default: localhost:5173, localhost:3000)
    - Methods: GET, POST, DELETE, OPTIONS
    - Headers: all
    - Credentials: enabled (for session cookies if needed)
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
