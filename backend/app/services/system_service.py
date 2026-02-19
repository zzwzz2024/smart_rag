from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import joinedload
import uuid
from datetime import datetime

from backend.app.models import Role, Menu, Permission, RolePermission, Dictionary, DictionaryItem
from backend.app.schemas.system import (
    RoleCreate, RoleUpdate, MenuCreate, MenuUpdate, PermissionCreate, PermissionUpdate,
    RolePermissionCreate, DictionaryCreate, DictionaryUpdate, DictionaryItemCreate, DictionaryItemUpdate
)


class SystemService:
    """系统设置服务类"""

    # 1. 角色相关服务
    @staticmethod
    async def create_role(db: AsyncSession, role_data: RoleCreate) -> Role:
        """创建角色"""
        db_role = Role(
            id=str(uuid.uuid4()),
            name=role_data.name,
            code=role_data.code,
            description=role_data.description
        )
        db.add(db_role)
        await db.commit()
        await db.refresh(db_role)
        return db_role

    @staticmethod
    async def get_roles(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Role]:
        """获取角色列表"""
        result = await db.execute(
            select(Role).offset(skip).limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def get_role_by_id(db: AsyncSession, role_id: str) -> Optional[Role]:
        """根据ID获取角色"""
        result = await db.execute(
            select(Role).where(Role.id == role_id).options(joinedload(Role.permissions))
        )
        return result.scalars().first()

    @staticmethod
    async def update_role(db: AsyncSession, role_id: str, role_data: RoleUpdate) -> Optional[Role]:
        """更新角色"""
        db_role = await SystemService.get_role_by_id(db, role_id)
        if not db_role:
            return None
        
        update_data = role_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_role, field, value)
        
        db_role.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(db_role)
        return db_role

    @staticmethod
    async def delete_role(db: AsyncSession, role_id: str) -> bool:
        """删除角色"""
        db_role = await SystemService.get_role_by_id(db, role_id)
        if not db_role:
            return False
        
        await db.delete(db_role)
        await db.commit()
        return True

    @staticmethod
    async def assign_permissions_to_role(db: AsyncSession, role_permission_data: RolePermissionCreate) -> Optional[Role]:
        """为角色分配权限"""
        # 先删除角色现有的所有权限关联
        await db.execute(
            delete(RolePermission).where(RolePermission.role_id == role_permission_data.role_id)
        )
        
        # 对权限ID列表进行去重处理
        unique_permission_ids = list(set(role_permission_data.permission_ids))
        
        # 添加新的权限关联
        for permission_id in unique_permission_ids:
            role_permission = RolePermission(
                role_id=role_permission_data.role_id,
                permission_id=permission_id
            )
            db.add(role_permission)
        
        await db.commit()
        
        # 返回更新后的角色
        return await SystemService.get_role_by_id(db, role_permission_data.role_id)

    # 2. 菜单相关服务
    @staticmethod
    async def create_menu(db: AsyncSession, menu_data: MenuCreate) -> Menu:
        """创建菜单"""
        db_menu = Menu(
            id=str(uuid.uuid4()),
            name=menu_data.name,
            code=menu_data.code,
            path=menu_data.path,
            icon=menu_data.icon,
            parent_id=menu_data.parent_id,
            sort=menu_data.sort,
            is_active=menu_data.is_active
        )
        db.add(db_menu)
        await db.commit()
        await db.refresh(db_menu)
        return db_menu

    @staticmethod
    async def get_menus(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Menu]:
        """获取菜单列表"""
        result = await db.execute(
            select(Menu).offset(skip).limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def get_menu_by_id(db: AsyncSession, menu_id: str) -> Optional[Menu]:
        """根据ID获取菜单"""
        result = await db.execute(
            select(Menu).where(Menu.id == menu_id)
        )
        return result.scalars().first()

    @staticmethod
    async def update_menu(db: AsyncSession, menu_id: str, menu_data: MenuUpdate) -> Optional[Menu]:
        """更新菜单"""
        db_menu = await SystemService.get_menu_by_id(db, menu_id)
        if not db_menu:
            return None
        
        update_data = menu_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_menu, field, value)
        
        db_menu.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(db_menu)
        return db_menu

    @staticmethod
    async def delete_menu(db: AsyncSession, menu_id: str) -> bool:
        """删除菜单"""
        db_menu = await SystemService.get_menu_by_id(db, menu_id)
        if not db_menu:
            return False
        
        await db.delete(db_menu)
        await db.commit()
        return True

    @staticmethod
    async def get_menu_tree(db: AsyncSession) -> List[dict]:
        """获取菜单树结构（修复重复问题）"""
        # 1. 先获取所有菜单
        result = await db.execute(
            select(Menu)
            .order_by(Menu.sort)
        )
        all_menus = result.scalars().all()
        
        # 2. 将菜单转换为字典格式，方便构建树
        menu_dict = {}
        root_menus = []
        
        for menu in all_menus:
            menu_data = {
                "id": menu.id,
                "name": menu.name,
                "code": menu.code,
                "path": menu.path,
                "icon": menu.icon,
                "parent_id": menu.parent_id,
                "sort": menu.sort,
                "is_active": menu.is_active,
                "created_at": menu.created_at,
                "updated_at": menu.updated_at,
                "children": []
            }
            menu_dict[menu.id] = menu_data
            
            if menu.parent_id is None:
                root_menus.append(menu_data)
        
        # 3. 构建菜单树
        for menu_id, menu_data in menu_dict.items():
            if menu_data["parent_id"]:
                parent = menu_dict.get(menu_data["parent_id"])
                if parent:
                    parent["children"].append(menu_data)
        
        return root_menus

    # 3. 权限相关服务
    @staticmethod
    async def create_permission(db: AsyncSession, permission_data: PermissionCreate) -> Permission:
        """创建权限"""
        db_permission = Permission(
            id=str(uuid.uuid4()),
            name=permission_data.name,
            code=permission_data.code,
            description=permission_data.description,
            menu_id=permission_data.menu_id
        )
        db.add(db_permission)
        await db.commit()
        await db.refresh(db_permission)
        return db_permission

    @staticmethod
    async def get_permissions(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Permission]:
        """获取权限列表"""
        result = await db.execute(
            select(Permission).offset(skip).limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def get_permission_by_id(db: AsyncSession, permission_id: str) -> Optional[Permission]:
        """根据ID获取权限"""
        result = await db.execute(
            select(Permission).where(Permission.id == permission_id)
        )
        return result.scalars().first()

    @staticmethod
    async def update_permission(db: AsyncSession, permission_id: str, permission_data: PermissionUpdate) -> Optional[Permission]:
        """更新权限"""
        db_permission = await SystemService.get_permission_by_id(db, permission_id)
        if not db_permission:
            return None
        
        update_data = permission_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_permission, field, value)
        
        db_permission.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(db_permission)
        return db_permission

    @staticmethod
    async def delete_permission(db: AsyncSession, permission_id: str) -> bool:
        """删除权限"""
        db_permission = await SystemService.get_permission_by_id(db, permission_id)
        if not db_permission:
            return False
        
        await db.delete(db_permission)
        await db.commit()
        return True

    # 4. 字典相关服务
    @staticmethod
    async def create_dictionary(db: AsyncSession, dictionary_data: DictionaryCreate) -> Dictionary:
        """创建字典"""
        db_dictionary = Dictionary(
            id=str(uuid.uuid4()),
            name=dictionary_data.name,
            type=dictionary_data.type,
            description=dictionary_data.description
        )
        db.add(db_dictionary)
        await db.commit()
        await db.refresh(db_dictionary)
        return db_dictionary

    @staticmethod
    async def get_dictionaries(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Dictionary]:
        """获取字典列表"""
        result = await db.execute(
            select(Dictionary).offset(skip).limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def get_dictionary_by_id(db: AsyncSession, dictionary_id: str) -> Optional[Dictionary]:
        """根据ID获取字典"""
        result = await db.execute(
            select(Dictionary).where(Dictionary.id == dictionary_id).options(joinedload(Dictionary.items))
        )
        return result.scalars().first()

    @staticmethod
    async def get_dictionary_by_type(db: AsyncSession, dictionary_type: str) -> Optional[Dictionary]:
        """根据类型获取字典"""
        result = await db.execute(
            select(Dictionary).where(Dictionary.type == dictionary_type).options(joinedload(Dictionary.items))
        )
        return result.scalars().first()

    @staticmethod
    async def update_dictionary(db: AsyncSession, dictionary_id: str, dictionary_data: DictionaryUpdate) -> Optional[Dictionary]:
        """更新字典"""
        db_dictionary = await SystemService.get_dictionary_by_id(db, dictionary_id)
        if not db_dictionary:
            return None
        
        update_data = dictionary_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_dictionary, field, value)
        
        db_dictionary.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(db_dictionary)
        return db_dictionary

    @staticmethod
    async def delete_dictionary(db: AsyncSession, dictionary_id: str) -> bool:
        """删除字典"""
        db_dictionary = await SystemService.get_dictionary_by_id(db, dictionary_id)
        if not db_dictionary:
            return False
        
        await db.delete(db_dictionary)
        await db.commit()
        return True

    # 5. 字典项相关服务
    @staticmethod
    async def create_dictionary_item(db: AsyncSession, item_data: DictionaryItemCreate) -> DictionaryItem:
        """创建字典项"""
        db_item = DictionaryItem(
            id=str(uuid.uuid4()),
            dictionary_id=item_data.dictionary_id,
            key=item_data.key,
            value=item_data.value,
            label=item_data.label,
            sort=item_data.sort,
            is_active=item_data.is_active
        )
        db.add(db_item)
        await db.commit()
        await db.refresh(db_item)
        return db_item

    @staticmethod
    async def get_dictionary_items(db: AsyncSession, dictionary_id: str) -> List[DictionaryItem]:
        """获取字典项列表"""
        result = await db.execute(
            select(DictionaryItem).where(DictionaryItem.dictionary_id == dictionary_id).order_by(DictionaryItem.sort)
        )
        return result.scalars().all()

    @staticmethod
    async def get_dictionary_item_by_id(db: AsyncSession, item_id: str) -> Optional[DictionaryItem]:
        """根据ID获取字典项"""
        result = await db.execute(
            select(DictionaryItem).where(DictionaryItem.id == item_id)
        )
        return result.scalars().first()

    @staticmethod
    async def update_dictionary_item(db: AsyncSession, item_id: str, item_data: DictionaryItemUpdate) -> Optional[DictionaryItem]:
        """更新字典项"""
        db_item = await SystemService.get_dictionary_item_by_id(db, item_id)
        if not db_item:
            return None
        
        update_data = item_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_item, field, value)
        
        db_item.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(db_item)
        return db_item

    @staticmethod
    async def delete_dictionary_item(db: AsyncSession, item_id: str) -> bool:
        """删除字典项"""
        db_item = await SystemService.get_dictionary_item_by_id(db, item_id)
        if not db_item:
            return False
        
        await db.delete(db_item)
        await db.commit()
        return True
