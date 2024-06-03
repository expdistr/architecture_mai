FROM python:3.12

WORKDIR /rest_api/services

RUN pip install fastapi[all] pymongo motor pydantic

COPY . /rest_api/services/

ENTRYPOINT ["bash", "-c", "uvicorn main:app --port 8080 --host 0.0.0.0"]
