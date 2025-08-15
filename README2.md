## Follow step by step to get working - type in terminal using powershell

1. create virtual env - Powershell 
python -m venv .venv

2. activate virtual env
.venv\Scripts\Activate.ps1

3. Quick start (Python only start)
localhost fastapi server
uvicorn app.main:app --reload
					Either of these options

3. Start up using docker
docker-compose up

4. Access FastAPI to use web server

http://127.0.0.1:8000/docs


## Test

pytest