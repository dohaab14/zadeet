# --- FRONTEND DOCKERFILE ---

# 1. Image Nginx légère
FROM nginx:alpine 

# 2. Suppression de la config par défaut de Nginx
RUN rm /etc/nginx/conf.d/default.conf

# 3. Copie de notre fichier de configuration Nginx (créé à l'étape 2)

COPY nginx.conf /etc/nginx/nginx.conf

# 4. Copie des fichiers statiques du projet vers le dossier web de Nginx

# Copie des templates (HTML) à la racine du serveur web
COPY app/frontend/templates/ /usr/share/nginx/html/

# Copie des scripts JS dans /js
COPY app/frontend/js/ /usr/share/nginx/html/js/

# Copie du style CSS dans /static
COPY app/frontend/static/ /usr/share/nginx/html/static/

# 5. Exposition du port 80 (standard Web)
EXPOSE 80

# 6. Lancement de Nginx
CMD ["nginx", "-g", "daemon off;"]