import uuid
from datetime import datetime
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database import Base
from typing import Optional, List

class Role(Base):
    __tablename__ = "roles"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 关系
    users = relationship("User", back_populates="user_role", foreign_keys="User.role_id")
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")


# backend/app/models/system.py
class Menu(Base):
    __tablename__ = "menus"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    parent_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("menus.id"))
    sort: Mapped[int] = mapped_column(Integer, default=0)

    # ✅ 补充缺失字段
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(100), nullable=False)
    path: Mapped[str] = mapped_column(String(255), nullable=False)
    icon: Mapped[Optional[str]] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    permissions: Mapped[List["Permission"]] = relationship(
        "Permission",
        back_populates="menu",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    children: Mapped[List["Menu"]] = relationship(
        "Menu",
        back_populates="parent",
        cascade="all",
        lazy="selectin",
        passive_deletes=True
    )
    parent: Mapped[Optional["Menu"]] = relationship(
        "Menu",
        back_populates="children",
        remote_side=[id],
        lazy="selectin"
    )


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    menu_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("menus.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 关系
    menu = relationship("Menu", back_populates="permissions")
    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")


class RolePermission(Base):
    __tablename__ = "role_permissions"

    role_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("roles.id"), primary_key=True
    )
    permission_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("permissions.id"), primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )


class Dictionary(Base):
    __tablename__ = "dictionaries"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    type: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 关系
    items = relationship("DictionaryItem", back_populates="dictionary", cascade="all, delete-orphan")


class DictionaryItem(Base):
    __tablename__ = "dictionary_items"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    dictionary_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("dictionaries.id"), nullable=False
    )
    key: Mapped[str] = mapped_column(String(50), nullable=False)
    value: Mapped[str] = mapped_column(String(100), nullable=False)
    label: Mapped[str] = mapped_column(String(50), nullable=False)
    sort: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 关系
    dictionary = relationship("Dictionary", back_populates="items")

    # 复合唯一约束
    __table_args__ = (
        {'extend_existing': True},
    )