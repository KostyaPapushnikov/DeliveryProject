from fastapi import FastAPI, Form, status, HTTPException, Depends, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from models import *
from database import engine
from sqlmodel import Session, select
from typing import Annotated, Optional


app = FastAPI(
    description='Delivery Project',
    docs_url=None,
    redoc_url=None
)

templates = Jinja2Templates('templates')

session = Session(bind=engine)



@app.get('/', response_model=Food, tags=['Pages'])
async def get_all_food(request: Request):
    statement = select(Food)
    result = session.exec(statement).all()
    cookie = request.cookies.get('id')
    
    flag = False
    
    if cookie != None:
        flag = True
    
    if result == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return templates.TemplateResponse(
        request = request,
        name = 'index.html',
        context = {
            'result': result,
            
        }
    )

def check_admin_cookie(request: Request):
    admin_id = request.cookies.get("admin_id")
    if not admin_id:
        raise HTTPException(status_code=403, detail="Access forbidden")

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html(request: Request):
    check_admin_cookie(request)
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")

@app.get("/redoc", include_in_schema=False)
async def custom_redoc_html(request: Request):
    check_admin_cookie(request)
    return get_redoc_html(openapi_url="/openapi.json", title="ReDoc")

@app.get('/food/{food_id}', response_model=Food, tags=['Pages'])
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
            'price': result.price
        }
    )

@app.get('/login', tags=['Pages'])
async def get_login_page(request: Request):
    cookie = request.cookies.get('id')
    seller_cookie = request.cookies.get('seller_id')
    
    if cookie != None:
        return RedirectResponse('/profile/'+cookie, status_code=302)
    elif seller_cookie != None:
        return RedirectResponse('/profile/'+seller_cookie, status_code=302)
    
    return templates.TemplateResponse('login.html', {'request': request})

@app.get('/registration', tags=['Pages'])
async def get_registration_page(request: Request):
    return templates.TemplateResponse('registration.html', {'request': request})

@app.get('/create_food', tags=['Pages'])
async def get_create_food_page(request: Request):
        
    cookie = request.cookies.get('seller_id')
    
    if cookie == None:
        return RedirectResponse('/login', status_code=302)
    
    return templates.TemplateResponse('create_food.html', {'request': request})

@app.get('/profile/{cust_id}', response_model=Customer, tags=['Pages'])
async def get_profile(request: Request, cust_id: int):
    cookie = request.cookies.get('seller_id')
    
    flag = False
    
    if cookie != None:
        flag = True
        
    statement = select(Customer).where(Customer.id == cust_id)
    result = session.exec(statement).first()
    

    if result == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    return templates.TemplateResponse(
        request = request,
        name = 'profile.html',
        context = {
            'id': result.id,
            'first_name': result.first_name,
            'second_name': result.second_name,
            'phone': result.phone,
            'email': result.email,
            'address': result.address,
            'flag': flag
        }
    )

@app.get('/cart', tags=['Pages'])
async def get_cart_page(request: Request):
    return templates.TemplateResponse(request=request, name='cart.html')




@app.post('/create_food', response_model=Food, response_class=RedirectResponse,
          status_code=status.HTTP_201_CREATED, tags=['Food'])
async def create_a_food(title: str = Form(...), 
                        price: int = Form(...)) -> RedirectResponse:
    new_food = Food(title=title, price=price)

    session.add(new_food)
    session.commit()
    session.rollback()
    
    return RedirectResponse('/', status_code=302)

@app.put('/food/{food_id}', response_model=Food, tags=['Food'])
async def change_a_food(food_id: int, food: Annotated[Food, Depends()]):
    statement = select(Food).where(Food.id == food_id)
    result = session.exec(statement).first()

    result.title = food.title
    result.price = food.price
    
    session.commit()

    return result
    
@app.delete('/food/{food_id}', status_code=status.HTTP_204_NO_CONTENT, tags=['Food'])
async def delete_a_food(food_id: int):
    statement = select(Food).where(Food.id == food_id)
    result = session.exec(statement).one_or_none()

    if result == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail='Resourse Not Found')
    
    session.delete(result)
    session.commit()

    return result




@app.post('/registration', status_code=status.HTTP_201_CREATED, 
          response_class=RedirectResponse, tags=['Account'])
async def create_a_customer(first_name: str = Form(...), 
                            second_name: str = Form(...), 
                            email: str = Form(...), 
                            address: str = Form(...),
                            phone: int = Form(...),
                            password: str = Form(...),
                            remember: Optional[bool] = Form(default=False),
                            seller: Optional[bool] = Form(default=False),
                            admin: Optional[bool] = Form(default=False)) -> RedirectResponse:
    
    statement = select(Customer).where(Customer.email == email or Customer.phone == phone)
    result = session.exec(statement).one_or_none()
    
    new_cust = Customer(first_name=first_name, second_name=second_name,
                        phone=phone, email=email, password=password,
                        address=address, seller=seller, admin=admin)
    
    if result == None:
        if seller == None:
            session.add(new_cust)
            session.commit()
            
            response = RedirectResponse('/profile/'+str(new_cust.id), status_code=302)
            if remember == True:
                response.set_cookie(key="id", value=str(new_cust.id), max_age=15695000)
            return response
        
        else:
            session.add(new_cust)
            session.commit()
                
            response = RedirectResponse('/profile/'+str(new_cust.id), status_code=302)
            if remember == True:
                    response.set_cookie(key="seller_id", value=str(new_cust.id), max_age=15695000)
            return response
        

    return RedirectResponse('/registration', status_code=302)

@app.post('/login', response_class=RedirectResponse, tags=['Account'])
async def get_cust(email_login: str = Form(...), 
                   password_login: str = Form(...),
                   remember: Optional[bool] = Form(default=False)) -> RedirectResponse:
    email_statement = select(Customer).where(Customer.email == email_login)
    email_result = session.exec(email_statement).first()
    
    password_statement = select(Customer).where(Customer.password == password_login)
    password_result = session.exec(password_statement).first()
    
    
    if email_result != None: 
        if email_result.id == password_result.id:
            response = RedirectResponse('/profile/'+str(email_result.id), status_code=302)
            if remember == True:
                if email_result.admin == True:
                    response.set_cookie(key="admin_id", value=str(email_result.id), max_age=15695000)
                response.set_cookie(key="id", value=str(email_result.id), max_age=15695000)
            return response

@app.delete('/profile/{cust_id}', status_code=status.HTTP_204_NO_CONTENT, 
            tags=['Account'])
async def delete_a_cust(cust_id: int):
    statement = select(Customer).where(Customer.id == cust_id)
    result = session.exec(statement).one_or_none()

    if result == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail='Resourse Not Found')
    
    session.delete(result)
    session.commit()
    session.rollback()

    return result

@app.get('/profile', tags=['Account'])
async def switch_account(response: Response):
    response = RedirectResponse('/login', status_code=302)
    response.delete_cookie('id')
    return response

