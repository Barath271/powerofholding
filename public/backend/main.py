from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from supabase import create_client, Client
from typing import Optional, List
import random
import string

load_dotenv()

app = FastAPI(title="Power Of Holding API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRegister(BaseModel):
    full_name: str
    email: EmailStr
    mobile_number: str
    password: str
    confirm_password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class VerifyEmail(BaseModel):
    token: str


class ForgotPassword(BaseModel):
    email: EmailStr


class VerifyOTP(BaseModel):
    email: EmailStr
    otp: str


class ResetPassword(BaseModel):
    email: EmailStr
    otp: str
    new_password: str
    confirm_password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def generate_verification_token(length=32):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))


async def get_current_user(request: Request):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise credentials_exception
        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    response = supabase.table("users").select("*").eq("email", token_data.email).single().execute()
    user = response.data
    if user is None:
        raise credentials_exception
    return user


@app.get("/")
def read_root():
    return {"message": "Power Of Holding API"}


@app.post("/api/auth/register")
async def register(user: UserRegister):
    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    existing_user = supabase.table("users").select("*").eq("email", user.email).execute()
    if existing_user.data:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    verification_token = generate_verification_token()
    expires_at = (datetime.utcnow() + timedelta(hours=24)).isoformat()
    
    new_user = {
        "full_name": user.full_name,
        "email": user.email,
        "mobile_number": user.mobile_number,
        "password_hash": hashed_password,
        "email_verified": False,
        "admin_approved": False,
        "status": "pending_approval",
        "subscription_end": (datetime.utcnow() + timedelta(days=180)).isoformat()
    }
    
    user_response = supabase.table("users").insert(new_user).execute()
    user_id = user_response.data[0]["id"]
    
    supabase.table("email_verification_tokens").insert({
        "user_id": user_id,
        "token": verification_token,
        "expires_at": expires_at
    }).execute()
    
    return {"message": "Registration successful. Please verify your email address. After email verification, your account will be reviewed by the administrator."}


@app.post("/api/auth/verify-email")
async def verify_email(data: VerifyEmail):
    token_response = supabase.table("email_verification_tokens").select("*").eq("token", data.token).single().execute()
    token = token_response.data
    
    if not token:
        raise HTTPException(status_code=400, detail="Invalid verification token")
    
    if datetime.fromisoformat(token["expires_at"]) < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Verification token expired")
    
    user_response = supabase.table("users").update({"email_verified": True}).eq("id", token["user_id"]).execute()
    supabase.table("email_verification_tokens").delete().eq("token", data.token).execute()
    
    return {"message": "Email verified successfully. Please wait for administrator approval."}


@app.post("/api/auth/login")
async def login(user: UserLogin):
    user_response = supabase.table("users").select("*").eq("email", user.email).single().execute()
    db_user = user_response.data
    
    if not db_user or not verify_password(user.password, db_user["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    if not db_user["email_verified"]:
        raise HTTPException(status_code=403, detail="Please verify your email before logging in")
    
    if not db_user["admin_approved"]:
        raise HTTPException(status_code=403, detail="Your account is awaiting administrator approval")
    
    if db_user["status"] == "suspended":
        raise HTTPException(status_code=403, detail="Your account has been suspended")
    
    if datetime.fromisoformat(db_user["subscription_end"]) < datetime.utcnow():
        raise HTTPException(status_code=403, detail="Your subscription has expired. Please contact the administrator")
    
    access_token = create_access_token(data={"sub": db_user["email"]})
    refresh_token = create_refresh_token(data={"sub": db_user["email"]})
    
    existing_session = supabase.table("login_sessions").select("*").eq("user_id", db_user["id"]).execute()
    if existing_session.data:
        supabase.table("login_sessions").delete().eq("user_id", db_user["id"]).execute()
    
    supabase.table("login_sessions").insert({
        "user_id": db_user["id"],
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at": (datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).isoformat()
    }).execute()
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer", "user": db_user}


@app.post("/api/auth/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    supabase.table("login_sessions").delete().eq("user_id", current_user["id"]).execute()
    return {"message": "Logged out successfully"}


@app.post("/api/auth/forgot-password")
async def forgot_password(data: ForgotPassword):
    user_response = supabase.table("users").select("*").eq("email", data.email).single().execute()
    user = user_response.data
    
    if not user:
        return {"message": "If this email is registered, you will receive an OTP"}
    
    otp = generate_otp()
    otp_expires = (datetime.utcnow() + timedelta(minutes=10)).isoformat()
    
    supabase.table("otp_codes").insert({
        "user_id": user["id"],
        "otp": otp,
        "expires_at": otp_expires,
        "attempts": 0
    }).execute()
    
    return {"message": "OTP sent to your email", "otp": otp}


@app.post("/api/auth/verify-otp")
async def verify_otp(data: VerifyOTP):
    user_response = supabase.table("users").select("*").eq("email", data.email).single().execute()
    user = user_response.data
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid request")
    
    otp_response = supabase.table("otp_codes").select("*").eq("user_id", user["id"]).order("created_at", desc=True).limit(1).single().execute()
    otp_record = otp_response.data
    
    if not otp_record:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    if otp_record["attempts"] >= 5:
        raise HTTPException(status_code=400, detail="Too many attempts. Please request a new OTP")
    
    if otp_record["otp"] != data.otp:
        supabase.table("otp_codes").update({"attempts": otp_record["attempts"] + 1}).eq("id", otp_record["id"]).execute()
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    if datetime.fromisoformat(otp_record["expires_at"]) < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP expired")
    
    return {"message": "OTP verified successfully"}


@app.post("/api/auth/reset-password")
async def reset_password(data: ResetPassword):
    if data.new_password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    user_response = supabase.table("users").select("*").eq("email", data.email).single().execute()
    user = user_response.data
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid request")
    
    otp_response = supabase.table("otp_codes").select("*").eq("user_id", user["id"]).order("created_at", desc=True).limit(1).single().execute()
    otp_record = otp_response.data
    
    if not otp_record or otp_record["otp"] != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    if datetime.fromisoformat(otp_record["expires_at"]) < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP expired")
    
    hashed_password = get_password_hash(data.new_password)
    supabase.table("users").update({"password_hash": hashed_password}).eq("id", user["id"]).execute()
    supabase.table("otp_codes").delete().eq("user_id", user["id"]).execute()
    
    return {"message": "Password reset successful. Please log in with your new password"}


@app.get("/api/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user


@app.get("/api/admin/users")
async def get_all_users(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    users_response = supabase.table("users").select("*").execute()
    return users_response.data


@app.post("/api/admin/users/{user_id}/approve")
async def approve_user(user_id: str, current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    supabase.table("users").update({"admin_approved": True, "status": "active"}).eq("id", user_id).execute()
    return {"message": "User approved successfully"}


@app.post("/api/admin/users/{user_id}/reject")
async def reject_user(user_id: str, current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    supabase.table("users").delete().eq("id", user_id).execute()
    return {"message": "User rejected and deleted"}


@app.get("/api/videos")
async def get_videos(current_user: dict = Depends(get_current_user)):
    videos_response = supabase.table("videos").select("*, video_categories(*)").execute()
    return videos_response.data


@app.get("/api/admin/dashboard")
async def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    total_users = len(supabase.table("users").select("*").execute().data)
    approved_users = len(supabase.table("users").select("*").eq("admin_approved", True).execute().data)
    pending_users = len(supabase.table("users").select("*").eq("admin_approved", False).eq("email_verified", True).execute().data)
    total_videos = len(supabase.table("videos").select("*").execute().data)
    
    return {
        "total_users": total_users,
        "approved_users": approved_users,
        "pending_users": pending_users,
        "total_videos": total_videos
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
