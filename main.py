from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()
SQLALCHEMY_DATABASE_URL = "sqlite:///./recipes.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class Recipe(Base):
    __tablename__ = "recipes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    ingredients = Column(String)
    instructions = Column(String)


Base.metadata.create_all(bind=engine)



class RecipeCreate(BaseModel):
    name: str
    ingredients: str
    instructions: str

class RecipeRead(RecipeCreate):
    id: int

@app.post("/recipes/", response_model= RecipeRead)
def create_recipe(recipe: RecipeCreate):
    db = SessionLocal()
    db_recipe = Recipe(**recipe.dict())
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    db.close()
    return db_recipe

@app.get("/recipes/", response_model = List[RecipeRead])
def read_recipes():
    db = SessionLocal()
    recipes = db.query(Recipe).all()
    db.close()
    return recipes

@app.get("/recipes/{recipe_id}", response_model = RecipeRead)
def read_recipe(recipe_id: int):
    db = SessionLocal()
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    db.close()
    if recipe is None:
        raise HTTPException(status_code= 404, detail = "Recipe not found")
    return recipe

@app.put("/recipes/{recipe_id}", response_model = RecipeRead)
def update_recipe(recipe_id: int, updated: RecipeCreate):
    db = SessionLocal()
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if recipe is None:
        db.close()
        raise HTTPException(status_code= 404, detail = "Recipe not found")
    recipe.name = updated.name
    recipe.ingredients = updated.ingredients
    recipe.instructions = updated.instructions
    db.commit()
    db.refresh(recipe)
    db.close()
    return recipe

@app.delete("/recipes/{recipe_id}")
def delete_recipe(recipe_id: int):
    db = SessionLocal()
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if recipe is None:
        db.close()
        raise HTTPException(status_code= 404, detail = "Recipe not found")
    db.delete(recipe)
    db.commit()
    db.close()
    return{"message": "Recipe deleted"}