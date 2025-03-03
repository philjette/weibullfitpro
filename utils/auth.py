import bcrypt
import os
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional
from sqlalchemy.orm import Session
from utils.database import User, get_db

# Generate a secure secret key for JWT
SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or os.urandom(32).hex()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )

def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')

def create_access_token(data: dict) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    expires = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expires})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str) -> Optional[dict]:
    """Verify JWT token and return user data."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"user_id": payload.get("sub")}
    except JWTError:
        return None

def authenticate_user(email: str, password: str, db: Session) -> Optional[User]:
    """Authenticate user credentials."""
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password):
        return None
    return user

def create_user(email: str, password: str, db: Session) -> tuple[bool, str]:
    """Create a new user."""
    if db.query(User).filter(User.email == email).first():
        return False, "Email already registered"
    
    try:
        hashed_password = get_password_hash(password)
        user = User(email=email, password=hashed_password)
        db.add(user)
        db.commit()
        return True, "User created successfully"
    except Exception as e:
        db.rollback()
        return False, f"Error creating user: {str(e)}"
