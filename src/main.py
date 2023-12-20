from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from .params import PostTraduction, PostDico, PostDicoLigne, Traduction, Update, supprimer
from .responses import GetIndexResponse, PostTradResponse, GetTradResponse, PostDictResponse, PostDict_LigneResponse, TradResponse, UpdateResponse, DeleteResponse
from .models import Trad, Dict, Dict_Ligne
from .database import Base, engine, SessionLocal
from typing import List, Tuple

# initialisation bdd et creation table
Base.metadata.create_all(bind=engine)


app = FastAPI()
# ouverture fermeture de la bdd pour chaques requête
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from sqlalchemy.orm import Session

# Suppression du dico
@app.delete('/dico', response_model=DeleteResponse)
def delete(dico_nom: str, db: Session = Depends(get_db)):

    # Trouve le dictionnaire en fonction de son nom
    db_dict = db.query(Dict).filter(Dict.name.ilike(dico_nom)).first()

    # Vérifier que le dictionnaire est réel
    if not db_dict:
        raise HTTPException(status_code=404, detail="Dictionnaire non trouvé")

    # Créer une liste de lettre 
    lettre = [chr(ord('A') + i) for i in range(26)]

    # Supprimer les ligne de lettre
    for letter in lettre:
        db_dict_ligne = db.query(Dict_Ligne).filter(Dict_Ligne.trad_id == db_dict.id, Dict_Ligne.letter == letter).first()
        if db_dict_ligne:

        # Supprimer l'entrée si elle existe
            db.delete(db_dict_ligne)

    # Supprimer le dictionnaire
    db.delete(db_dict)
    db.commit()

    return {
        'message':  f"Le dictionnaire {db_dict.name} a été supprimé avec succès"
    }
    # MAJ du dico
@app.post('/dico/{dico_nom}/maj', response_model=List[UpdateResponse])
def update(params: Update, dico_nom: str, db: Session = Depends(get_db)):
    # Récupérer l'ID du dico en fonction de son nom
    db_dict = db.query(Dict).filter(Dict.name.ilike(dico_nom)).first()

    # Vérifier que le dico existe
    if not db_dict:
        raise HTTPException(status_code=404, detail="Dictionnaire non trouvé")

    # Vérifie que la liste de traductions correspond au nombre de lettres
    if len(params.trads) != 26:
        raise HTTPException(status_code=400, detail="La liste de traductions doit contenir exactement 26 éléments")

    # Créer une liste de lettre 
    lettre = [chr(ord('A') + i) for i in range(26)]

    # Parcourir les lettres et mettre à jour ou ajouter les traductions
    result = []
    for letter, trad in zip(lettre, params.trads):
        db_dict_ligne = db.query(Dict_Ligne).filter(Dict_Ligne.trad_id == db_dict.id, Dict_Ligne.letter == letter).first()
        
        if db_dict_ligne:
            # Mettre à jour 
            db_dict_ligne.trad = trad
        else:
            # Ajouter une nouvelle entrée si il y en a pas
            db_dict_ligne = Dict_Ligne(letter=letter, trad=trad, trad_id=db_dict.id)
            db.add(db_dict_ligne)

        result.append({
            'letter': letter,
            'trad': trad,
            'dict_id': db_dict.id,
        })

    db.commit()
    db.refresh(db_dict)

    return result
# traduire mot
@app.post('/dico/{dico_nom}/traduction', response_model=TradResponse)
def traduire(params: Traduction, dico_nom: str, db: Session = Depends(get_db)):
    # Récupérer l'ID du dico 
    db_dict = db.query(Dict).filter(Dict.name.ilike(dico_nom)).first()

    # Vérifier que le dico existe
    if not db_dict:
        raise HTTPException(status_code=404, detail="Dictionnaire non trouvé")
    lettre = list(params.mot)

    result = ""
    for i,letter in enumerate(lettre):
        db_dict_ligne = db.query(Dict_Ligne).filter(Dict_Ligne.trad_id == db_dict.id, Dict_Ligne.letter == letter).first()
        result += db_dict_ligne.trad
        if i < len(lettre) - 1: 
            result += " "

    return TradResponse(trad=result)
    

@app.post('/dico/{dico_nom}', response_model=List[PostDict_LigneResponse])
def newDico_Ligne(params: PostDicoLigne, dico_nom: str, db: Session = Depends(get_db)):
    # Récupérer l'ID du dico
    db_dict = db.query(Dict).filter(Dict.name.ilike(dico_nom)).first()

   
    if not db_dict:
        raise HTTPException(status_code=404, detail="Dictionnaire non trouvé")

    if len(params.trads) != 26:
        raise HTTPException(status_code=400, detail="La liste de traductions doit contenir exactement 26 éléments")

    # Créer une liste 
    lettre = [chr(ord('A') + i) for i in range(26)]

    result = []
    for letter, trad in zip(lettre, params.trads):
        
        existing_entry = db.query(Dict_Ligne).filter(Dict_Ligne.trad_id == db_dict.id, Dict_Ligne.letter == letter).first()
    
        if existing_entry:
            raise HTTPException(status_code=400, detail=f"Une entrée pour la trad {trad} existe déjà.")

        db_dict_ligne = Dict_Ligne(letter=letter, trad=trad, trad_id=db_dict.id)
        db.add(db_dict_ligne)
        result.append({
            'letter': letter,
            'trad': trad,
            'dict_id': db_dict.id,
        })

    db.commit()
    db.refresh(db_dict)

    return result
# creation dico
@app.post('/dico', response_model=PostDictResponse)
def newDico(params: PostDico, db: Session = Depends(get_db)):
    db_dict = Dict(name=params.name.strip())
    db.add(db_dict)
    db.commit()
    db.refresh(db_dict)

    return{
        'id': db_dict.id,
        'name': db_dict.name   
    }

# ajouter une traduction
@app.post('/traduction', response_model=PostTradResponse)
def postTrad(params: Traduction, db:Session = Depends(get_db)):
    trad_db = Trad(trad = "...---...", word=params.word, dictionnary=params.dictionnary)
    db.add(trad_db)
    db.commit()

    return{
        'word': params.word,
        'dictionnary': params.dictionnary,
        'trad': "...---..."
    }

@app.get("/", response_model=GetIndexResponse)
def index():
    return {'msg': 'Hello World !'}
@app.get("/traduction/(word)", response_model=GetTradResponse)
def getTrad(word: str):
    return{
        "word" : word,
        "trad" : "... --- ..."
    }

