from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List, Optional


# 基础Schema
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# 1. 角色相关Schema
class RoleBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=50, description="角色名称")
    code: str = Field(..., min_length=1, max_length=50, description="角色编码")
    description: Optional[str] = Field(None, description="角色描述")


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="角色名称")
    code: Optional[str] = Field(None, min_length=1, max_length=50, description="角色编码")
    description: Optional[str] = Field(None, description="角色描述")


class RoleResponse(RoleBase):
    id: str = Field(..., description="角色ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class RoleWithPermissions(RoleResponse):
    permissions: List['PermissionResponse'] = Field(default_factory=list, description="角色权限列表")


# 2. 菜单相关Schema
class MenuBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=50, description="菜单名称")
    code: str = Field(..., min_length=1, max_length=50, description="菜单编码")
    path: str = Field(..., min_length=1, max_length=100, description="菜单路径")
    icon: Optional[str] = Field(None, max_length=50, description="菜单图标")
    parent_id: Optional[str] = Field(None, description="父菜单ID")
    sort: int = Field(default=0, description="排序")
    is_active: bool = Field(default=True, description="是否激活")


class MenuCreate(MenuBase):
    pass


class MenuUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="菜单名称")
    code: Optional[str] = Field(None, min_length=1, max_length=50, description="菜单编码")
    path: Optional[str] = Field(None, min_length=1, max_length=100, description="菜单路径")
    icon: Optional[str] = Field(None, max_length=50, description="菜单图标")
    parent_id: Optional[str] = Field(None, description="父菜单ID")
    sort: Optional[int] = Field(None, description="排序")
    is_active: Optional[bool] = Field(None, description="是否激活")


class MenuResponse(MenuBase):
    id: str = Field(..., description="菜单ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class MenuWithChildren(MenuResponse):
    children: List['MenuWithChildren'] = Field(default_factory=list, description="子菜单列表")


# 3. 权限相关Schema
class PermissionBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=50, description="权限名称")
    code: str = Field(..., min_length=1, max_length=50, description="权限编码")
    description: Optional[str] = Field(None, description="权限描述")
    menu_id: Optional[str] = Field(None, description="菜单ID")


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="权限名称")
    code: Optional[str] = Field(None, min_length=1, max_length=50, description="权限编码")
    description: Optional[str] = Field(None, description="权限描述")
    menu_id: Optional[str] = Field(None, description="菜单ID")


class PermissionResponse(PermissionBase):
    id: str = Field(..., description="权限ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


# 4. 角色权限关联Schema
class RolePermissionCreate(BaseSchema):
    role_id: str = Field(..., description="角色ID")
    permission_ids: List[str] = Field(..., description="权限ID列表")


# 5. 字典相关Schema
class DictionaryBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=50, description="字典名称")
    type: str = Field(..., min_length=1, max_length=50, description="字典类型")
    description: Optional[str] = Field(None, description="字典描述")


class DictionaryCreate(DictionaryBase):
    pass


class DictionaryUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="字典名称")
    type: Optional[str] = Field(None, min_length=1, max_length=50, description="字典类型")
    description: Optional[str] = Field(None, description="字典描述")


class DictionaryResponse(DictionaryBase):
    id: str = Field(..., description="字典ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class DictionaryWithItems(DictionaryResponse):
    items: List['DictionaryItemResponse'] = Field(default_factory=list, description="字典项列表")


# 6. 字典项相关Schema
class DictionaryItemBase(BaseSchema):
    key: str = Field(..., min_length=1, max_length=50, description="字典项键")
    value: str = Field(..., min_length=1, max_length=100, description="字典项值")
    label: str = Field(..., min_length=1, max_length=50, description="字典项标签")
    sort: int = Field(default=0, description="排序")
    is_active: bool = Field(default=True, description="是否激活")


class DictionaryItemCreate(DictionaryItemBase):
    dictionary_id: str = Field(..., description="字典ID")


class DictionaryItemUpdate(BaseSchema):
    key: Optional[str] = Field(None, min_length=1, max_length=50, description="字典项键")
    value: Optional[str] = Field(None, min_length=1, max_length=100, description="字典项值")
    label: Optional[str] = Field(None, min_length=1, max_length=50, description="字典项标签")
    sort: Optional[int] = Field(None, description="排序")
    is_active: Optional[bool] = Field(None, description="是否激活")


class DictionaryItemResponse(DictionaryItemBase):
    id: str = Field(..., description="字典项ID")
    dictionary_id: str = Field(..., description="字典ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


# 7. 用户相关Schema扩展
class UserRoleUpdate(BaseSchema):
    role_id: Optional[str] = Field(None, description="角色ID")


# 8. 通用响应Schema
class SuccessResponse(BaseSchema):
    success: bool = Field(True, description="是否成功")
    message: str = Field("操作成功", description="响应消息")


class ErrorResponse(BaseSchema):
    success: bool = Field(False, description="是否成功")
    message: str = Field(..., description="错误消息")


# 9. 分页响应Schema
class PaginationMeta(BaseSchema):
    total: int = Field(..., description="总数据量")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")
    total_pages: int = Field(..., description="总页数")


class PaginatedResponse(BaseSchema):
    data: List[BaseSchema] = Field(..., description="数据列表")
    meta: PaginationMeta = Field(..., description="分页元数据")


# 循环引用解析
MenuWithChildren.model_rebuild()
RoleWithPermissions.model_rebuild()
DictionaryWithItems.model_rebuild()
