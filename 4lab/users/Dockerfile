FROM python:3.12

WORKDIR /rest_api/users

RUN pip install passlib sqlalchemy psycopg2-binary "fastapi["all"]" pyjwt

COPY . /rest_api/users/  

ENTRYPOINT ["bash", "-c", "uvicorn main:app --port 8080 --host 0.0.0.0"]