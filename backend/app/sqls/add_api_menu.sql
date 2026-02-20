-- 添加知识库菜单和API接口管理子菜单

-- 1. 插入知识库主菜单（如果不存在）
INSERT INTO menus (id, name, code, path, icon, parent_id, sort) VALUES
('7', '知识库', 'knowledge', '/knowledge', '📚', NULL, 200)
ON CONFLICT (code) DO NOTHING;

-- 2. 插入知识库管理子菜单（如果不存在）
INSERT INTO menus (id, name, code, path, icon, parent_id, sort) VALUES
('8', '知识库管理', 'knowledge_base', '/knowledge-base', '📚', '7', 1)
ON CONFLICT (code) DO NOTHING;

-- 3. 插入文档管理子菜单（如果不存在）
INSERT INTO menus (id, name, code, path, icon, parent_id, sort) VALUES
('9', '文档管理', 'documents', '/documents', '📄', '7', 2)
ON CONFLICT (code) DO NOTHING;

-- 4. 插入知识库评估子菜单（如果不存在）
INSERT INTO menus (id, name, code, path, icon, parent_id, sort) VALUES
('10', '知识库评估', 'evaluation', '/evaluation', '📊', '7', 3)
ON CONFLICT (code) DO NOTHING;

-- 5. 插入API接口管理子菜单（如果不存在）
INSERT INTO menus (id, name, code, path, icon, parent_id, sort) VALUES
('11', 'API接口管理', 'api_management', '/api-authorization', '🔑', '7', 4)
ON CONFLICT (code) DO NOTHING;

-- 6. 插入对应的权限（如果不存在）
INSERT INTO permissions (id, name, code, description, menu_id) VALUES
('6', '知识库管理权限', 'knowledge_management', '知识库管理相关操作权限', '8'),
('7', '文档管理权限', 'documents_management', '文档管理相关操作权限', '9'),
('8', '知识库评估权限', 'evaluation_management', '知识库评估相关操作权限', '10'),
('9', 'API接口管理权限', 'api_management', 'API接口管理相关操作权限', '11')
ON CONFLICT (code) DO NOTHING;

-- 7. 为超级管理员角色分配这些权限
INSERT INTO role_permissions (role_id, permission_id) VALUES
('1', '6'),
('1', '7'),
('1', '8'),
('1', '9')
ON CONFLICT DO NOTHING;
