from fastapi import FastAPI, Query, HTTPException
from typing import List
from pydantic import BaseModel, EmailStr, field_validator
from datetime import date
from db_functions import startup_event, execute_query

app = FastAPI()

current_date = date.today()
current_year = current_date.year


class User(BaseModel):
    name: str = Query('none', description='Enter your name')
    email: EmailStr = Query(..., description='Enter your emailaddres')
    order_list: list = Query('[seeOrder]', description='Enter the list with the order')

    @field_validator('email')
    @classmethod
    def validate_email(cls, value):
        try:
            return EmailStr(value)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Email was entered false, details: {str(e)}")


class UserResponse(BaseModel):
    response: List[User]


class Order(BaseModel):
    name_product: str = Query(..., description='Enter the name of your product')
    numeric_product: int = Query(1, description='Enter the numeric of the ordered products')
    price_product: float = Query(..., description='Enter the price of the product')

    @field_validator("numeric_product")
    async def validate_name(cls, value):
        if len(value) < 1 or value != int(value):
            raise HTTPException(status_code=400,
                                detail="The numeric must be bigger then 0 and be integer")
        return value

    @field_validator("price_product")
    async def validate_name(cls, value):
        if len(value) < 1:
            raise HTTPException(status_code=400,
                                detail="The numeric must be bigger then 0")
        return value


class OrderResponse(BaseModel):
    response: List[Order]


@app.on_event('startup')
async def startup_event():
    await startup_event()


@app.post('/new')
async def new(user: User, order: Order, datetime: str):
    datetime= str(current_date) + str(current_year)
    try:
        await execute_query("""
        INSERT INTO table(name, email, order_list, name_product, numeric_product, price_product, datetime) VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            user.name,
            user.email,
            user.order_list,
            order.name_product,
            order.numeric_product,
            order.price_product,
            datetime)
                            )
        raise HTTPException(status_code=201, detail="Query is succesful")

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Something went wrong, more details: {str(e)}")


@app.get('/get_data')
async def get_data(user: User):
    try:
        response = await execute_query("""
        SELECT * FROM table WHERE email = %s
        """, (user.email,))
        if not response:
            raise HTTPException(status_code=404, detail='Emailaddres was not found')

        data1 = [User(**row) for row in response[1:3]]
        data2 = [Order(**row) for row in response[3:]]

        return [UserResponse(response=data1), OrderResponse(response=data2)]

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Something went wrong, more details: {str(e)}")
