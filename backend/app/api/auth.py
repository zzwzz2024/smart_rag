"""
认证 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from backend.app.utils.auth import hash_password, verify_password, create_access_token
from backend.app.models.response_model import Response

router = APIRouter()


@router.post("/register", response_model=Response)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    """用户注册"""
    # 检查用户名
    existing = await db.execute(
        select(User).where(User.username == data.username)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(400, "用户名已存在")

    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
        # hashed_password=data.password,
        is_active=True
    )
    db.add(user)
    await db.flush()

    token = create_access_token({"sub": user.id})
    return Response(
        data=Token(
            access_token=token,
            user=UserResponse.model_validate(user),
        )
    )


@router.post("/login", response_model=Response)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    """用户登录"""
    result = await db.execute(
        select(User).where(User.username == data.username)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(401, "用户名或密码错误")

    token = create_access_token({"sub": user.id})
    return Response(
        data=Token(
            access_token=token,
            user=UserResponse.model_validate(user),
        )
    )


@router.get("/me", response_model=Response)
async def get_me(
    current_user: User = Depends(
        __import__("backend.app.utils.auth", fromlist=["get_current_user"]).get_current_user
    ),
):
    """获取当前用户信息"""
    # return UserResponse.model_validate(current_user)
    return Response(
        data=UserResponse.model_validate(current_user)  # 直接传入 UserResponse 对象
    )