from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base

class Trad(Base):
    __tablename__="trads"

    id = Column(Integer, primary_key=True, index=True)
    trad = Column(String(255))
    word = Column(String(40))
    dictionnary = Column(String(40))   

class  Dict(Base):
    __tablename__="dict"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))

    lines = relationship("Dict_Ligne", back_populates="dico")

class Dict_Ligne(Base):
    __tablename__="dict_ligne"

    id = Column(Integer, primary_key=True, index=True)
    letter = Column(String(4))
    trad = Column(String(4))
    trad_id = Column(Integer, ForeignKey("dict.id"))

    dico = relationship("Dict", back_populates="lines")
     

