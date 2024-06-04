FROM python:3.12

WORKDIR /rest_api/orders

RUN pip install fastapi[all] pymongo motor pydantic pyjwt

COPY . /rest_api/orders/

ENTRYPOINT ["bash", "-c", "uvicorn main:app --port 8080 --host 0.0.0.0"]
