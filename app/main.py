from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import du router depuis ton dossier api/routes.py
#from app.api.routes_plafonds import router as api_router

# Initialisation
app = FastAPI(
    title="Gestion de Budget API",
    version="1.0.0"
)

# Configuration CORS (Indispensable pour que ton HTML parle à l'API)
origins = ["*"] # Pour le dev, on accepte tout. En prod, mets l'URL de ton site.

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- INCLUSION DU ROUTER ---
# On ajoute le préfixe "/api" ici. 
# Donc les routes deviennent /api/data/... et /api/plafond/...
#app.include_router(api_router, prefix="/api")

# Route racine pour tester
@app.get("/")
async def root():
    return {"message": "API en ligne. Routes disponibles sous /api/"}
