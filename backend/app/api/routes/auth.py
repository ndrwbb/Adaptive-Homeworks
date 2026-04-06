from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models.learner_state import LearnerState
from app.models.user import User
from app.schemas.auth import RegisterIn, TokenOut, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


def serialize_user(user: User) -> UserOut:
    return UserOut(id=user.id, email=user.email, full_name=user.full_name, role=user.role)


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = User(
        email=data.email.lower().strip(),
        full_name=data.full_name.strip(),
        password_hash=hash_password(data.password),
        role=data.role,
    )
    db.add(user)
    db.flush()

    if data.role == "student":
        db.add(LearnerState(user_id=user.id, skill_score=50))

    db.commit()
    db.refresh(user)
    return serialize_user(user)


@router.post("/login", response_model=TokenOut)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form.username.lower().strip()).first()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(subject=user.email)
    return TokenOut(access_token=token, user=serialize_user(user))


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return serialize_user(user)

