from fastapi import FastAPI, status, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from models import *
from database import engine
from sqlmodel import Session, select
from typing import List, Annotated

app = FastAPI()

templates = Jinja2Templates('templates')

session = Session(bind=engine)


@app.get('/', response_model=List[Food], status_code=status.HTTP_200_OK)
async def get_all_food(request: Request):
    statement = select(Food)
    result = session.exec(statement).all()
    
    if result == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return templates.TemplateResponse(
        request = request,
        name = 'index.html',
        context = {
            'result': result
        }
    )

@app.post('/food', response_model=Food, status_code=status.HTTP_201_CREATED)
async def create_a_food(food: Annotated[Food, Depends()]):
    new_food = Food(id=food.id, title=food.title, price=food.price)

    session.add(new_food)
    session.commit()
    
    return new_food

@app.get('/food/{food_id}', response_model=Food)
async def get_a_food(request: Request, food_id: int):
    statement = select(Food).where(Food.id == food_id)
    result = session.exec(statement).first()

    if result == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    return templates.TemplateResponse(
        request = request,
        name = 'food_card.html',
        context = {
            'id': result.id,
            'title': result.title,
            'price': result.price,
        }
    )

@app.put('/food/{food_id}', response_model=Food)
async def change_a_food(food_id: int, food: Annotated[Food, Depends()]):
    statement = select(Food).where(Food.id == food_id)
    result = session.exec(statement).first()

    result.title = food.title
    result.price = food.price
    
    session.commit()

    return result
    

@app.delete('/food/{food_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_a_food(food_id: int):
    statement = select(Food).where(Food.id == food_id)
    result = session.exec(statement).one_or_none()

    if result == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail='Resourse Not Found')
    
    session.delete(result)

    return result
    
@app.get('/login')
async def get_login_page(request: Request):
    return templates.TemplateResponse('login.html', {'request': request})

@app.get('/')
async def get_index_page(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})