from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.models import User
from backend.app.schemas import (
    UserCreate, UserResponse, UserUpdate, UserRoleUpdate,
    RoleCreate, RoleUpdate, RoleResponse, RoleWithPermissions,
    MenuCreate, MenuUpdate, MenuResponse, MenuWithChildren,
    PermissionCreate, PermissionUpdate, PermissionResponse,
    RolePermissionCreate,
    DictionaryCreate, DictionaryUpdate, DictionaryResponse, DictionaryWithItems,
    DictionaryItemCreate, DictionaryItemUpdate, DictionaryItemResponse,
    SuccessResponse
)
from backend.app.models.response_model import Response
from backend.app.services import SystemService
from backend.app.utils.auth import get_current_user, get_current_active_user

router = APIRouter(prefix="/system", tags=["system"])


# 1. 用户管理API
@router.get("/users", response_model=Response)
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取用户列表"""
    from backend.app.services import user_service
    users = await user_service.get_users(db, skip=skip, limit=limit)
    return Response(data=[UserResponse.model_validate(user) for user in users])


@router.get("/users/{user_id}", response_model=Response)
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """根据ID获取用户"""
    from backend.app.services import user_service
    user = await user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return Response(data=UserResponse.model_validate(user))


@router.put("/users/{user_id}", response_model=Response)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """更新用户信息"""
    from backend.app.services import user_service
    updated_user = await user_service.update_user(db, user_id, user_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return Response(data=UserResponse.model_validate(updated_user))


@router.put("/users/{user_id}/role", response_model=Response)
async def update_user_role(
    user_id: str,
    role_data: UserRoleUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """更新用户角色"""
    from backend.app.services import user_service
    updated_user = await user_service.update_user_role(db, user_id, role_data.role_id)
    if not updated_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return Response(data=UserResponse.model_validate(updated_user))


@router.delete("/users/{user_id}", response_model=Response)
async def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """删除用户"""
    from backend.app.services import user_service
    deleted = await user_service.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="用户不存在")
    return Response(data={"message": "用户删除成功"})


@router.post("/users", response_model=Response)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """创建用户"""
    from backend.app.services import user_service
    user = await user_service.create_user(db, user_data)
    return Response(data=UserResponse.model_validate(user))


# 2. 角色管理API
@router.post("/roles", response_model=Response)
async def create_role(
    role_data: RoleCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """创建角色"""
    role = await SystemService.create_role(db, role_data)
    return Response(data=RoleResponse.model_validate(role))


@router.get("/roles", response_model=Response)
async def get_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取角色列表"""
    roles = await SystemService.get_roles(db, skip=skip, limit=limit)
    return Response(data=[RoleResponse.model_validate(role) for role in roles])


@router.get("/roles/{role_id}", response_model=Response)
async def get_role(
    role_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """根据ID获取角色"""
    role = await SystemService.get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    return Response(data=RoleWithPermissions.model_validate(role))


@router.put("/roles/{role_id}", response_model=Response)
async def update_role(
    role_id: str,
    role_data: RoleUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """更新角色"""
    updated_role = await SystemService.update_role(db, role_id, role_data)
    if not updated_role:
        raise HTTPException(status_code=404, detail="角色不存在")
    return Response(data=RoleResponse.model_validate(updated_role))


@router.delete("/roles/{role_id}", response_model=Response)
async def delete_role(
    role_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """删除角色"""
    deleted = await SystemService.delete_role(db, role_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="角色不存在")
    return Response(data={"message": "角色删除成功"})


@router.post("/roles/{role_id}/permissions", response_model=Response)
async def assign_permissions(
    role_id: str,
    permission_data: RolePermissionCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """为角色分配权限"""
    # 确保role_id与请求体中的role_id一致
    if permission_data.role_id != role_id:
        raise HTTPException(status_code=400, detail="角色ID不一致")
    
    updated_role = await SystemService.assign_permissions_to_role(db, permission_data)
    if not updated_role:
        raise HTTPException(status_code=404, detail="角色不存在")
    return Response(data=RoleWithPermissions.model_validate(updated_role))


# 3. 菜单管理API
@router.post("/menus", response_model=Response)
async def create_menu(
    menu_data: MenuCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """创建菜单"""
    menu = await SystemService.create_menu(db, menu_data)
    return Response(data=MenuResponse.model_validate(menu))


@router.get("/menus", response_model=Response)
async def get_menus(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取菜单列表"""
    menus = await SystemService.get_menus(db, skip=skip, limit=limit)
    return Response(data=[MenuResponse.model_validate(menu) for menu in menus])


@router.get("/menus/tree", response_model=Response)
async def get_menu_tree(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取菜单树结构"""
    menu_tree = await SystemService.get_menu_tree(db)
    return Response(data=[MenuWithChildren.model_validate(menu) for menu in menu_tree])


@router.get("/menus/{menu_id}", response_model=Response)
async def get_menu(
    menu_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """根据ID获取菜单"""
    menu = await SystemService.get_menu_by_id(db, menu_id)
    if not menu:
        raise HTTPException(status_code=404, detail="菜单不存在")
    return Response(data=MenuResponse.model_validate(menu))


@router.put("/menus/{menu_id}", response_model=Response)
async def update_menu(
    menu_id: str,
    menu_data: MenuUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """更新菜单"""
    updated_menu = await SystemService.update_menu(db, menu_id, menu_data)
    if not updated_menu:
        raise HTTPException(status_code=404, detail="菜单不存在")
    return Response(data=MenuResponse.model_validate(updated_menu))


@router.delete("/menus/{menu_id}", response_model=Response)
async def delete_menu(
    menu_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """删除菜单"""
    deleted = await SystemService.delete_menu(db, menu_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="菜单不存在")
    return Response(data={"message": "菜单删除成功"})


# 4. 权限管理API
@router.post("/permissions", response_model=Response)
async def create_permission(
    permission_data: PermissionCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """创建权限"""
    permission = await SystemService.create_permission(db, permission_data)
    return Response(data=PermissionResponse.model_validate(permission))


@router.get("/permissions", response_model=Response)
async def get_permissions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取权限列表"""
    permissions = await SystemService.get_permissions(db, skip=skip, limit=limit)
    return Response(data=[PermissionResponse.model_validate(permission) for permission in permissions])


@router.get("/permissions/{permission_id}", response_model=Response)
async def get_permission(
    permission_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """根据ID获取权限"""
    permission = await SystemService.get_permission_by_id(db, permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="权限不存在")
    return Response(data=PermissionResponse.model_validate(permission))


@router.put("/permissions/{permission_id}", response_model=Response)
async def update_permission(
    permission_id: str,
    permission_data: PermissionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """更新权限"""
    updated_permission = await SystemService.update_permission(db, permission_id, permission_data)
    if not updated_permission:
        raise HTTPException(status_code=404, detail="权限不存在")
    return Response(data=PermissionResponse.model_validate(updated_permission))


@router.delete("/permissions/{permission_id}", response_model=Response)
async def delete_permission(
    permission_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """删除权限"""
    deleted = await SystemService.delete_permission(db, permission_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="权限不存在")
    return Response(data={"message": "权限删除成功"})


# 5. 字典管理API
@router.post("/dictionaries", response_model=Response)
async def create_dictionary(
    dictionary_data: DictionaryCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """创建字典"""
    dictionary = await SystemService.create_dictionary(db, dictionary_data)
    return Response(data=DictionaryResponse.model_validate(dictionary))


@router.get("/dictionaries", response_model=Response)
async def get_dictionaries(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取字典列表"""
    dictionaries = await SystemService.get_dictionaries(db, skip=skip, limit=limit)
    return Response(data=[DictionaryResponse.model_validate(dictionary) for dictionary in dictionaries])


@router.get("/dictionaries/{dictionary_id}", response_model=Response)
async def get_dictionary(
    dictionary_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """根据ID获取字典"""
    dictionary = await SystemService.get_dictionary_by_id(db, dictionary_id)
    if not dictionary:
        raise HTTPException(status_code=404, detail="字典不存在")
    return Response(data=DictionaryWithItems.model_validate(dictionary))


@router.get("/dictionaries/type/{dictionary_type}", response_model=Response)
async def get_dictionary_by_type(
    dictionary_type: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """根据类型获取字典"""
    dictionary = await SystemService.get_dictionary_by_type(db, dictionary_type)
    if not dictionary:
        raise HTTPException(status_code=404, detail="字典不存在")
    return Response(data=DictionaryWithItems.model_validate(dictionary))


@router.put("/dictionaries/{dictionary_id}", response_model=Response)
async def update_dictionary(
    dictionary_id: str,
    dictionary_data: DictionaryUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """更新字典"""
    updated_dictionary = await SystemService.update_dictionary(db, dictionary_id, dictionary_data)
    if not updated_dictionary:
        raise HTTPException(status_code=404, detail="字典不存在")
    return Response(data=DictionaryResponse.model_validate(updated_dictionary))


@router.delete("/dictionaries/{dictionary_id}", response_model=Response)
async def delete_dictionary(
    dictionary_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """删除字典"""
    deleted = await SystemService.delete_dictionary(db, dictionary_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="字典不存在")
    return Response(data={"message": "字典删除成功"})


# 6. 字典项管理API
@router.post("/dictionary-items", response_model=Response)
async def create_dictionary_item(
    item_data: DictionaryItemCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """创建字典项"""
    item = await SystemService.create_dictionary_item(db, item_data)
    return Response(data=DictionaryItemResponse.model_validate(item))


@router.get("/dictionaries/{dictionary_id}/items", response_model=Response)
async def get_dictionary_items(
    dictionary_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取字典项列表"""
    items = await SystemService.get_dictionary_items(db, dictionary_id)
    return Response(data=[DictionaryItemResponse.model_validate(item) for item in items])


@router.put("/dictionary-items/{item_id}", response_model=Response)
async def update_dictionary_item(
    item_id: str,
    item_data: DictionaryItemUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """更新字典项"""
    updated_item = await SystemService.update_dictionary_item(db, item_id, item_data)
    if not updated_item:
        raise HTTPException(status_code=404, detail="字典项不存在")
    return Response(data=DictionaryItemResponse.model_validate(updated_item))


@router.delete("/dictionary-items/{item_id}", response_model=Response)
async def delete_dictionary_item(
    item_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """删除字典项"""
    deleted = await SystemService.delete_dictionary_item(db, item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="字典项不存在")
    return Response(data={"message": "字典项删除成功"})


# 7. 用户菜单权限API
@router.get("/user/menus", response_model=Response)
async def get_user_menus(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户的菜单权限"""
    menus = await SystemService.get_user_menu_permissions(db, current_user.id)
    return Response(data=menus)
