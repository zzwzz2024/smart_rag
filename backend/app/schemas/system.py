from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List, Optional


# 基础Schema
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# 1. 角色相关Schema
class RoleBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=50)
    code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None


class RoleResponse(RoleBase):
    id: str
    created_at: datetime
    updated_at: datetime


class RoleWithPermissions(RoleResponse):
    permissions: List['PermissionResponse'] = []


# 2. 菜单相关Schema
class MenuBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=50)
    code: str = Field(..., min_length=1, max_length=50)
    path: str = Field(..., min_length=1, max_length=100)
    icon: Optional[str] = Field(None, max_length=50)
    parent_id: Optional[str] = None
    sort: int = Field(default=0)
    is_active: bool = Field(default=True)


class MenuCreate(MenuBase):
    pass


class MenuUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    path: Optional[str] = Field(None, min_length=1, max_length=100)
    icon: Optional[str] = Field(None, max_length=50)
    parent_id: Optional[str] = None
    sort: Optional[int] = None
    is_active: Optional[bool] = None


class MenuResponse(MenuBase):
    id: str
    created_at: datetime
    updated_at: datetime


class MenuWithChildren(MenuResponse):
    children: List['MenuWithChildren'] = []


# 3. 权限相关Schema
class PermissionBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=50)
    code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    menu_id: Optional[str] = None


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None
    menu_id: Optional[str] = None


class PermissionResponse(PermissionBase):
    id: str
    created_at: datetime
    updated_at: datetime


# 4. 角色权限关联Schema
class RolePermissionCreate(BaseSchema):
    role_id: str
    permission_ids: List[str]


# 5. 字典相关Schema
class DictionaryBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=50)
    type: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None


class DictionaryCreate(DictionaryBase):
    pass


class DictionaryUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    type: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None


class DictionaryResponse(DictionaryBase):
    id: str
    created_at: datetime
    updated_at: datetime


class DictionaryWithItems(DictionaryResponse):
    items: List['DictionaryItemResponse'] = []


# 6. 字典项相关Schema
class DictionaryItemBase(BaseSchema):
    key: str = Field(..., min_length=1, max_length=50)
    value: str = Field(..., min_length=1, max_length=100)
    label: str = Field(..., min_length=1, max_length=50)
    sort: int = Field(default=0)
    is_active: bool = Field(default=True)


class DictionaryItemCreate(DictionaryItemBase):
    dictionary_id: str


class DictionaryItemUpdate(BaseSchema):
    key: Optional[str] = Field(None, min_length=1, max_length=50)
    value: Optional[str] = Field(None, min_length=1, max_length=100)
    label: Optional[str] = Field(None, min_length=1, max_length=50)
    sort: Optional[int] = None
    is_active: Optional[bool] = None


class DictionaryItemResponse(DictionaryItemBase):
    id: str
    dictionary_id: str
    created_at: datetime
    updated_at: datetime


# 7. 用户相关Schema扩展
class UserRoleUpdate(BaseSchema):
    role_id: Optional[str] = None


# 8. 通用响应Schema
class SuccessResponse(BaseSchema):
    success: bool = True
    message: str = "操作成功"


class ErrorResponse(BaseSchema):
    success: bool = False
    message: str


# 9. 分页响应Schema
class PaginationMeta(BaseSchema):
    total: int
    page: int
    page_size: int
    total_pages: int


class PaginatedResponse(BaseSchema):
    data: List[BaseSchema]
    meta: PaginationMeta


# 循环引用解析
MenuWithChildren.model_rebuild()
RoleWithPermissions.model_rebuild()
DictionaryWithItems.model_rebuild()
