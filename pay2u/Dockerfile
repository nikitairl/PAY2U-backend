FROM python:3.11

WORKDIR /app

COPY . .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt --no-cache-dir

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "pay2u.wsgi"]