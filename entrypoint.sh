#!/bin/sh

if [ "$RUN_WORKER" = "true" ]; then
    
    echo "Starting Celery worker..."
    celery -A app.tasks worker --loglevel=info -E

else
    
    echo "Starting FastAPI app..."
    uvicorn app.main:app --host 0.0.0.0 --port 8000

fi