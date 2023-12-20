from pydantic import BaseModel

class GetIndexResponse(BaseModel):
    msg:str

class GetTradResponse(BaseModel):
    word:str
    trad:str

class PostTradResponse(BaseModel):
    word: str
    dictionnary: str
    trad: str

class PostDictResponse(BaseModel):
    id: int
    name: str

class PostDict_LigneResponse(BaseModel):
    letter: str
    trad: str
    dict_id: int

class TradResponse(BaseModel):
    trad:str
 
class UpdateResponse(BaseModel):
    letter: str
    trad: str
    dict_id: int

class DeleteResponse(BaseModel):
    message: str

