from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt import PyJWTError
from .config import get_settings
from .schemas import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    settings = get_settings()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET, 
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        session_id: str = payload.get("session_id")
        if not user_id or not session_id:
            raise credentials_exception
        return TokenData(user_id=user_id, session_id=session_id)
    except PyJWTError:
        raise credentials_exception
    
def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    payload = jwt.decode(token)
    return payload.get("user_id")