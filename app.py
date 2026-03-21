from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, validator
from datetime import datetime
import os
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()

# Configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/color_platform"
)

# Convert postgres:// to postgresql:// for SQLAlchemy 2.0
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Initialize FastAPI
app = FastAPI(
    title="Color Educational Platform",
    description="API for color learning platform",
    version="1.0.0"
)

# CORS Configuration - Update allowlist for your domain
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://127.0.0.1:3000",
    FRONTEND_URL,  # Your deployed domain
    # Add your production domain here, e.g., "https://yourdomain.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Setup
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Ensure connection is alive before using
    pool_size=5,
    max_overflow=10,
    echo=False  # Set to True for SQL debugging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Database Models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    age = Column(Integer, nullable=False)
    designation = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# Pydantic Models for request validation
class UserLogin(BaseModel):
    name: str
    age: int
    designation: str
    location: str
    email: str

    @validator('name', 'designation', 'location', 'email')
    def validate_strings(cls, v):
        if isinstance(v, str):
            v = v.strip()
        if not v:
            raise ValueError('Field cannot be empty')
        return v

    @validator('age')
    def validate_age(cls, v):
        if v < 1 or v > 150:
            raise ValueError('Age must be between 1 and 150')
        return v

    @validator('email')
    def validate_email(cls, v):
        if '@' not in v or '.' not in v:
            raise ValueError('Invalid email format')
        return v.lower()

    class Config:
        schema_extra = {
            "example": {
                "name": "John Doe",
                "age": 20,
                "designation": "Student",
                "location": "New York",
                "email": "john@example.com"
            }
        }


class UserResponse(BaseModel):
    id: int
    name: str
    age: int
    designation: str
    location: str
    email: str
    created_at: datetime

    class Config:
        orm_mode = True


# Initialize Database
def init_db():
    Base.metadata.create_all(bind=engine)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Startup Event
@app.on_event("startup")
def startup_event():
    init_db()
    print("✅ Database initialized successfully")


# Health Check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Color Educational Platform API"
    }


# Login Endpoint
@app.post("/login", response_model=dict)
async def login(user_data: UserLogin, db: Session = None):
    """
    User login/registration endpoint.
    Stores user information in PostgreSQL database.
    """
    try:
        # Get database session
        db = SessionLocal()

        # Check if email already exists
        existing_user = db.query(User).filter(
            User.email == user_data.email
        ).first()

        if existing_user:
            return {
                "success": True,
                "message": "Welcome back!",
                "user_id": existing_user.id
            }

        # Create new user
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
        db.close()

        return {
            "success": True,
            "message": "Registration successful!",
            "user_id": new_user.id
        }

    except Exception as e:
        db.close()
        print(f"❌ Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process login. Please try again."
        )


# Get all users (for testing/admin purposes)
@app.get("/users", response_model=list[UserResponse])
async def get_users(db: Session = None):
    """
    Get all registered users (for testing only - remove in production)
    """
    try:
        db = SessionLocal()
        users = db.query(User).all()
        db.close()
        return users
    except Exception as e:
        db.close()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch users"
        )


# Get user by ID
@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = None):
    """
    Get user by ID
    """
    try:
        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        db.close()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user

    except HTTPException:
        raise
    except Exception as e:
        db.close()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user"
        )


# Root endpoint
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
        reload=False  # Set to True only for development
    )
