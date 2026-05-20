from fastapi import Header, HTTPException, Depends
from jose import JWTError, jwt
from ..config import settings
from typing import Optional


def verify_token(authorization: Optional[str] = Header(None)) -> dict:
    """Verificar JWT token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"user_id": int(user_id), "token": token}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header")


async def get_current_user(auth_data: dict = Depends(verify_token)) -> dict:
    """Get current authenticated user"""
    return auth_data
