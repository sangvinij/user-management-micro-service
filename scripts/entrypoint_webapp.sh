#!/bin/bash
alembic upgrade head
uvicorn user_management.main:app --host 0.0.0.0 --port 8000