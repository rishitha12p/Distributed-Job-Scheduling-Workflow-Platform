from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import get_db
from app.models.job import User

oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/token")
def current_user(token: str = Depends(oauth2), db: Session = Depends(get_db)) -> User:
    try: username = jwt.decode(token, settings.secret_key, algorithms=["HS256"]).get("sub")
    except JWTError: raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.username == username).first()
    if not user or not user.active: raise HTTPException(status_code=401, detail="User unavailable")
    return user
