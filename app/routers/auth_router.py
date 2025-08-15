from fastapi import APIRouter, Depends, HTTPException
from ..schemas import (
    LoginRequest, UserCreate, Token, UserProfile,
    UpdatePasswordRequest, ForgotPasswordRequest, ResetPasswordRequest
)
from ..dependencies import get_current_user, oauth2_scheme
from ..services.auth_service import (
    signup_user, login_user, logout_user,
    get_user_profile, update_user_profile,
    change_user_password, send_reset_email,
    reset_user_password
)

from ..schemas import TokenData

router = APIRouter()

# ✅ Signup
@router.post("/signup", response_model=dict)
async def signup(user: UserCreate):
    try:
        user_id = signup_user(user)
        return {"message": "User created successfully", "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ✅ Login
@router.post("/login", response_model=Token)
async def login(request: LoginRequest):
    try:
        return login_user(request.email, request.password)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid credentials")

# ✅ Logout
@router.post("/logout")
async def logout(token: TokenData = Depends(get_current_user)):
    try:
        logout_user()
        return {"message": "Logged out successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ✅ Get Profile
@router.get("/get_profile", response_model=UserProfile)
async def get_profile(user: TokenData = Depends(get_current_user)):
    try:
        data=get_user_profile(user)
 
        return UserProfile(**data)
        
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

# ✅ Update Profile
@router.put("/update_profile")
async def update_profile(data: UserProfile, user: TokenData = Depends(get_current_user)):
    try:
        return update_user_profile(user, data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ✅ Change Password
@router.post("/change_password")
async def change_password(data: UpdatePasswordRequest, user: TokenData = Depends(get_current_user)):
    try:
        return change_user_password(user, data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ✅ Forgot Password
@router.post("/forgot_password")
async def forgot_password(data: ForgotPasswordRequest):
    try:
        return send_reset_email(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ✅ Reset Password
@router.post("/reset_password")
async def reset_password(data: ResetPasswordRequest):
    try:
        return reset_user_password(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
