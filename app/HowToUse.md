git checkout accueil
git pull origin accueil
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn sqlalchemy
python3 init_db.py
uvicorn app.main:app --reload
