# Image de base ancienne, compatible avec les vieilles dépendances
FROM python:3.8-slim
WORKDIR /app
# On installe d'abord les dépendances (meilleur cache Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 5000
CMD ["python", "app.py"]
