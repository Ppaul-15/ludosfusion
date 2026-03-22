from datetime import datetime
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, field_validator
from sqlalchemy import Column, DateTime, Integer, String, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker
import uvicorn

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/color_platform"
)

app = FastAPI(
    title="Color Educational Platform",
    description="API for color learning platform",
    version="1.0.0"
)

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://127.0.0.1:3000",
    "https://glowing-faun-704609.netlify.app",
    FRONTEND_URL,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    age = Column(Integer, nullable=False)
    designation = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserLogin(BaseModel):
    name: str
    age: int
    designation: str
    location: str
    email: str

    @field_validator("name", "designation", "location", "email")
    @classmethod
    def validate_strings(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Field cannot be empty")
        return value

    @field_validator("age")
    @classmethod
    def validate_age(cls, value: int) -> int:
        if value < 1 or value > 150:
            raise ValueError("Age must be between 1 and 150")
        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if "@" not in value or "." not in value:
            raise ValueError("Invalid email format")
        return value.lower()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "John Doe",
                "age": 20,
                "designation": "Student",
                "location": "New York",
                "email": "john@example.com"
            }
        }
    )


class UserResponse(BaseModel):
    id: int
    name: str
    age: int
    designation: str
    location: str
    email: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


@app.on_event("startup")
def startup_event() -> None:
    init_db()
    print("Database initialized successfully")


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Color Educational Platform API"
    }


@app.post("/login", response_model=dict)
async def login(user_data: UserLogin):
    """
    User login/registration endpoint.
    Stores user information in PostgreSQL database.
    """
    db: Session = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.email == user_data.email).first()

        if existing_user:
            return {
                "success": True,
                "message": "Welcome back!",
                "user_id": existing_user.id
            }

        new_user = User(
            name=user_data.name,
            age=user_data.age,
            designation=user_data.designation,
            location=user_data.location,
            email=user_data.email
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {
            "success": True,
            "message": "Registration successful!",
            "user_id": new_user.id
        }
    except Exception as exc:
        db.rollback()
        print(f"Login error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process login. Please try again."
        )
    finally:
        db.close()


@app.get("/users", response_model=list[UserResponse])
async def get_users():
    """
    Get all registered users.
    """
    db: Session = SessionLocal()
    try:
        return db.query(User).all()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch users"
        )
    finally:
        db.close()


@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """
    Get user by ID.
    """
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return user
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user"
        )
    finally:
        db.close()


@app.get("/")
async def root():
    return {
        "service": "Color Educational Platform API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "login": "POST /login",
            "users": "GET /users",
            "user_by_id": "GET /users/{user_id}"
        }
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )
