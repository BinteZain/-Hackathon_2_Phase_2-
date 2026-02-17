# 🚀 Hackathon Todo - Phase 2

A full-stack todo application with authentication, built as a monorepo for **Hackathon Phase 2**.

## 📋 Project Overview

This is **Phase 2** of the Hackathon project, featuring:
- ✅ User Authentication with Better Auth
- ✅ Task CRUD Operations
- ✅ Modern UI with Next.js and Tailwind CSS
- ✅ RESTful API with FastAPI
- ✅ PostgreSQL Database
- ✅ Docker Support
- ✅ Vercel Deployment Ready

## 🏗️ Project Structure

```
hackathon-todo/
├── frontend/              # Next.js + React + TypeScript
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── lib/
│   │   └── contexts/
│   ├── package.json
│   └── .env.example
├── backend/               # FastAPI + Python
│   ├── src/
│   │   ├── main.py
│   │   ├── models/
│   │   ├── schemas/
│   │   └── routes/
│   ├── requirements.txt
│   └── .env.example
├── vercel.json            # Vercel deployment config
├── docker-compose.yml     # Docker setup
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- Docker (optional, for containerized deployment)

### Local Development

#### 1. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your configuration

# Run the backend
uvicorn src.main:app --reload --port 8000
```

#### 2. Frontend Setup

```bash
cd frontend
npm install

# Copy environment variables
cp .env.example .env.local
# Edit .env.local with your configuration

# Run the frontend
npm run dev
```

The application will be available at `http://localhost:3000`

### Docker Deployment

```bash
# Create .env file in root directory
cp .env.example .env

# Start all services
docker-compose up --build
```

## ☁️ Vercel Deployment

### Frontend Deployment (Vercel)

1. **Install Vercel CLI** (optional):
   ```bash
   npm install -g vercel
   ```

2. **Deploy to Vercel**:
   ```bash
   # From project root
   vercel login
   vercel --prod
   ```

3. **Configure Environment Variables** in Vercel dashboard:
   - `NEXT_PUBLIC_API_URL` - Your backend API URL

4. **Build Settings**:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

### Backend Deployment Options

#### Option 1: Vercel Serverless Functions

1. Move backend code to `api/` directory
2. Deploy alongside frontend

#### Option 2: Separate Backend Service

- Deploy backend to Railway, Render, or Fly.io
- Update `NEXT_PUBLIC_API_URL` in frontend

#### Option 3: Docker Deployment

```bash
docker-compose -f docker-compose.yml up -d
```

## 🔧 Environment Variables

### Root `.env`

```env
POSTGRES_DB=todoapp
POSTGRES_USER=user
POSTGRES_PASSWORD=password
BETTER_AUTH_SECRET=your-secret-key
BACKEND_URL=http://localhost:4000/api/v1
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### Frontend `.env.local`

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### Backend `.env`

```env
DATABASE_URL=postgresql://user:password@localhost:5432/todoapp
BETTER_AUTH_SECRET=your-secret-key
```

## 🎯 Features

### Authentication
- User registration and login
- JWT token-based authentication
- Secure password hashing with bcrypt
- Better Auth integration

### Task Management
- Create, Read, Update, Delete tasks
- Toggle task completion status
- User-specific task isolation
- Real-time updates

### UI/UX
- Responsive design (mobile, tablet, desktop)
- Clean, modern interface
- Loading states and error handling
- Toast notifications

## 🧪 Sample Data

### Test Users
- **admin@example.com** / admin123
- **user1@example.com** / user123
- **user2@example.com** / user223

## 🔌 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration

### Tasks (Protected)
- `GET /api/v1/tasks` - Get all user tasks
- `GET /api/v1/tasks/{id}` - Get specific task
- `POST /api/v1/tasks` - Create new task
- `PUT /api/v1/tasks/{id}` - Update task
- `DELETE /api/v1/tasks/{id}` - Delete task
- `PATCH /api/v1/tasks/{id}/status` - Toggle task status

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 13
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios
- **Icons**: Heroicons

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.11+
- **Database**: PostgreSQL
- **ORM**: SQLModel
- **Auth**: Better Auth / python-jose
- **Migrations**: Alembic

### DevOps
- **Containerization**: Docker & Docker Compose
- **Deployment**: Vercel (frontend), Railway/Render (backend)
- **CI/CD**: GitHub Actions (optional)

## 📝 Development

### Running Tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm run lint
```

### Code Quality

```bash
# Backend lint
cd backend
flake8 src/

# Frontend lint
cd frontend
npm run lint
```

## 🤝 Contributing

This is a hackathon project for Phase 2. Contributions welcome!

## 📄 License

MIT License - see LICENSE file for details

## 🎉 Acknowledgments

Built for Hackathon Phase 2 🚀

---

**Happy Coding!** 💻✨
