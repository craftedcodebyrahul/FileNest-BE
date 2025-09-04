from datetime import datetime, timedelta
import json
from fastapi import HTTPException
import jwt
from supabase import create_client
from ..config import get_settings
from ..schemas import ForgotPasswordRequest, ResetPasswordRequest, TokenData, UpdatePasswordRequest, UserCreate, Token, UserProfile

settings = get_settings()
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def create_access_token(user_id: str, session_id: str):
    expires_delta = timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)
    expire = datetime.utcnow() + expires_delta
    payload = {
        "sub": user_id,
        "session_id": session_id,
        "exp": expire
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.ALGORITHM)

def signup_user(user: UserCreate):
    auth_response = supabase.auth.sign_up({
        "email": user.email,
        "password": user.password
    })
    
    user_id = auth_response.user.id
    
 
    supabase.table("profiles").insert({
        "user_id": user_id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone_number": user.phone_number
    }).execute()
    
    return user_id

def login_user(email: str, password: str):
    response = supabase.auth.sign_in_with_password({
        "email": email,
        "password": password
    })
    print(json.dumps(response.json()))
    return Token(
        access_token=create_access_token(
            user_id=response.user.id,
            session_id=response.session.access_token
        ),
        token_type="bearer"
    )

def logout_user(token: TokenData):
    supabase.auth.sign_out()

# 👤 Get Profile
def get_user_profile(user: TokenData) -> dict:
    # Step 1: Fetch profile from 'profiles' table
    profile_result = supabase.table("profiles") \
        .select("*") \
        .eq("user_id", user.user_id) \
        .single() \
        .execute()
    
    if not profile_result.data:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile_data = profile_result.data

    # Step 2: Fetch user from Supabase Auth to get email
    auth_user = supabase.auth.get_user(user.session_id)

    if not auth_user.user:
        raise HTTPException(status_code=404, detail="User email not found")

    profile_data["email"] = auth_user.user.email

    return profile_data


# ✏️ Update Profile
def update_user_profile(user: TokenData, updated_data: UserProfile):
    supabase.table("profiles").update(updated_data.dict()).eq("user_id", user.user_id).execute()
    return {"message": "Profile updated successfully"}


# 🔒 Change Password
def change_user_password(user: TokenData, data: UpdatePasswordRequest):
    try:
        # Optional: Validate old password if needed
        supabase.auth.sign_in_with_password({
            "email": user.email,
            "password": data.old_password
        })
        supabase.auth.update_user({"password": data.new_password})
        return {"message": "Password updated successfully"}
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid current password")


# 📧 Forgot Password
def send_reset_email(data: ForgotPasswordRequest):
    try:
        supabase.auth.reset_password_email(data.email)
        return {"message": "Password reset email sent"}
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to send reset email")


# 🔁 Reset Password with Token
def reset_user_password(data: ResetPasswordRequest):
    try:
        supabase.auth.update_user(
            {"password": data.new_password},
            session_token=data.token
        )
        return {"message": "Password reset successful"}
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to reset password")