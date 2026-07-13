from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas, security
from app.limiter import limiter

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def register(request: Request, user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account.

    Allows user signup by verifying email uniqueness and hashing the plain password.

    - **user_in**: Registration details containing email and plain text password.
    - **db**: Database session dependency.

    **Possible HTTP status returns:**
    - **201 Created**: Registration succeeded. Returns the new user's ID, email, and creation timestamp.
    - **400 Bad Request**: If the email address is already registered in the system.
    - **422 Unprocessable Entity**: If input parameters fail regex, formatting, or missing property checks.
    - **429 Too Many Requests**: If client requests exceed the strict signup limit of 5 requests/minute.
    """
    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = security.hash_password(user_in.password)
    new_user = models.User(
        email=user_in.email,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=schemas.Token)
@limiter.limit("5/minute")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticate user credentials and issue a JWT token.

    Supports standard OAuth2 username/password login format (Url-encoded form data) to allow native Swagger auth.

    - **username**: Registered email.
    - **password**: User password.

    **Possible HTTP status returns:**
    - **200 OK**: Login succeeded. Returns a JWT access token and its token type ("bearer").
    - **400 Bad Request**: If email is not found or password verification fails.
    - **429 Too Many Requests**: If requests exceed the strict limit of 5 requests/minute per client IP.
    """
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid credentials"
        )
    
    access_token = security.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
