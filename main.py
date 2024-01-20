#3#plan
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy import text, select
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.routes import contacts
from src.routes import auth #2.12.A&A
from src.entity.models import Contact
from src.repository import contacts as reps_contacts


app = FastAPI()


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api") #2.12.A&A
app.include_router(contacts.router, prefix="/api")

@app.get("/")
def index():
    return {"message": "Contact Application"}

@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    try:
        # Make request
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")


@app.get("/find_contact")
async def find_contact(
    db: AsyncSession = Depends(get_db),
    f_name: str = Query(None, min_length=3, max_length=50),
    l_name: str = Query(None, min_length=3, max_length=50),
    email: str = Query(None, regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
):
    filters = []
    if f_name:
        filters.append(Contact.f_name == f_name)
    if l_name:
        filters.append(Contact.l_name == l_name)
    if email:
        filters.append(Contact.email == email)

    query = select(Contact).filter(*filters)
    result = await db.execute(query)
    contacts = result.scalars().all()

    return {"contacts": contacts}



