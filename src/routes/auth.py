from fastapi import APIRouter, HTTPException, Depends, status, Path, Query, Security
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.repository import users as reps_users
from src.schemas.user import UserSchema, TokenSchema, UserResponse
from src.services.auth import auth_service

import re
from datetime import date, timedelta

router = APIRouter(prefix='/auth', tags=['auth'])
get_refresh_token = HTTPBearer() #____9.12.A&A____

#__________________2.12.A&A_______________________________________________________________________________________
@router.post("/signup")
#____6.12.A&A_____________________________реалізація____________________________
async def signup(body: UserSchema, db: AsyncSession = Depends(get_db)):
    exist_user = await reps_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await reps_users.create_user(body, db)
    return new_user

#__________________2.12.A&A_______________________________________________________________________________________
@router.post("/login", response_model=TokenSchema)
#____7.12.A&A_____________________________реалізація____________________________
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await reps_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email, "test": "Ярослав Вдовенко"})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await reps_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

#__________________2.12.A&A_______________________________________________________________________________________
@router.get('/refresh_token', response_model=TokenSchema)
#____9.12.A&A_____________________________реалізація____________________________
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(get_refresh_token),
                        db: AsyncSession = Depends(get_db)):
    
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await reps_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await reps_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await reps_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}