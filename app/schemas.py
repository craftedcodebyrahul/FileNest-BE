from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone_number: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    user_id: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: str
    session_id: str
    
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    
class UserProfile(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    email: EmailStr

class UpdatePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
    

 