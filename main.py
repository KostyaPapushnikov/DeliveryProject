from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from typing import List
from pydantic import BaseModel, Field

app = FastAPI(
    title='Delivery project'
)

templates = Jinja2Templates(directory="templates")

