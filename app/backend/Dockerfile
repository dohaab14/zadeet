# --- BACKEND DOCKERFILE ---

FROM python:3.11-slim

# 2. Variables d'environnement pour optimiser Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Répertoire de travail dans le conteneur
WORKDIR /code

# 4. Installation des dépendances

COPY requirements.txt /code/
RUN pip install --no-cache-dir --upgrade --default-timeout=1000 -r /code/requirements.txt

# 5. Copie du code source

COPY . /code/


# 6. Exposition du port
EXPOSE 8000

# 7. Lancement de l'API

CMD ["uvicorn", "app.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]