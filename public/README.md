# Power Of Holding - Premium Trading Learning Platform

A full-stack trading education platform with React frontend, FastAPI backend, and Supabase database.

## Tech Stack

### Frontend
- React 18
- Vite
- Tailwind CSS
- React Router
- Redux Toolkit
- Axios
- Framer Motion

### Backend
- Python 3.9+
- FastAPI
- Supabase PostgreSQL
- Supabase Storage

## Setup Instructions

### 1. Supabase Setup
1. Create a Supabase account at https://supabase.com
2. Create a new project
3. Run the SQL script in `backend/schema.sql` in the Supabase SQL Editor
4. Get your Project URL and Service Role Key from Project Settings → API

### 2. Backend Setup
1. Navigate to `backend` directory
2. Create a virtual environment (optional but recommended)
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and fill in your credentials
5. Run the server: `python main.py`

### 3. Frontend Setup
1. Navigate to `frontend` directory
2. Install dependencies: `npm install`
3. Run the dev server: `npm run dev`

## Features

- User Registration & Email Verification
- Admin Approval Workflow
- 6-Month Subscription Management
- One Device Login
- Secure Video Streaming with Watermarks
- Admin Dashboard & User Management
- OTP-based Password Reset

## Default Subscription Duration
6 Months from registration date
