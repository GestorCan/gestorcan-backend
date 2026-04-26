from sqlalchemy import Column, Integer, String
from database import Base

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    telefono = Column(String)
