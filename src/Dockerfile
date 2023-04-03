FROM python:3.9-slim

WORKDIR /app
COPY ./src .
COPY ./src/requirements.txt /app

RUN pip3 install -r requirements.txt

# EXPOSE 8000
CMD python3 /app/app.py

# CMD ["uvicorn","src.route:app","--host=0.0.0.0","--reload"]