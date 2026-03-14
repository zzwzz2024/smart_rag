import asyncio
from backend.app.database import get_db
from backend.app.models import User, Role, Permission, RolePermission, Menu

async def check_user_role():
    db = await anext(get_db())
    try:
        # 获取第一个用户
        user_result = await db.execute(User.__table__.select().limit(1))
        user = user_result.first()
        print('User:', user)
        if user:
            user_id = user.id
            role_id = user.role_id
            print('User ID:', user_id)
            print('User role_id:', role_id)
            
            if role_id:
                # 获取角色
                role_result = await db.execute(Role.__table__.select().where(Role.id == role_id))
                role = role_result.first()
                print('Role:', role)
                
                if role:
                    # 获取角色的权限
                    role_permissions = await db.execute(
                        RolePermission.__table__.select().where(RolePermission.role_id == role_id)
                    )
                    permission_ids = [rp.permission_id for rp in role_permissions]
                    print('Permission IDs:', permission_ids)
                    
                    if permission_ids:
                        # 获取权限
                        permissions = await db.execute(
                            Permission.__table__.select().where(Permission.id.in_(permission_ids))
                        )
                        print('Permissions:')
                        for perm in permissions:
                            print(f'  - {perm.name} (Menu ID: {perm.menu_id})')
                    else:
                        print('No permissions assigned to role')
            else:
                print('User has no role assigned')
        else:
            print('No users found')
            
        # 检查是否存在角色
        roles = await db.execute(Role.__table__.select())
        roles = roles.all()
        print('\nRoles:')
        for role in roles:
            print(f'  - {role.name} (ID: {role.id})')
            
        # 检查是否存在权限
        permissions = await db.execute(Permission.__table__.select())
        permissions = permissions.all()
        print('\nPermissions:')
        for perm in permissions:
            print(f'  - {perm.name} (ID: {perm.id}, Menu ID: {perm.menu_id})')
            
    finally:
        await db.close()

if __name__ == '__main__':
    asyncio.run(check_user_role())