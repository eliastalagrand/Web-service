from pydantic import BaseModel
from typing import List

class PostTraduction(BaseModel):
    word:str
    dictionnary:str

class PostDico(BaseModel):
    name:str
    
class PostDicoLigne(BaseModel):
    trads: List[str]

class Traduction(BaseModel):
    mot: str

class Update(BaseModel):
    trads: List[str]

class supprimer(BaseModel):
    name:str

