# Color Educational Platform - Backend API

## 🔄 Migration from SQLite to PostgreSQL

This backend has been **converted from SQLite to PostgreSQL** for production deployment. SQLite files (`.db`) will no longer be used.

### Why PostgreSQL?
- ✅ **Persistent Storage**: Data survives server restarts
- ✅ **Production-Ready**: Suitable for enterprise deployments
- ✅ **Render Compatible**: Free tier includes PostgreSQL database
- ✅ **Scalability**: Handles concurrent connections better
- ❌ **SQLite Issue**: Data lost on Render dyno restarts (free tier)

---

## 📂 Project Structure

```
backend/
├── app.py                 # Main FastAPI application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create `.env` File
```bash
cp .env.example .env
```

Edit `.env` for local development:
```env
DATABASE_URL=postgresql://colorsfusions:zyw3JOqCfG61PpmnDctyGF9Spm6VthKA@dpg-d6v1q3lm5p6s73a324p0-a.singapore-postgres.render.com/ludosfusion
PORT=8000
```

### 3. Run Backend
```bash
python -m uvicorn app:app --reload
```

Visit: `http://localhost:8000`

---

## 🛠️ Key Changes from Previous Version

### Database
| Feature | SQLite | PostgreSQL |
|---------|--------|-----------|
| Storage | File-based | Server-based |
| Persistent | ❌ No (Render) | ✅ Yes |
| Performance | Okay | Excellent |
| Concurrency | Limited | Unlimited |

### New Dependencies
```
psycopg2-binary    # PostgreSQL driver
sqlalchemy         # ORM (cleaner code)
pydantic          # Data validation
python-dotenv     # Environment variables
```

### Code Improvements
- ✅ Input validation with Pydantic
- ✅ Error handling with proper HTTP status codes
- ✅ Connection pooling for better performance
- ✅ Environment variable configuration
- ✅ Health check endpoint
- ✅ Unique email constraint (prevents duplicates)
- ✅ User creation timestamp

---

## 📧 API Documentation

### Initialize Database
Automatically runs on startup

### Health Check
```
GET /health
```
```json
{
  "status": "healthy",
  "service": "Color Educational Platform API"
}
```

### User Login/Registration
```
POST /login
Content-Type: application/json
```

**Request:**
```json
{
  "name": "John Doe",
  "age": 20,
  "designation": "Student",
  "location": "New York",
  "email": "john@example.com"
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Registration successful!",
  "user_id": 1
}
```

**Response (Returning User):**
```json
{
  "success": true,
  "message": "Welcome back!",
  "user_id": 1
}
```

**Response (Error):**
```json
{
  "detail": "Failed to process login. Please try again."
}
```

### Get All Users
```
GET /users
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "age": 20,
    "designation": "Student",
    "location": "New York",
    "email": "john@example.com",
    "created_at": "2024-03-21T12:00:00"
  }
]
```

### Get User by ID
```
GET /users/{user_id}
```

---

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    age INTEGER NOT NULL,
    designation VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🌍 Environment Variables

```env
# PostgreSQL Connection String
DATABASE_URL=postgresql://user:password@host:port/dbname

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:3000

# Server Port
PORT=8000
```

---

## 🔒 CORS Configuration

The API allows requests from:
- `http://localhost:3000`
- `http://localhost:5500`
- Your deployed domain

To add your domain:
1. Edit `ALLOWED_ORIGINS` in `app.py`
2. Add your domain: `https://yourdomain.com`

---

## 🧪 Testing Locally

### 1. Start Backend
```bash
python -m uvicorn app:app --reload
```

### 2. Test Health Check
```bash
curl http://localhost:8000/health
```

### 3. Test Login
```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "age": 25,
    "designation": "Student",
    "location": "City",
    "email": "test@example.com"
  }'
```

### 4. Get Users
```bash
curl http://localhost:8000/users
```

---

## 🐛 Debugging

### Enable SQL Logging
In `app.py`, change:
```python
echo=False  # Change to True
```

### Check Database Connection
```bash
psql postgresql://user:password@host:port/dbname
```

### View Logs
```bash
python -m uvicorn app:app --reload --log-level debug
```

---

## 📋 Deployment Steps

See [DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md) for:
- ✅ Local PostgreSQL setup
- ✅ Render.com deployment
- ✅ Environment configuration
- ✅ Troubleshooting

---

## 🔐 Security Checklist

- [ ] Add `.env` to `.gitignore`
- [ ] Use strong database password
- [ ] Enable HTTPS in production
- [ ] Validate all inputs (already done)
- [ ] Set secure CORS origins
- [ ] Use environment variables for secrets
- [ ] Remove old SQLite `.db` files

---

## 📊 Database Migration (If Existing Data)

If you had users in SQLite, manually migrate:

```python
# Backup old data from SQLite
import sqlite3
conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM users")
old_users = cursor.fetchall()
conn.close()

# Insert into PostgreSQL using the app's endpoints
for user in old_users:
    # Call POST /login for each user
    pass
```

---

## 🎯 Next Steps

1. ✅ Configure `.env` file
2. ✅ Install PostgreSQL locally
3. ✅ Test backend locally
4. ✅ Deploy to Render
5. ✅ Update frontend config
6. ✅ Deploy frontend to Netlify

---

## 📞 Support

For issues:
1. Check [DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md)
2. Review error logs
3. Test database connection
4. Verify environment variables

---

**Last Updated:** March 2024  
**Version:** 2.0.0 (PostgreSQL Edition)
