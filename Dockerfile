FROM python:3.8-slim

WORKDIR /server

COPY . .

CMD ["python", "setup.py"]