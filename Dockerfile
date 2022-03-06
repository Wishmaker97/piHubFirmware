FROM python:3.7-alpine

WORKDIR /server

COPY . .

CMD ["python", "setup.py"]