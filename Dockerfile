FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app.py
COPY app.py .

# Copy templates directory (will be created on host)
COPY templates/ ./templates/

ENV DB_HOST=db
ENV DB_PORT=3306
ENV DB_NAME=login_db
ENV DB_USER=login_user
ENV DB_PASSWORD=user_password

CMD ["python", "app.py"]