# Step-by-Step Hosting Guide

This guide will walk you through deploying your Power Of Holding platform to production.

## Table of Contents
1. [Database Setup: Supabase](#1-database-setup-supabase)
2. [Backend Hosting: Google Cloud Run](#2-backend-hosting-google-cloud-run)
3. [Frontend Hosting: Firebase Hosting](#3-frontend-hosting-firebase-hosting)
4. [Domain Setup (Optional)](#4-domain-setup-optional)
5. [Final Checks](#5-final-checks)

---

## 1. Database Setup: Supabase

### Step 1.1: Create Supabase Project
1. Go to [https://supabase.com/dashboard](https://supabase.com/dashboard)
2. Click "New Project"
3. Fill in project details:
   - Name: `power-of-holding`
   - Database Password: (Save this in a secure place!)
   - Region: Choose the region closest to your users
4. Click "Create new project" (this may take a few minutes)

### Step 1.2: Run Database Schema
1. In your Supabase dashboard, go to **SQL Editor** → **New query**
2. Copy all content from `backend/schema.sql` and paste it into the editor
3. Click "Run"
4. Verify tables were created by going to **Table Editor**

### Step 1.3: Get Supabase Credentials
1. Go to **Project Settings** → **API**
2. Save these values:
   - Project URL (e.g., `https://xxxxxx.supabase.co`)
   - service_role secret (under "Project API keys")

---

## 2. Backend Hosting: Google Cloud Run

### Step 2.1: Prepare Backend Files
Create a `Dockerfile` in the `backend/` directory:

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create a `.dockerignore` file:
```
__pycache__
venv
.env
*.pyc
```

### Step 2.2: Set Up Google Cloud
1. Go to [https://console.cloud.google.com/](https://console.cloud.google.com/)
2. Create a new project
3. Enable the following APIs:
   - Cloud Run API
   - Cloud Build API
   - Container Registry API
4. Install [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)

### Step 2.3: Deploy Backend
Open a terminal and run:
```powershell
# Authenticate
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Deploy to Cloud Run
cd backend
gcloud run deploy power-of-holding-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "SUPABASE_URL=YOUR_SUPABASE_URL,SUPABASE_KEY=YOUR_SERVICE_ROLE_KEY,SECRET_KEY=YOUR_SECRET_KEY"
```

After deployment, save the Cloud Run URL (e.g., `https://power-of-holding-backend-xxxxx.a.run.app`)

---

## 3. Frontend Hosting: Firebase Hosting

### Step 3.1: Update Frontend API URL
Edit `frontend/src/services/api.js`:
```javascript
const api = axios.create({
  baseURL: 'YOUR_CLOUD_RUN_URL/api',  // Replace with your Cloud Run URL
  headers: {
    'Content-Type': 'application/json'
  }
})
```

### Step 3.2: Install Firebase CLI
```powershell
npm install -g firebase-tools
```

### Step 3.3: Initialize Firebase
```powershell
cd frontend
firebase login
firebase init
```
Select:
- ❯ **Hosting: Configure files for Firebase Hosting and (optionally) set up GitHub Action deploys**
- Use an existing project or create a new one
- What do you want to use as your public directory? `dist`
- Configure as a single-page app? **Yes**
- Set up automatic builds and deploys with GitHub? **No**

### Step 3.4: Build Frontend
```powershell
npm install
npm run build
```

### Step 3.5: Deploy Frontend
```powershell
firebase deploy
```
Save the Firebase Hosting URL (e.g., `https://your-project-id.web.app`)

---

## 4. Domain Setup (Optional)

### Custom Domain for Frontend (Firebase)
1. Go to Firebase Console → Hosting
2. Click "Add custom domain"
3. Follow the instructions to verify ownership and update DNS records

### Custom Domain for Backend (Cloud Run)
1. Go to Google Cloud Console → Cloud Run
2. Select your service → "Manage custom domains"
3. Follow the instructions to map a custom domain

---

## 5. Final Checks

1. **Test Registration**: Create a test account
2. **Test Email Verification**: Check if emails send (you may need to set up SendGrid or another email service in production)
3. **Test Login**: Verify login flow works
4. **Test Video Portal**: Ensure videos load
5. **Test Admin Dashboard**: Verify admin functions (approve/reject users)

---

## Production Enhancements
- Add proper email service (SendGrid, Mailgun) for verification emails and OTP
- Set up environment variables for all services
- Add monitoring and logging
- Enable HTTPS everywhere (Firebase and Cloud Run do this automatically)
- Set up backup for Supabase database
