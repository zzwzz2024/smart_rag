-- 系统设置相关表结构初始化脚本

-- 1. 角色表
CREATE TABLE IF NOT EXISTS roles (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    code VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 2. 菜单表
CREATE TABLE IF NOT EXISTS menus (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    code VARCHAR(50) NOT NULL UNIQUE,
    path VARCHAR(100) NOT NULL,
    icon VARCHAR(50),
    parent_id VARCHAR(36) NULL,
    sort INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES menus(id) ON DELETE SET NULL
);

-- 3. 权限表
CREATE TABLE IF NOT EXISTS permissions (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    code VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    menu_id VARCHAR(36) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (menu_id) REFERENCES menus(id) ON DELETE SET NULL
);

-- 4. 角色权限关联表
CREATE TABLE IF NOT EXISTS role_permissions (
    role_id VARCHAR(36) NOT NULL,
    permission_id VARCHAR(36) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
);

-- 5. 字典表
CREATE TABLE IF NOT EXISTS dictionaries (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    type VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 6. 字典项表
CREATE TABLE IF NOT EXISTS dictionary_items (
    id VARCHAR(36) PRIMARY KEY,
    dictionary_id VARCHAR(36) NOT NULL,
    key VARCHAR(50) NOT NULL,
    value VARCHAR(100) NOT NULL,
    label VARCHAR(50) NOT NULL,
    sort INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE (dictionary_id, key),
    FOREIGN KEY (dictionary_id) REFERENCES dictionaries(id) ON DELETE CASCADE
);

-- 7. 更新用户表，添加角色关联
ALTER TABLE IF EXISTS users
ADD COLUMN IF NOT EXISTS role_id VARCHAR(36) NULL,
ADD FOREIGN KEY IF NOT EXISTS (role_id) REFERENCES roles(id) ON DELETE SET NULL;

-- 插入默认数据

-- 默认角色
INSERT INTO roles (id, name, code, description) VALUES
('1', '超级管理员', 'admin', '系统最高权限'),
('2', '普通用户', 'user', '普通用户权限')
ON CONFLICT (code) DO NOTHING;

-- 默认菜单
INSERT INTO menus (id, name, code, path, icon, parent_id, sort) VALUES
('1', '系统设置', 'system', '/system', '🛠️', NULL, 100),
('2', '用户管理', 'system_users', '/system/users', '👤', '1', 1),
('3', '角色管理', 'system_roles', '/system/roles', '🎭', '1', 2),
('4', '菜单管理', 'system_menus', '/system/menus', '📋', '1', 3),
('5', '权限设置', 'system_permissions', '/system/permissions', '🔒', '1', 4),
('6', '字典管理', 'system_dictionaries', '/system/dictionaries', '📚', '1', 5)
ON CONFLICT (code) DO NOTHING;

-- 默认权限
INSERT INTO permissions (id, name, code, description, menu_id) VALUES
('1', '用户管理权限', 'user_management', '用户管理相关操作权限', '2'),
('2', '角色管理权限', 'role_management', '角色管理相关操作权限', '3'),
('3', '菜单管理权限', 'menu_management', '菜单管理相关操作权限', '4'),
('4', '权限设置权限', 'permission_management', '权限设置相关操作权限', '5'),
('5', '字典管理权限', 'dictionary_management', '字典管理相关操作权限', '6')
ON CONFLICT (code) DO NOTHING;

-- 默认角色权限关联
INSERT INTO role_permissions (role_id, permission_id) VALUES
('1', '1'),
('1', '2'),
('1', '3'),
('1', '4'),
('1', '5')
ON CONFLICT DO NOTHING;

-- 默认字典
INSERT INTO dictionaries (id, name, type, description) VALUES
('1', '模型厂商', 'model_vendor', 'AI模型厂商字典'),
('2', '用户状态', 'user_status', '用户状态字典'),
('3', '文档类型', 'document_type', '文档类型字典')
ON CONFLICT (type) DO NOTHING;

-- 默认字典项
INSERT INTO dictionary_items (dictionary_id, key, value, label, sort) VALUES
-- 模型厂商
('1', 'openai', 'openai', 'OpenAI', 1),
('1', 'qwen', 'qwen', '通义千问', 2),
('1', 'deepseek', 'deepseek', '深度求索', 3),
('1', 'ollama', 'ollama', 'Ollama', 4),
-- 用户状态
('2', 'active', 'active', '活跃', 1),
('2', 'inactive', 'inactive', '未激活', 2),
('2', 'disabled', 'disabled', '禁用', 3),
-- 文档类型
('3', 'txt', 'txt', '文本文件', 1),
('3', 'pdf', 'pdf', 'PDF文件', 2),
('3', 'docx', 'docx', 'Word文件', 3),
('3', 'xlsx', 'xlsx', 'Excel文件', 4)
ON CONFLICT (dictionary_id, key) DO NOTHING;