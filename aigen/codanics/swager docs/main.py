# import the libraires
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World", "message": "Welcome to the FastAPI application!"}

@app.post("/items/")
async def create_item(item: dict):
    return {"Message": "Item created successfully", "item": item}


@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"Message": f"item_id is {item_id}"}

@app.get("/users")
async def read_users():
    return {"Message": "List of users"}

@app.get("/users/{user_id}")
async def read_user(user_id: int):
    return {"Message": f"User ID is {user_id}"}




