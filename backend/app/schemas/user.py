from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱")
    password: str = Field(..., description="密码")
    role_id: Optional[str] = Field(None, description="角色ID")
    is_active: Optional[bool] = Field(True, description="是否激活")


class UserLogin(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, description="用户名")
    email: Optional[str] = Field(None, description="邮箱")
    password: Optional[str] = Field(None, description="密码")
    role: Optional[str] = Field(None, description="角色")
    is_active: Optional[bool] = Field(None, description="是否激活")


class UserResponse(BaseModel):
    id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱")
    role: str = Field(..., description="角色")
    role_id: Optional[str] = Field(None, description="角色ID")
    is_active: bool = Field(..., description="是否激活")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field("bearer", description="令牌类型")
    user: UserResponse = Field(..., description="用户信息")