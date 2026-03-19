/*
 Navicat Premium Dump SQL

 Source Server         : 本机测试
 Source Server Type    : PostgreSQL
 Source Server Version : 170009 (170009)
 Source Host           : localhost:5432
 Source Catalog        : projects
 Source Schema         : public

 Target Server Type    : PostgreSQL
 Target Server Version : 170009 (170009)
 File Encoding         : 65001

 Date: 17/03/2026 16:37:00
*/


-- ----------------------------
-- Sequence structure for project_purchases_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."project_purchases_id_seq";
CREATE SEQUENCE "public"."project_purchases_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Table structure for project_info
-- ----------------------------
DROP TABLE IF EXISTS "public"."project_info";
CREATE TABLE "public"."project_info" (
  "project_code" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "project_name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "region" varchar(20) COLLATE "pg_catalog"."default",
  "city" varchar(20) COLLATE "pg_catalog"."default",
  "department" varchar(50) COLLATE "pg_catalog"."default",
  "construction_unit" varchar(50) COLLATE "pg_catalog"."default",
  "contract_amount" numeric(14,2),
  "payment_terms" text COLLATE "pg_catalog"."default",
  "sales_manager" varchar(20) COLLATE "pg_catalog"."default",
  "product_manager" varchar(20) COLLATE "pg_catalog"."default",
  "tech_manager" varchar(20) COLLATE "pg_catalog"."default",
  "ops_manager" varchar(20) COLLATE "pg_catalog"."default",
  "planned_start" date,
  "actual_start" date,
  "planned_end" date,
  "actual_end" date,
  "delay_status" varchar(10) COLLATE "pg_catalog"."default",
  "construction_cycle" varchar(20) COLLATE "pg_catalog"."default"
)
;
COMMENT ON COLUMN "public"."project_info"."project_code" IS '项目编码：唯一标识符，主键';
COMMENT ON COLUMN "public"."project_info"."project_name" IS '项目名称';
COMMENT ON COLUMN "public"."project_info"."region" IS '所属大区';
COMMENT ON COLUMN "public"."project_info"."city" IS '所属城市';
COMMENT ON COLUMN "public"."project_info"."department" IS '所属部门';
COMMENT ON COLUMN "public"."project_info"."construction_unit" IS '建设单位';
COMMENT ON COLUMN "public"."project_info"."contract_amount" IS '合同金额';
COMMENT ON COLUMN "public"."project_info"."payment_terms" IS '付款条款';
COMMENT ON COLUMN "public"."project_info"."sales_manager" IS '销售经理';
COMMENT ON COLUMN "public"."project_info"."product_manager" IS '产品经理';
COMMENT ON COLUMN "public"."project_info"."tech_manager" IS '技术负责人';
COMMENT ON COLUMN "public"."project_info"."ops_manager" IS '运维负责人';
COMMENT ON COLUMN "public"."project_info"."planned_start" IS '计划开始日期';
COMMENT ON COLUMN "public"."project_info"."actual_start" IS '实际开始日期';
COMMENT ON COLUMN "public"."project_info"."planned_end" IS '计划结束日期';
COMMENT ON COLUMN "public"."project_info"."actual_end" IS '实际结束日期';
COMMENT ON COLUMN "public"."project_info"."delay_status" IS '延期状态（如：正常、延期）';
COMMENT ON COLUMN "public"."project_info"."construction_cycle" IS '建设周期';
COMMENT ON TABLE "public"."project_info" IS '项目基础信息表：存储项目的核心档案与管理信息';

-- ----------------------------
-- Table structure for project_purchases
-- ----------------------------
DROP TABLE IF EXISTS "public"."project_purchases";
CREATE TABLE "public"."project_purchases" (
  "id" int4 NOT NULL DEFAULT nextval('project_purchases_id_seq'::regclass),
  "project_code" varchar(50) COLLATE "pg_catalog"."default",
  "project_name" varchar(255) COLLATE "pg_catalog"."default",
  "purchase_item" varchar(100) COLLATE "pg_catalog"."default",
  "quantity" int4,
  "unit_price" numeric(10,2),
  "total_amount" numeric(12,2),
  "supplier" varchar(100) COLLATE "pg_catalog"."default",
  "purchase_officer" varchar(50) COLLATE "pg_catalog"."default",
  "warranty_period" varchar(20) COLLATE "pg_catalog"."default",
  "purchase_date" date,
  "status" varchar(20) COLLATE "pg_catalog"."default"
)
;
COMMENT ON COLUMN "public"."project_purchases"."id" IS '主键ID';
COMMENT ON COLUMN "public"."project_purchases"."project_code" IS '关联项目编码：外键，关联 project_info 表';
COMMENT ON COLUMN "public"."project_purchases"."project_name" IS '项目名称（冗余字段，便于查询展示）';
COMMENT ON COLUMN "public"."project_purchases"."purchase_item" IS '采购物品/服务名称';
COMMENT ON COLUMN "public"."project_purchases"."quantity" IS '采购数量';
COMMENT ON COLUMN "public"."project_purchases"."unit_price" IS '单价';
COMMENT ON COLUMN "public"."project_purchases"."total_amount" IS '总金额';
COMMENT ON COLUMN "public"."project_purchases"."supplier" IS '供应商名称';
COMMENT ON COLUMN "public"."project_purchases"."purchase_officer" IS '采购负责人';
COMMENT ON COLUMN "public"."project_purchases"."warranty_period" IS '质保期';
COMMENT ON COLUMN "public"."project_purchases"."purchase_date" IS '采购日期';
COMMENT ON COLUMN "public"."project_purchases"."status" IS '项目状态';
COMMENT ON TABLE "public"."project_purchases" IS '项目采购记录表：存储与项目关联的物资/服务采购明细';

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."project_purchases_id_seq"
OWNED BY "public"."project_purchases"."id";
SELECT setval('"public"."project_purchases_id_seq"', 2839, true);

-- ----------------------------
-- Primary Key structure for table project_info
-- ----------------------------
ALTER TABLE "public"."project_info" ADD CONSTRAINT "project_info_pkey" PRIMARY KEY ("project_code");

-- ----------------------------
-- Primary Key structure for table project_purchases
-- ----------------------------
ALTER TABLE "public"."project_purchases" ADD CONSTRAINT "project_purchases_pkey" PRIMARY KEY ("id");
