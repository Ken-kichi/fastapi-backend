from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from models import Token
from auth import Auth
import os
from datetime import timedelta
from dotenv import load_dotenv
import jwt
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from models import User, TokenData,UserReadAll

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

load_dotenv()

SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = os.environ["ALGORITHM"]
ACCESS_TOKEN_EXPIRE_MINUTES = os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"]

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/token")

auth = Auth(
    SECRET_KEY=SECRET_KEY,
    ALGORITHM=ALGORITHM,
    pwd_context=pwd_context,
    oauth2_schema=oauth2_schema
)

async def get_current_user(token=Depends(oauth2_schema)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except InvalidTokenError:
        raise credentials_exception
    user_dict = auth.get_user(email=email)
    return user_dict

async def get_current_active_user(current_user:User=Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400,detail="Inactivate user")
    return current_user

@router.post("/token")
async def login_for_access_token(
    form_data:OAuth2PasswordRequestForm = Depends()
)->Token:
    user = auth.authenticate_user(
        email=form_data.username,
        password=form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = auth.create_access_token(
        data={"sub":user.email},
        expires_delta=access_token_expires
    )

    response_user = UserReadAll(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_manager=user.is_manager,
        disabled=user.disabled
    )

    return Token(access_token=access_token,token_type="bearer",user=response_user)

def main():
    print(auth.get_password_hash("hashedpassword123"))

if __name__ == "__main__":
    main()
