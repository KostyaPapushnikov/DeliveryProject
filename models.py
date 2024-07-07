from typing import Optional
from sqlmodel import SQLModel, Field


class Customer(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    first_name: str
    second_name: str
    phone: int
    email: str
    password: str
    address: str
    seller: bool = Field(default=False)
    admin: bool = Field(default=False)
    
    
class Food(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    price: int

    