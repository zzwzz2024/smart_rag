-- 添加标签管理和领域管理菜单

-- 假设知识库菜单的ID为已知值，这里使用占位符
-- 首先获取知识库菜单的ID
DO $$
DECLARE
    kb_menu_id VARCHAR(36);
BEGIN
    -- 获取知识库菜单ID
    SELECT id INTO kb_menu_id FROM menu WHERE name = '知识库管理' LIMIT 1;
    
    -- 如果找到知识库菜单，则添加子菜单
    IF kb_menu_id IS NOT NULL THEN
        -- 添加标签管理菜单项
        INSERT INTO menu (id, name, path, component, icon, parent_id, order_num, status, created_at, updated_at)
        VALUES (
            gen_random_uuid()::VARCHAR(36),
            '标签管理',
            '/kb/tags',
            'TagManagement',
            'tag',
            kb_menu_id,
            3,
            1,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        ) ON CONFLICT (path) DO NOTHING;
        
        -- 添加领域管理菜单项
        INSERT INTO menu (id, name, path, component, icon, parent_id, order_num, status, created_at, updated_at)
        VALUES (
            gen_random_uuid()::VARCHAR(36),
            '领域管理',
            '/kb/domains',
            'DomainManagement',
            'area-chart',
            kb_menu_id,
            4,
            1,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        ) ON CONFLICT (path) DO NOTHING;
    END IF;
END $$;
