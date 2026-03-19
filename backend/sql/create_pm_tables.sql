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

 Date: 17/03/2026 19:37:08
*/


-- ----------------------------
-- Sequence structure for kb_evaluations_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."kb_evaluations_id_seq";
CREATE SEQUENCE "public"."kb_evaluations_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

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
-- Table structure for api_authorizations
-- ----------------------------
DROP TABLE IF EXISTS "public"."api_authorizations";
CREATE TABLE "public"."api_authorizations" (
  "id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "vendor_name" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "vendor_contact" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "contact_phone" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "authorized_ips" text COLLATE "pg_catalog"."default",
  "auth_code" varchar(64) COLLATE "pg_catalog"."default" NOT NULL,
  "start_time" timestamp(6) NOT NULL,
  "end_time" timestamp(6) NOT NULL,
  "is_active" bool NOT NULL,
  "created_at" timestamp(6) NOT NULL,
  "updated_at" timestamp(6) NOT NULL
)
;

-- ----------------------------
-- Records of api_authorizations
-- ----------------------------

-- ----------------------------
-- Table structure for api_logs
-- ----------------------------
DROP TABLE IF EXISTS "public"."api_logs";
CREATE TABLE "public"."api_logs" (
  "id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "auth_code" varchar(64) COLLATE "pg_catalog"."default" NOT NULL,
  "endpoint" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "method" varchar(10) COLLATE "pg_catalog"."default" NOT NULL,
  "ip" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "user_agent" text COLLATE "pg_catalog"."default",
  "status" int4 NOT NULL,
  "response_time" int4 NOT NULL,
  "error_message" text COLLATE "pg_catalog"."default",
  "created_at" timestamp(6) NOT NULL
)
;

-- ----------------------------
-- Records of api_logs
-- ----------------------------

-- ----------------------------
-- Table structure for chat_conversations
-- ----------------------------
DROP TABLE IF EXISTS "public"."chat_conversations";
CREATE TABLE "public"."chat_conversations" (
  "id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "user_id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "kb_id" varchar(36) COLLATE "pg_catalog"."default",
  "title" varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "pinned" bool NOT NULL,
  "is_deleted" bool NOT NULL,
  "created_at" timestamp(6) NOT NULL,
  "updated_at" timestamp(6) NOT NULL
)
;

-- ----------------------------
-- Records of chat_conversations
-- ----------------------------

-- ----------------------------
-- Table structure for chat_feedbacks
-- ----------------------------
DROP TABLE IF EXISTS "public"."chat_feedbacks";
CREATE TABLE "public"."chat_feedbacks" (
  "id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "message_id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "rating" int4 NOT NULL,
  "comment" text COLLATE "pg_catalog"."default",
  "is_deleted" bool NOT NULL,
  "created_at" timestamp(6) NOT NULL
)
;

-- ----------------------------
-- Records of chat_feedbacks
-- ----------------------------

-- ----------------------------
-- Table structure for chat_logs
-- ----------------------------
DROP TABLE IF EXISTS "public"."chat_logs";
CREATE TABLE "public"."chat_logs" (
  "id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "user_id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "conversation_id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "message_id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "query" text COLLATE "pg_catalog"."default" NOT NULL,
  "answer" text COLLATE "pg_catalog"."default" NOT NULL,
  "model_used" varchar(100) COLLATE "pg_catalog"."default",
  "knowledge_bases" json,
  "response_time" float8,
  "is_deleted" bool NOT NULL,
  "created_at" timestamp(6) NOT NULL
)
;

-- ----------------------------
-- Records of chat_logs
-- ----------------------------

-- ----------------------------
-- Table structure for chat_messages
-- ----------------------------
DROP TABLE IF EXISTS "public"."chat_messages";
CREATE TABLE "public"."chat_messages" (
  "id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "conversation_id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "role" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "content" text COLLATE "pg_catalog"."default" NOT NULL,
  "citations" json,
  "confidence" float8,
  "retrieval_info" json,
  "token_usage" json,
  "is_deleted" bool NOT NULL,
  "created_at" timestamp(6) NOT NULL
)
;

-- ----------------------------
-- Records of chat_messages
-- ----------------------------

-- ----------------------------
-- Table structure for kb_document_chunks
-- ----------------------------
DROP TABLE IF EXISTS "public"."kb_document_chunks";
CREATE TABLE "public"."kb_document_chunks" (
  "id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "doc_id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "kb_id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "content" text COLLATE "pg_catalog"."default" NOT NULL,
  "chunk_index" int4 NOT NULL,
  "token_count" int4 NOT NULL,
  "meta" json,
  "is_deleted" bool NOT NULL,
  "created_at" timestamp(6) NOT NULL
)
;

-- ----------------------------
-- Records of kb_document_chunks
-- ----------------------------

-- ----------------------------
-- Table structure for kb_document_roles
-- ----------------------------
DROP TABLE IF EXISTS "public"."kb_document_roles";
CREATE TABLE "public"."kb_document_roles" (
  "doc_id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "role_id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "is_deleted" bool NOT NULL,
  "created_at" timestamp(6) NOT NULL
)
;

-- ----------------------------
-- Records of kb_document_roles
-- ----------------------------

-- ----------------------------
-- Table structure for kb_documents
-- ----------------------------
DROP TABLE IF EXISTS "public"."kb_documents";
CREATE TABLE "public"."kb_documents" (
  "id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "kb_id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "filename" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "file_path" varchar(500) COLLATE "pg_catalog"."default" NOT NULL,
  "file_type" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "file_size" int4 NOT NULL,
  "status" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "chunk_count" int4 NOT NULL,
  "meta" json,
  "error_msg" text COLLATE "pg_catalog"."default",
  "is_deleted" bool NOT NULL,
  "created_at" timestamp(6) NOT NULL
)
;

-- ----------------------------
-- Records of kb_documents
-- ----------------------------

-- ----------------------------
-- Table structure for kb_domains
-- ----------------------------
DROP TABLE IF EXISTS "public"."kb_domains";
CREATE TABLE "public"."kb_domains" (
  "id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "name" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "description" varchar(200) COLLATE "pg_catalog"."default",
  "is_active" bool NOT NULL,
  "is_deleted" bool NOT NULL,
  "created_at" timestamp(6) NOT NULL,
  "updated_at" timestamp(6) NOT NULL
)
;

-- ----------------------------
-- Records of kb_domains
-- ----------------------------

-- ----------------------------
-- Table structure for kb_evaluations
-- ----------------------------
DROP TABLE IF EXISTS "public"."kb_evaluations";
CREATE TABLE "public"."kb_evaluations" (
  "id" int4 NOT NULL DEFAULT nextval('kb_evaluations_id_seq'::regclass),
  "query" text COLLATE "pg_catalog"."default" NOT NULL,
  "reference_answer" text COLLATE "pg_catalog"."default" NOT NULL,
  "rag_answer" text COLLATE "pg_catalog"."default" NOT NULL,
  "score" float8 NOT NULL,
  "kb_id" varchar COLLATE "pg_catalog"."default" NOT NULL,
  "model_id" varchar COLLATE "pg_catalog"."default" NOT NULL,
  "is_deleted" bool NOT NULL,
  "created_at" timestamp(6) NOT NULL
)
;

-- ----------------------------
-- Records of kb_evaluations
-- ----------------------------

-- ----------------------------
-- Table structure for kb_knowledge_base_authorization_association
-- ----------------------------
DROP TABLE IF EXISTS "public"."kb_knowledge_base_authorization_association";
CREATE TABLE "public"."kb_knowledge_base_authorization_association" (
  "authorization_id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "knowledge_base_id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL
)
;

-- ----------------------------
-- Records of kb_knowledge_base_authorization_association
-- ----------------------------

-- ----------------------------
-- Table structure for kb_knowledge_base_domain_association
-- ----------------------------
DROP TABLE IF EXISTS "public"."kb_knowledge_base_domain_association";
CREATE TABLE "public"."kb_knowledge_base_domain_association" (
  "knowledge_base_id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "domain_id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL
)
;

-- ----------------------------
-- Records of kb_knowledge_base_domain_association
-- ----------------------------

-- ----------------------------
-- Table structure for kb_knowledge_base_roles
-- ----------------------------
DROP TABLE IF EXISTS "public"."kb_knowledge_base_roles";
CREATE TABLE "public"."kb_knowledge_base_roles" (
  "kb_id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "role_id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "is_deleted" bool NOT NULL,
  "created_at" timestamp(6) NOT NULL
)
;

-- ----------------------------
-- Records of kb_knowledge_base_roles
-- ----------------------------

-- ----------------------------
-- Table structure for kb_knowledge_base_tag_association
-- ----------------------------
DROP TABLE IF EXISTS "public"."kb_knowledge_base_tag_association";
CREATE TABLE "public"."kb_knowledge_base_tag_association" (
  "knowledge_base_id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "tag_id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL
)
;

-- ----------------------------
-- Records of kb_knowledge_base_tag_association
-- ----------------------------

-- ----------------------------
-- Table structure for kb_knowledge_bases
-- ----------------------------
DROP TABLE IF EXISTS "public"."kb_knowledge_bases";
CREATE TABLE "public"."kb_knowledge_bases" (
  "id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "name" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default",
  "avatar" varchar(10) COLLATE "pg_catalog"."default" NOT NULL,
  "embedding_model" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "embedding_model_id" varchar(36) COLLATE "pg_catalog"."default",
  "rerank_model" varchar(100) COLLATE "pg_catalog"."default",
  "rerank_model_id" varchar(36) COLLATE "pg_catalog"."default",
  "chunk_size" int4 NOT NULL,
  "chunk_overlap" int4 NOT NULL,
  "chunk_method" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "retrieval_mode" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "doc_count" int4 NOT NULL,
  "chunk_count" int4 NOT NULL,
  "owner_id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "is_deleted" bool NOT NULL,
  "created_at" timestamp(6) NOT NULL,
  "updated_at" timestamp(6) NOT NULL
)
;

-- ----------------------------
-- Records of kb_knowledge_bases
-- ----------------------------

-- ----------------------------
-- Table structure for kb_tags
-- ----------------------------
DROP TABLE IF EXISTS "public"."kb_tags";
CREATE TABLE "public"."kb_tags" (
  "id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "name" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "color" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "is_active" bool NOT NULL,
  "is_deleted" bool NOT NULL,
  "created_at" timestamp(6) NOT NULL,
  "updated_at" timestamp(6) NOT NULL
)
;

-- ----------------------------
-- Records of kb_tags
-- ----------------------------

-- ----------------------------
-- Table structure for m_model_vendors
-- ----------------------------
DROP TABLE IF EXISTS "public"."m_model_vendors";
CREATE TABLE "public"."m_model_vendors" (
  "id" varchar COLLATE "pg_catalog"."default" NOT NULL,
  "name" varchar COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default",
  "is_deleted" bool NOT NULL,
  "created_at" timestamptz(6) DEFAULT now(),
  "updated_at" timestamptz(6) DEFAULT now()
)
;

-- ----------------------------
-- Records of m_model_vendors
-- ----------------------------

-- ----------------------------
-- Table structure for m_models
-- ----------------------------
DROP TABLE IF EXISTS "public"."m_models";
CREATE TABLE "public"."m_models" (
  "id" varchar COLLATE "pg_catalog"."default" NOT NULL,
  "name" varchar COLLATE "pg_catalog"."default" NOT NULL,
  "model" varchar COLLATE "pg_catalog"."default" NOT NULL,
  "type" varchar COLLATE "pg_catalog"."default" NOT NULL,
  "vendor_id" varchar COLLATE "pg_catalog"."default",
  "api_key" varchar COLLATE "pg_catalog"."default",
  "base_url" varchar COLLATE "pg_catalog"."default",
  "description" text COLLATE "pg_catalog"."default",
  "is_active" bool NOT NULL,
  "is_default" bool NOT NULL,
  "is_deleted" bool NOT NULL,
  "top_k" int4,
  "temperature" float8,
  "top_p" float8,
  "created_at" timestamptz(6) DEFAULT now(),
  "updated_at" timestamptz(6) DEFAULT now()
)
;

-- ----------------------------
-- Records of m_models
-- ----------------------------

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
-- Records of project_info
-- ----------------------------
INSERT INTO "public"."project_info" VALUES ('PROJ_001', '杭州教育局信息化建设项目', '华北', '杭州', '教育局', '技术开发部', 4717561.17, '30%预付款，验收后付60%，10%质保金', '张洋', '李强', '王洋', '刘杰', '2024-08-19', '2024-08-23', '2025-01-09', '2025-01-02', '否', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_002', '重庆公安局信息化建设项目', '华中', '重庆', '公安局', '技术开发部', 3419485.19, '按月结算', '张军', '李强', '王敏', '刘芳', '2025-05-28', '2025-05-29', '2025-09-28', '2025-10-12', '是', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_003', '重庆财政局信息化建设项目', '华中', '重庆', '财政局', '技术开发部', 4991666.01, '验收一次性付清', '张静', '李敏', '王静', '刘敏', '2024-03-20', '2024-03-26', '2024-07-31', '2024-08-16', '是', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_004', '西安卫健委信息化建设项目', '华北', '西安', '卫健委', '技术开发部', 1276859.15, '验收一次性付清', '张洋', '李强', '王娜', '刘伟', '2025-04-30', '2025-05-09', '2025-08-18', '2025-08-18', '否', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_006', '武汉公安局信息化建设项目', '西南', '武汉', '公安局', '技术开发部', 4011887.14, '30%预付款，验收后付60%，10%质保金', '张杰', '李伟', '王娜', '刘强', '2024-04-16', '2024-04-16', '2024-09-16', '2024-09-29', '是', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_007', '成都住建局信息化建设项目', '华北', '成都', '住建局', '技术开发部', 4949273.72, '验收一次性付清', '张伟', '李军', '王伟', '刘芳', '2025-08-24', '2025-08-28', '2025-12-19', '2025-12-23', '是', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_008', '广州住建局信息化建设项目', '华北', '广州', '住建局', '技术开发部', 4635991.44, '按月结算', '张军', '李杰', '王伟', '刘静', '2024-11-16', '2024-11-21', '2025-04-18', '2025-04-13', '否', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_009', '济南住建局信息化建设项目', '华南', '济南', '住建局', '技术开发部', 1003320.87, '按月结算', '张磊', '李芳', '王洋', '刘敏', '2025-01-12', '2025-01-18', '2025-07-09', '2025-07-22', '是', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_010', '北京住建局信息化建设项目', '华南', '北京', '住建局', '技术开发部', 3346727.36, '30%预付款，验收后付60%，10%质保金', '张静', '李敏', '王敏', '刘军', '2024-10-15', '2024-10-25', '2025-02-24', '2025-03-03', '是', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_011', '广州公安局信息化建设项目', '华南', '广州', '公安局', '技术开发部', 4007532.74, '验收一次性付清', '张敏', '李强', '王强', '刘磊', '2025-11-21', '2025-12-01', '2026-05-01', '2026-05-16', '是', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_013', '贵阳人社局信息化建设项目', '西南', '贵阳', '人社局', '技术开发部', 4185003.76, '验收一次性付清', '张芳', '李磊', '王静', '刘静', '2024-08-25', '2024-09-03', '2024-12-15', '2024-12-26', '是', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_014', '重庆住建局信息化建设项目', '西南', '重庆', '住建局', '技术开发部', 2984957.81, '验收一次性付清', '张芳', '李军', '王磊', '刘敏', '2024-06-06', '2024-06-13', '2024-11-13', '2024-11-06', '否', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_015', '杭州卫健委信息化建设项目', '华东', '杭州', '卫健委', '技术开发部', 2768608.34, '30%预付款，验收后付60%，10%质保金', '张娜', '李强', '王磊', '刘娜', '2024-02-24', '2024-02-27', '2024-07-08', '2024-06-29', '否', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_016', '上海公安局信息化建设项目', '华东', '上海', '公安局', '技术开发部', 2849893.47, '验收一次性付清', '张磊', '李洋', '王伟', '刘静', '2024-11-23', '2024-11-26', '2025-02-25', '2025-03-11', '是', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_017', '武汉卫健委信息化建设项目', '西南', '武汉', '卫健委', '技术开发部', 4707710.65, '30%预付款，验收后付60%，10%质保金', '张伟', '李伟', '王伟', '刘娜', '2025-11-15', '2025-11-22', '2026-02-14', '2026-02-11', '否', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_018', '北京财政局信息化建设项目', '西南', '北京', '财政局', '技术开发部', 2452665.17, '30%预付款，验收后付60%，10%质保金', '张静', '李伟', '王娜', '刘强', '2024-09-18', '2024-09-27', '2025-01-19', '2025-01-11', '否', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_019', '上海教育局信息化建设项目', '华南', '上海', '教育局', '技术开发部', 4200052.83, '30%预付款，验收后付60%，10%质保金', '张洋', '李敏', '王敏', '刘杰', '2024-08-23', '2024-08-23', '2024-12-30', '2025-01-13', '是', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_020', '遵义人社局信息化建设项目', '华中', '遵义', '人社局', '技术开发部', 3331043.57, '验收一次性付清', '张洋', '李静', '王静', '刘杰', '2025-04-14', '2025-04-17', '2025-09-24', '2025-10-06', '是', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_022', '成都教育局信息化建设项目', '华南', '成都', '教育局', '技术开发部', 1144019.80, '验收一次性付清', '张娜', '李洋', '王强', '刘敏', '2025-08-17', '2025-08-17', '2025-12-03', '2025-12-09', '是', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_024', '杭州人社局信息化建设项目', '华南', '杭州', '人社局', '技术开发部', 2984515.71, '30%预付款，验收后付60%，10%质保金', '张芳', '李静', '王静', '刘洋', '2024-04-11', '2024-04-17', '2024-09-27', '2024-10-12', '是', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_026', '成都卫健委信息化建设项目', '西北', '成都', '卫健委', '技术开发部', 3007608.78, '按月结算', '张静', '李敏', '王杰', '刘强', '2025-03-02', '2025-03-06', '2025-08-15', '2025-08-08', '否', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_028', '贵阳卫健委信息化建设项目', '华南', '贵阳', '卫健委', '技术开发部', 3278909.19, '按月结算', '张军', '李娜', '王军', '刘敏', '2025-05-27', '2025-06-01', '2025-09-25', '2025-09-15', '否', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_029', '深圳住建局信息化建设项目', '华北', '深圳', '住建局', '技术开发部', 3625841.66, '按月结算', '张芳', '李磊', '王静', '刘强', '2024-06-15', '2024-06-17', '2024-11-25', '2024-11-27', '是', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_030', '深圳人社局信息化建设项目', '华北', '深圳', '人社局', '技术开发部', 3609256.77, '30%预付款，验收后付60%，10%质保金', '张静', '李敏', '王静', '刘静', '2024-11-24', '2024-12-01', '2025-03-14', '2025-03-24', '是', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_031', '北京教育局信息化建设项目', '华北', '北京', '教育局', '技术开发部', 1199358.38, '按月结算', '张磊', '李伟', '王军', '刘静', '2024-11-03', '2024-11-08', '2025-04-02', '2025-04-09', '是', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_032', '遵义教育局信息化建设项目', '西北', '遵义', '教育局', '技术开发部', 2207018.22, '30%预付款，验收后付60%，10%质保金', '张军', '李娜', '王芳', '刘敏', '2024-01-18', '2024-01-26', '2024-06-13', '2024-06-10', '否', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_035', '贵阳住建局信息化建设项目', '华北', '贵阳', '住建局', '技术开发部', 2887012.79, '验收一次性付清', '张强', '李娜', '王军', '刘娜', '2025-12-06', '2025-12-11', '2026-05-14', '2026-05-10', '否', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_036', '济南人社局信息化建设项目', '华北', '济南', '人社局', '技术开发部', 3940977.46, '验收一次性付清', '张芳', '李娜', '王军', '刘静', '2025-03-08', '2025-03-10', '2025-07-19', '2025-07-31', '是', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_037', '北京公安局信息化建设项目', '华南', '北京', '公安局', '技术开发部', 3025526.35, '30%预付款，验收后付60%，10%质保金', '张磊', '李军', '王芳', '刘杰', '2024-11-22', '2024-11-22', '2025-05-03', '2025-05-13', '是', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_038', '武汉人社局信息化建设项目', '华北', '武汉', '人社局', '技术开发部', 4204670.93, '按月结算', '张军', '李强', '王磊', '刘芳', '2025-06-21', '2025-06-27', '2025-11-18', '2025-11-21', '是', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_040', '西安人社局信息化建设项目', '西南', '西安', '人社局', '技术开发部', 809445.87, '验收一次性付清', '张静', '李娜', '王芳', '刘敏', '2024-10-14', '2024-10-22', '2025-03-13', '2025-03-29', '是', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_041', '济南卫健委信息化建设项目', '西南', '济南', '卫健委', '技术开发部', 1001349.64, '按月结算', '张强', '李敏', '王军', '刘娜', '2025-04-21', '2025-05-01', '2025-08-16', '2025-08-24', '是', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_044', '北京人社局信息化建设项目', '华中', '北京', '人社局', '技术开发部', 4464309.53, '验收一次性付清', '张磊', '李静', '王芳', '刘军', '2024-12-29', '2025-01-01', '2025-05-11', '2025-05-23', '是', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_045', '上海财政局信息化建设项目', '华北', '上海', '财政局', '技术开发部', 3742561.64, '验收一次性付清', '张军', '李磊', '王杰', '刘伟', '2024-05-09', '2024-05-13', '2024-10-24', '2024-10-22', '否', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_049', '深圳卫健委信息化建设项目', '华南', '深圳', '卫健委', '技术开发部', 3243116.58, '按月结算', '张杰', '李洋', '王静', '刘伟', '2024-03-08', '2024-03-14', '2024-08-26', '2024-09-03', '是', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_052', '北京卫健委信息化建设项目', '华南', '北京', '卫健委', '技术开发部', 4874436.48, '验收一次性付清', '张洋', '李伟', '王军', '刘磊', '2024-11-15', '2024-11-17', '2025-02-17', '2025-03-07', '是', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_053', '济南财政局信息化建设项目', '华东', '济南', '财政局', '技术开发部', 3489829.21, '30%预付款，验收后付60%，10%质保金', '张洋', '李军', '王伟', '刘娜', '2024-09-30', '2024-10-07', '2025-01-09', '2025-01-04', '否', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_055', '遵义卫健委信息化建设项目', '华南', '遵义', '卫健委', '技术开发部', 2685843.63, '按月结算', '张磊', '李芳', '王洋', '刘娜', '2024-02-06', '2024-02-11', '2024-06-28', '2024-06-28', '否', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_056', '武汉财政局信息化建设项目', '华南', '武汉', '财政局', '技术开发部', 2485460.53, '按月结算', '张敏', '李娜', '王静', '刘芳', '2025-07-25', '2025-07-27', '2025-12-03', '2025-12-17', '是', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_067', '重庆人社局信息化建设项目', '华南', '重庆', '人社局', '技术开发部', 3758345.60, '验收一次性付清', '张杰', '李杰', '王静', '刘磊', '2024-05-19', '2024-05-25', '2024-09-03', '2024-09-13', '是', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_069', '广州卫健委信息化建设项目', '华中', '广州', '卫健委', '技术开发部', 803721.21, '按月结算', '张伟', '李敏', '王杰', '刘敏', '2024-05-03', '2024-05-11', '2024-08-04', '2024-08-10', '是', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_073', '遵义公安局信息化建设项目', '华中', '遵义', '公安局', '技术开发部', 1404576.60, '按月结算', '张军', '李杰', '王敏', '刘芳', '2024-03-16', '2024-03-16', '2024-06-19', '2024-06-23', '是', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_077', '成都人社局信息化建设项目', '西南', '成都', '人社局', '技术开发部', 4718749.70, '30%预付款，验收后付60%，10%质保金', '张杰', '李芳', '王芳', '刘磊', '2024-02-05', '2024-02-14', '2024-05-19', '2024-05-28', '是', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_078', '西安财政局信息化建设项目', '西北', '西安', '财政局', '技术开发部', 2108486.34, '按月结算', '张伟', '李军', '王芳', '刘强', '2025-11-24', '2025-11-30', '2026-04-24', '2026-04-20', '否', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_079', '西安住建局信息化建设项目', '西南', '西安', '住建局', '技术开发部', 1573573.28, '验收一次性付清', '张强', '李强', '王磊', '刘敏', '2024-12-18', '2024-12-27', '2025-04-11', '2025-04-08', '否', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_081', '重庆卫健委信息化建设项目', '西北', '重庆', '卫健委', '技术开发部', 639903.80, '验收一次性付清', '张伟', '李伟', '王伟', '刘敏', '2024-10-09', '2024-10-15', '2025-03-11', '2025-03-25', '是', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_083', '重庆教育局信息化建设项目', '西南', '重庆', '教育局', '技术开发部', 1641680.18, '按月结算', '张杰', '李静', '王洋', '刘伟', '2024-12-01', '2024-12-10', '2025-04-12', '2025-04-16', '是', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_084', '成都财政局信息化建设项目', '西北', '成都', '财政局', '技术开发部', 3946155.80, '按月结算', '张强', '李伟', '王静', '刘洋', '2024-07-07', '2024-07-13', '2024-11-15', '2024-12-03', '是', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_085', '成都公安局信息化建设项目', '华东', '成都', '公安局', '技术开发部', 1744376.93, '30%预付款，验收后付60%，10%质保金', '张杰', '李芳', '王洋', '刘磊', '2024-03-28', '2024-04-01', '2024-08-22', '2024-09-07', '是', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_092', '遵义住建局信息化建设项目', '华中', '遵义', '住建局', '技术开发部', 4542313.98, '30%预付款，验收后付60%，10%质保金', '张敏', '李洋', '王磊', '刘磊', '2025-02-08', '2025-02-08', '2025-05-20', '2025-06-07', '是', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_094', '深圳教育局信息化建设项目', '华东', '深圳', '教育局', '技术开发部', 3509298.09, '验收一次性付清', '张强', '李杰', '王芳', '刘静', '2024-02-07', '2024-02-16', '2024-07-26', '2024-07-31', '是', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_096', '上海卫健委信息化建设项目', '华中', '上海', '卫健委', '技术开发部', 2401476.73, '按月结算', '张杰', '李伟', '王芳', '刘芳', '2025-03-21', '2025-03-23', '2025-06-22', '2025-06-30', '是', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_100', '杭州住建局信息化建设项目', '华北', '杭州', '住建局', '技术开发部', 879998.78, '30%预付款，验收后付60%，10%质保金', '张强', '李芳', '王洋', '刘芳', '2025-08-06', '2025-08-09', '2026-01-28', '2026-01-21', '否', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_102', '西安教育局信息化建设项目', '西南', '西安', '教育局', '技术开发部', 2369298.15, '按月结算', '张磊', '李静', '王杰', '刘伟', '2025-03-11', '2025-03-20', '2025-08-20', '2025-09-07', '是', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_107', '贵阳财政局信息化建设项目', '西南', '贵阳', '财政局', '技术开发部', 1976186.23, '验收一次性付清', '张强', '李娜', '王娜', '刘军', '2024-10-02', '2024-10-04', '2025-01-05', '2025-01-23', '是', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_108', '遵义财政局信息化建设项目', '华东', '遵义', '财政局', '技术开发部', 4642197.67, '按月结算', '张杰', '李静', '王洋', '刘洋', '2024-11-13', '2024-11-19', '2025-03-25', '2025-03-24', '否', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_119', '济南公安局信息化建设项目', '西北', '济南', '公安局', '技术开发部', 3261041.53, '验收一次性付清', '张军', '李军', '王娜', '刘杰', '2024-12-23', '2024-12-24', '2025-04-17', '2025-04-17', '否', '6个月');
INSERT INTO "public"."project_info" VALUES ('PROJ_120', '广州教育局信息化建设项目', '华南', '广州', '教育局', '技术开发部', 3351232.44, '按月结算', '张伟', '李芳', '王娜', '刘娜', '2024-12-11', '2024-12-16', '2025-03-23', '2025-03-27', '是', '6个月');

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
-- Records of project_purchases
-- ----------------------------
INSERT INTO "public"."project_purchases" VALUES (2723, 'PROJ_001', '杭州教育局信息化建设项目', 'UPS电源', 10, 862.61, 1233.27, '王强', '高静', '3年', '2024-05-22', '已入库');
INSERT INTO "public"."project_purchases" VALUES (2724, 'PROJ_001', '杭州教育局信息化建设项目', 'UPS电源', 5, 977.05, 4446.87, '陈明', '高静', '5年', '2024-01-14', '待发货');
INSERT INTO "public"."project_purchases" VALUES (2725, 'PROJ_001', '杭州教育局信息化建设项目', 'UPS电源', 9, 7694.76, 74782.26, '陈明', '高静', '5年', '2024-06-10', '已入库');
INSERT INTO "public"."project_purchases" VALUES (2726, 'PROJ_002', '重庆公安局信息化建设项目', 'UPS电源', 3, 5870.48, 26640.30, '李丽', '高静', '4年', '2024-04-01', '已入库');
INSERT INTO "public"."project_purchases" VALUES (2727, 'PROJ_002', '重庆公安局信息化建设项目', 'UPS电源', 6, 2329.80, 11097.18, '王强', '高静', '1年', '2024-02-10', '待发货');
INSERT INTO "public"."project_purchases" VALUES (2728, 'PROJ_002', '重庆公安局信息化建设项目', 'UPS电源', 10, 10457.19, 741.14, '王强', '高静', '2年', '2024-11-05', '待发货');
INSERT INTO "public"."project_purchases" VALUES (2729, 'PROJ_003', '重庆财政局信息化建设项目', 'UPS电源', 2, 5061.18, 20740.23, '陈明', '高静', '3年', '2024-12-20', '待发货');
INSERT INTO "public"."project_purchases" VALUES (2730, 'PROJ_004', '西安卫健委信息化建设项目', 'UPS电源', 7, 6710.90, 27767.58, '王强', '高静', '1年', '2024-07-17', '已入库');
INSERT INTO "public"."project_purchases" VALUES (2731, 'PROJ_004', '西安卫健委信息化建设项目', 'UPS电源', 4, 2846.89, 5519.36, '周敏', '高静', '4年', '2024-10-27', '已入库');
INSERT INTO "public"."project_purchases" VALUES (2732, 'PROJ_004', '西安卫健委信息化建设项目', 'UPS电源', 9, 2555.94, 84262.68, '陈明', '高静', '4年', '2024-11-16', '运输中');
INSERT INTO "public"."project_purchases" VALUES (2733, 'PROJ_006', '武汉公安局信息化建设项目', 'UPS电源', 10, 6694.36, 14436.92, '周敏', '高静', '2年', '2024-07-23', '已入库');
INSERT INTO "public"."project_purchases" VALUES (2734, 'PROJ_006', '武汉公安局信息化建设项目', 'UPS电源', 7, 1396.28, 85871.43, '赵刚', '高静', '5年', '2024-04-25', '已取消');
INSERT INTO "public"."project_purchases" VALUES (2735, 'PROJ_006', '武汉公安局信息化建设项目', 'UPS电源', 7, 9376.30, 82435.20, '赵刚', '高静', '4年', '2024-10-14', '已取消');
INSERT INTO "public"."project_purchases" VALUES (2736, 'PROJ_007', '成都住建局信息化建设项目', 'UPS电源', 3, 9488.80, 39032.24, '周敏', '高静', '4年', '2024-05-14', '已入库');
INSERT INTO "public"."project_purchases" VALUES (2737, 'PROJ_008', '广州住建局信息化建设项目', 'UPS电源', 2, 3530.32, 14034.72, '赵刚', '高静', '1年', '2024-04-14', '已入库');
INSERT INTO "public"."project_purchases" VALUES (2738, 'PROJ_009', '济南住建局信息化建设项目', 'UPS电源', 8, 4570.81, 7812.94, '王强', '高静', '1年', '2024-09-26', '待发货');
INSERT INTO "public"."project_purchases" VALUES (2739, 'PROJ_009', '济南住建局信息化建设项目', 'UPS电源', 3, 8178.64, 20328.33, '王强', '高静', '3年', '2024-05-13', '运输中');
INSERT INTO "public"."project_purchases" VALUES (2740, 'PROJ_010', '北京住建局信息化建设项目', 'UPS电源', 11, 3140.25, 23065.92, '陈明', '高静', '2年', '2024-05-05', '运输中');
INSERT INTO "public"."project_purchases" VALUES (2741, 'PROJ_010', '北京住建局信息化建设项目', 'UPS电源', 7, 9174.96, 12629.10, '王强', '高静', '2年', '2024-09-10', '已入库');
INSERT INTO "public"."project_purchases" VALUES (2742, 'PROJ_010', '北京住建局信息化建设项目', 'UPS电源', 2, 914.03, 39594.38, '周敏', '高静', '4年', '2024-06-16', '待发货');
INSERT INTO "public"."project_purchases" VALUES (2743, 'PROJ_011', '广州公安局信息化建设项目', 'UPS电源', 3, 10475.98, 9136.42, '陈明', '高静', '2年', '2024-05-27', '已取消');
INSERT INTO "public"."project_purchases" VALUES (2744, 'PROJ_013', '贵阳人社局信息化建设项目', 'UPS电源', 2, 6563.18, 16580.74, '李丽', '高静', '3年', '2024-04-10', '待发货');
INSERT INTO "public"."project_purchases" VALUES (2745, 'PROJ_014', '重庆住建局信息化建设项目', 'UPS电源', 1, 7114.03, 38829.69, '李丽', '高静', '3年', '2024-01-30', '运输中');
INSERT INTO "public"."project_purchases" VALUES (2746, 'PROJ_014', '重庆住建局信息化建设项目', 'UPS电源', 5, 969.16, 23483.20, '赵刚', '高静', '5年', '2024-11-14', '待发货');
INSERT INTO "public"."project_purchases" VALUES (2747, 'PROJ_014', '重庆住建局信息化建设项目', 'UPS电源', 6, 5108.49, 57888.50, '李丽', '高静', '1年', '2024-01-23', '待发货');
INSERT INTO "public"."project_purchases" VALUES (2748, 'PROJ_015', '杭州卫健委信息化建设项目', 'UPS电源', 8, 1777.53, 43141.84, '王强', '高静', '5年', '2024-01-05', '已取消');
INSERT INTO "public"."project_purchases" VALUES (2749, 'PROJ_015', '杭州卫健委信息化建设项目', 'UPS电源', 1, 3805.53, 103713.40, '周敏', '高静', '2年', '2024-06-20', '运输中');
INSERT INTO "public"."project_purchases" VALUES (2750, 'PROJ_015', '杭州卫健委信息化建设项目', 'UPS电源', 10, 516.50, 22065.50, '陈明', '高静', '2年', '2024-01-07', '已入库');
INSERT INTO "public"."project_purchases" VALUES (2751, 'PROJ_016', '上海公安局信息化建设项目', 'UPS电源', 8, 4132.47, 37087.88, '王强', '高静', '1年', '2024-10-08', '已入库');
INSERT INTO "public"."project_purchases" VALUES (2752, 'PROJ_016', '上海公安局信息化建设项目', 'UPS电源', 7, 4670.27, 3834.06, '李丽', '高静', '5年', '2024-09-07', '已取消');
INSERT INTO "public"."project_purchases" VALUES (2753, 'PROJ_017', '武汉卫健委信息化建设项目', 'UPS电源', 1, 9460.72, 8118.87, '陈明', '高静', '4年', '2024-04-20', '运输中');
INSERT INTO "public"."project_purchases" VALUES (2754, 'PROJ_018', '北京财政局信息化建设项目', 'UPS电源', 9, 3503.32, 18908.50, '陈明', '高静', '2年', '2024-03-22', '运输中');
INSERT INTO "public"."project_purchases" VALUES (2755, 'PROJ_018', '北京财政局信息化建设项目', 'UPS电源', 2, 2363.78, 83270.30, '赵刚', '高静', '3年', '2024-11-09', '已取消');
INSERT INTO "public"."project_purchases" VALUES (2756, 'PROJ_019', '上海教育局信息化建设项目', 'UPS电源', 9, 1713.97, 38212.16, '陈明', '高静', '2年', '2024-06-07', '已入库');
INSERT INTO "public"."project_purchases" VALUES (2757, 'PROJ_019', '上海教育局信息化建设项目', 'UPS电源', 7, 1058.82, 3368.55, '周敏', '高静', '3年', '2024-07-06', '已取消');
INSERT INTO "public"."project_purchases" VALUES (2758, 'PROJ_020', '遵义人社局信息化建设项目', 'UPS电源', 6, 2548.97, 15531.78, '陈明', '高静', '2年', '2024-11-17', '待发货');
INSERT INTO "public"."project_purchases" VALUES (2759, 'PROJ_020', '遵义人社局信息化建设项目', 'UPS电源', 6, 5219.23, 8321.46, '赵刚', '高静', '1年', '2024-04-23', '已入库');
INSERT INTO "public"."project_purchases" VALUES (2760, 'PROJ_020', '遵义人社局信息化建设项目', 'UPS电源', 6, 8082.65, 13758.48, '周敏', '高静', '1年', '2024-12-06', '待发货');
INSERT INTO "public"."project_purchases" VALUES (2761, 'PROJ_022', '成都教育局信息化建设项目', 'UPS电源', 2, 2872.06, 9907.38, '周敏', '高静', '4年', '2024-11-29', '待发货');
INSERT INTO "public"."project_purchases" VALUES (2762, 'PROJ_024', '杭州人社局信息化建设项目', 'UPS电源', 2, 2870.12, 22776.63, '赵刚', '高静', '1年', '2024-11-19', '待发货');
INSERT INTO "public"."project_purchases" VALUES (2763, 'PROJ_024', '杭州人社局信息化建设项目', 'UPS电源', 8, 1675.58, 14965.30, '陈明', '高静', '4年', '2024-06-03', '已入库');
INSERT INTO "public"."project_purchases" VALUES (2764, 'PROJ_024', '杭州人社局信息化建设项目', 'UPS电源', 7, 4048.63, 40297.95, '赵刚', '高静', '2年', '2024-06-17', '运输中');
INSERT INTO "public"."project_purchases" VALUES (2765, 'PROJ_026', '成都卫健委信息化建设项目', 'UPS电源', 2, 2348.07, 5598.70, '陈明', '高静', '5年', '2024-06-13', '待发货');
INSERT INTO "public"."project_purchases" VALUES (2766, 'PROJ_028', '贵阳卫健委信息化建设项目', 'UPS电源', 1, 8496.28, 10673.74, '李丽', '高静', '4年', '2024-09-08', '运输中');
INSERT INTO "public"."project_purchases" VALUES (2767, 'PROJ_028', '贵阳卫健委信息化建设项目', 'UPS电源', 2, 1997.38, 23815.48, '周敏', '高静', '3年', '2024-05-22', '运输中');
INSERT INTO "public"."project_purchases" VALUES (2768, 'PROJ_028', '贵阳卫健委信息化建设项目', 'UPS电源', 9, 9694.66, 74862.00, '王强', '高静', '4年', '2024-11-26', '已取消');
INSERT INTO "public"."project_purchases" VALUES (2769, 'PROJ_029', '深圳住建局信息化建设项目', 'UPS电源', 9, 8239.57, 53722.80, '周敏', '高静', '3年', '2024-02-20', '已取消');
INSERT INTO "public"."project_purchases" VALUES (2770, 'PROJ_030', '深圳人社局信息化建设项目', 'UPS电源', 2, 2439.40, 14251.68, '陈明', '高静', '2年', '2024-04-10', '已取消');
INSERT INTO "public"."project_purchases" VALUES (2771, 'PROJ_030', '深圳人社局信息化建设项目', 'UPS电源', 9, 8678.60, 26760.90, '周敏', '高静', '2年', '2024-05-07', '运输中');
INSERT INTO "public"."project_purchases" VALUES (2772, 'PROJ_030', '深圳人社局信息化建设项目', 'UPS电源', 6, 6227.92, 87070.90, '李丽', '高静', '5年', '2024-08-06', '待发货');
INSERT INTO "public"."project_purchases" VALUES (2773, 'PROJ_031', '北京教育局信息化建设项目', 'UPS电源', 1, 7333.13, 16133.13, '李丽', '高静', '3年', '2024-05-28', '运输中');
INSERT INTO "public"."project_purchases" VALUES (2774, 'PROJ_031', '北京教育局信息化建设项目', 'UPS电源', 9, 2041.53, 46589.15, '赵刚', '高静', '3年', '2024-08-07', '运输中');
INSERT INTO "public"."project_purchases" VALUES (2775, 'PROJ_032', '遵义教育局信息化建设项目', 'UPS电源', 6, 9574.30, 20840.64, '赵刚', '高静', '3年', '2024-04-26', '运输中');
INSERT INTO "public"."project_purchases" VALUES (2776, 'PROJ_032', '遵义教育局信息化建设项目', 'UPS电源', 10, 9630.08, 18277.04, '李丽', '高静', '2年', '2024-09-14', '已取消');
INSERT INTO "public"."project_purchases" VALUES (2777, 'PROJ_035', '贵阳住建局信息化建设项目', 'UPS电源', 9, 986.51, 40044.13, '赵刚', '高静', '5年', '2024-10-13', '待发货');
INSERT INTO "public"."project_purchases" VALUES (2778, 'PROJ_035', '贵阳住建局信息化建设项目', 'UPS电源', 7, 7867.93, 8753.46, '周敏', '高静', '5年', '2024-02-01', '运输中');
INSERT INTO "public"."project_purchases" VALUES (2779, 'PROJ_035', '贵阳住建局信息化建设项目', 'UPS电源', 9, 9890.94, 25866.89, '陈明', '高静', '3年', '2024-10-24', '已入库');
INSERT INTO "public"."project_purchases" VALUES (2780, 'PROJ_036', '济南人社局信息化建设项目', 'UPS电源', 3, 1145.14, 76499.20, '周敏', '高静', '1年', '2024-02-20', '待发货');
INSERT INTO "public"."project_purchases" VALUES (2781, 'PROJ_036', '济南人社局信息化建设项目', 'UPS电源', 11, 4592.08, 82895.52, '周敏', '高静', '4年', '2024-07-08', '已取消');
INSERT INTO "public"."project_purchases" VALUES (2782, 'PROJ_036', '济南人社局信息化建设项目', 'UPS电源', 9, 4900.75, 65284.90, '赵刚', '高静', '2年', '2024-10-18', '已取消');
INSERT INTO "public"."project_purchases" VALUES (2783, 'PROJ_037', '北京公安局信息化建设项目', 'UPS电源', 8, 2641.73, 26490.40, '陈明', '高静', '4年', '2024-04-29', '运输中');
INSERT INTO "public"."project_purchases" VALUES (2784, 'PROJ_037', '北京公安局信息化建设项目', 'UPS电源', 1, 9380.87, 52503.30, '王强', '高静', '2年', '2024-05-08', '已入库');
INSERT INTO "public"."project_purchases" VALUES (2785, 'PROJ_038', '武汉人社局信息化建设项目', 'UPS电源', 8, 4247.31, 1503.50, '王强', '高静', '5年', '2024-06-13', '待发货');
INSERT INTO "public"."project_purchases" VALUES (2786, 'PROJ_040', '西安人社局信息化建设项目', 'UPS电源', 8, 5203.03, 10531.46, '陈明', '高静', '4年', '2024-12-30', '已取消');
INSERT INTO "public"."project_purchases" VALUES (2787, 'PROJ_040', '西安人社局信息化建设项目', 'UPS电源', 6, 5195.41, 14506.08, '王强', '高静', '1年', '2024-01-19', '已入库');
INSERT INTO "public"."project_purchases" VALUES (2788, 'PROJ_040', '西安人社局信息化建设项目', 'UPS电源', 5, 3789.16, 74627.63, '王强', '高静', '4年', '2024-03-26', '待发货');
INSERT INTO "public"."project_purchases" VALUES (2789, 'PROJ_041', '济南卫健委信息化建设项目', 'UPS电源', 10, 7031.90, 20242.26, '李丽', '高静', '5年', '2024-04-27', '已取消');
INSERT INTO "public"."project_purchases" VALUES (2790, 'PROJ_041', '济南卫健委信息化建设项目', 'UPS电源', 10, 2210.08, 2326.32, '周敏', '高静', '4年', '2024-04-20', '待发货');
INSERT INTO "public"."project_purchases" VALUES (2791, 'PROJ_041', '济南卫健委信息化建设项目', 'UPS电源', 4, 8838.74, 9356.88, '李丽', '高静', '3年', '2024-08-05', '已入库');
INSERT INTO "public"."project_purchases" VALUES (2792, 'PROJ_044', '北京人社局信息化建设项目', 'UPS电源', 4, 6174.40, 8830.60, '周敏', '高静', '5年', '2024-02-24', '已取消');
INSERT INTO "public"."project_purchases" VALUES (2793, 'PROJ_045', '上海财政局信息化建设项目', 'UPS电源', 7, 1370.00, 61221.66, '陈明', '高静', '2年', '2024-12-20', '已取消');
INSERT INTO "public"."project_purchases" VALUES (2794, 'PROJ_045', '上海财政局信息化建设项目', 'UPS电源', 4, 2895.55, 14424.62, '周敏', '高静', '5年', '2024-02-07', '已取消');
INSERT INTO "public"."project_purchases" VALUES (2795, 'PROJ_049', '深圳卫健委信息化建设项目', 'UPS电源', 9, 2016.97, 45466.75, '周敏', '高静', '1年', '2024-07-11', '运输中');
INSERT INTO "public"."project_purchases" VALUES (2796, 'PROJ_049', '深圳卫健委信息化建设项目', 'UPS电源', 3, 6209.53, 44988.60, '赵刚', '高静', '4年', '2024-12-03', '已入库');
INSERT INTO "public"."project_purchases" VALUES (2797, 'PROJ_049', '深圳卫健委信息化建设项目', 'UPS电源', 10, 4103.85, 56732.08, '赵刚', '高静', '5年', '2024-11-06', '运输中');
INSERT INTO "public"."project_purchases" VALUES (2798, 'PROJ_052', '北京卫健委信息化建设项目', 'UPS电源', 2, 783.06, 28670.28, '陈明', '高静', '2年', '2024-03-08', '已入库');
INSERT INTO "public"."project_purchases" VALUES (2799, 'PROJ_052', '北京卫健委信息化建设项目', 'UPS电源', 6, 2486.73, 24696.60, '周敏', '高静', '4年', '2024-05-08', '待发货');
INSERT INTO "public"."project_purchases" VALUES (2800, 'PROJ_053', '济南财政局信息化建设项目', 'UPS电源', 6, 2307.80, 27503.85, '王强', '高静', '1年', '2024-09-12', '已取消');
INSERT INTO "public"."project_purchases" VALUES (2801, 'PROJ_055', '遵义卫健委信息化建设项目', 'UPS电源', 3, 6806.22, 1775.52, '陈明', '高静', '1年', '2024-07-19', '已入库');
INSERT INTO "public"."project_purchases" VALUES (2802, 'PROJ_056', '武汉财政局信息化建设项目', 'UPS电源', 8, 1646.67, 9835.68, '周敏', '高静', '3年', '2024-09-10', '运输中');
INSERT INTO "public"."project_purchases" VALUES (2803, 'PROJ_056', '武汉财政局信息化建设项目', 'UPS电源', 1, 1591.90, 23625.25, '周敏', '高静', '1年', '2024-11-04', '已取消');
INSERT INTO "public"."project_purchases" VALUES (2804, 'PROJ_067', '重庆人社局信息化建设项目', 'UPS电源', 3, 1695.48, 14916.57, '王强', '高静', '1年', '2024-11-01', '已取消');
INSERT INTO "public"."project_purchases" VALUES (2805, 'PROJ_069', '广州卫健委信息化建设项目', 'UPS电源', 5, 1871.10, 2794.73, '陈明', '高静', '1年', '2024-07-30', '已入库');
INSERT INTO "public"."project_purchases" VALUES (2806, 'PROJ_069', '广州卫健委信息化建设项目', 'UPS电源', 4, 1034.57, 58772.58, '王强', '高静', '4年', '2024-05-09', '运输中');
INSERT INTO "public"."project_purchases" VALUES (2807, 'PROJ_073', '遵义公安局信息化建设项目', 'UPS电源', 8, 9963.74, 77933.40, '周敏', '高静', '1年', '2024-02-05', '已入库');
INSERT INTO "public"."project_purchases" VALUES (2808, 'PROJ_073', '遵义公安局信息化建设项目', 'UPS电源', 5, 8680.49, 102186.30, '周敏', '高静', '1年', '2024-01-05', '已入库');
INSERT INTO "public"."project_purchases" VALUES (2809, 'PROJ_077', '成都人社局信息化建设项目', 'UPS电源', 2, 743.28, 62131.38, '赵刚', '高静', '2年', '2024-11-16', '已取消');
INSERT INTO "public"."project_purchases" VALUES (2810, 'PROJ_077', '成都人社局信息化建设项目', 'UPS电源', 3, 10454.37, 68624.22, '李丽', '高静', '3年', '2024-09-30', '已入库');
INSERT INTO "public"."project_purchases" VALUES (2811, 'PROJ_077', '成都人社局信息化建设项目', 'UPS电源', 8, 4859.85, 50350.32, '王强', '高静', '2年', '2024-12-10', '待发货');
INSERT INTO "public"."project_purchases" VALUES (2812, 'PROJ_078', '西安财政局信息化建设项目', 'UPS电源', 1, 3070.32, 62694.30, '陈明', '高静', '4年', '2024-08-04', '运输中');
INSERT INTO "public"."project_purchases" VALUES (2813, 'PROJ_078', '西安财政局信息化建设项目', 'UPS电源', 2, 8820.45, 78714.00, '李丽', '高静', '5年', '2024-04-01', '已取消');
INSERT INTO "public"."project_purchases" VALUES (2814, 'PROJ_079', '西安住建局信息化建设项目', 'UPS电源', 4, 6651.27, 28738.60, '周敏', '高静', '3年', '2024-04-30', '待发货');
INSERT INTO "public"."project_purchases" VALUES (2815, 'PROJ_079', '西安住建局信息化建设项目', 'UPS电源', 11, 6571.44, 15741.40, '周敏', '高静', '1年', '2024-10-08', '待发货');
INSERT INTO "public"."project_purchases" VALUES (2816, 'PROJ_079', '西安住建局信息化建设项目', 'UPS电源', 1, 2738.01, 23639.85, '王强', '高静', '4年', '2024-05-12', '运输中');
INSERT INTO "public"."project_purchases" VALUES (2817, 'PROJ_081', '重庆卫健委信息化建设项目', 'UPS电源', 11, 4911.66, 43754.22, '赵刚', '高静', '2年', '2024-12-30', '运输中');
INSERT INTO "public"."project_purchases" VALUES (2818, 'PROJ_081', '重庆卫健委信息化建设项目', 'UPS电源', 3, 4894.32, 39954.40, '周敏', '高静', '5年', '2024-01-27', '已入库');
INSERT INTO "public"."project_purchases" VALUES (2819, 'PROJ_081', '重庆卫健委信息化建设项目', 'UPS电源', 7, 1397.52, 24790.25, '李丽', '高静', '1年', '2024-01-31', '已取消');
INSERT INTO "public"."project_purchases" VALUES (2820, 'PROJ_083', '重庆教育局信息化建设项目', 'UPS电源', 8, 7524.18, 6709.76, '李丽', '高静', '5年', '2024-08-20', '已入库');
INSERT INTO "public"."project_purchases" VALUES (2821, 'PROJ_084', '成都财政局信息化建设项目', 'UPS电源', 9, 8504.43, 11209.32, '李丽', '高静', '2年', '2024-08-09', '已取消');
INSERT INTO "public"."project_purchases" VALUES (2822, 'PROJ_084', '成都财政局信息化建设项目', 'UPS电源', 9, 9184.78, 4364.18, '李丽', '高静', '5年', '2024-06-11', '待发货');
INSERT INTO "public"."project_purchases" VALUES (2823, 'PROJ_085', '成都公安局信息化建设项目', 'UPS电源', 9, 5796.75, 53850.33, '周敏', '高静', '5年', '2024-05-07', '已取消');
INSERT INTO "public"."project_purchases" VALUES (2824, 'PROJ_085', '成都公安局信息化建设项目', 'UPS电源', 11, 4122.52, 87884.46, '李丽', '高静', '2年', '2024-08-19', '已取消');
INSERT INTO "public"."project_purchases" VALUES (2825, 'PROJ_092', '遵义住建局信息化建设项目', 'UPS电源', 6, 2906.96, 23960.05, '周敏', '高静', '1年', '2024-07-01', '已入库');
INSERT INTO "public"."project_purchases" VALUES (2826, 'PROJ_092', '遵义住建局信息化建设项目', 'UPS电源', 2, 8153.42, 17930.94, '王强', '高静', '4年', '2024-01-17', '已入库');
INSERT INTO "public"."project_purchases" VALUES (2827, 'PROJ_092', '遵义住建局信息化建设项目', 'UPS电源', 5, 8143.23, 78087.33, '周敏', '高静', '4年', '2024-11-11', '已入库');
INSERT INTO "public"."project_purchases" VALUES (2828, 'PROJ_094', '深圳教育局信息化建设项目', 'UPS电源', 10, 4209.52, 68194.00, '周敏', '高静', '3年', '2024-03-10', '运输中');
INSERT INTO "public"."project_purchases" VALUES (2829, 'PROJ_096', '上海卫健委信息化建设项目', 'UPS电源', 5, 8584.20, 8334.40, '赵刚', '高静', '1年', '2024-02-28', '运输中');
INSERT INTO "public"."project_purchases" VALUES (2830, 'PROJ_100', '杭州住建局信息化建设项目', 'UPS电源', 10, 8981.04, 14506.20, '陈明', '高静', '4年', '2024-02-08', '运输中');
INSERT INTO "public"."project_purchases" VALUES (2831, 'PROJ_102', '西安教育局信息化建设项目', 'UPS电源', 9, 10455.46, 42554.60, '李丽', '高静', '4年', '2024-03-08', '已入库');
INSERT INTO "public"."project_purchases" VALUES (2832, 'PROJ_102', '西安教育局信息化建设项目', 'UPS电源', 3, 8115.33, 59306.70, '周敏', '高静', '2年', '2024-06-23', '运输中');
INSERT INTO "public"."project_purchases" VALUES (2833, 'PROJ_107', '贵阳财政局信息化建设项目', 'UPS电源', 4, 6777.56, 5453.52, '王强', '高静', '5年', '2024-11-19', '待发货');
INSERT INTO "public"."project_purchases" VALUES (2834, 'PROJ_107', '贵阳财政局信息化建设项目', 'UPS电源', 6, 7457.75, 17955.06, '周敏', '高静', '2年', '2024-04-06', '已取消');
INSERT INTO "public"."project_purchases" VALUES (2835, 'PROJ_108', '遵义财政局信息化建设项目', 'UPS电源', 6, 4961.34, 3574.80, '周敏', '高静', '1年', '2024-07-07', '已入库');
INSERT INTO "public"."project_purchases" VALUES (2836, 'PROJ_119', '济南公安局信息化建设项目', 'UPS电源', 9, 2114.81, 62512.20, '李丽', '高静', '4年', '2024-06-01', '运输中');
INSERT INTO "public"."project_purchases" VALUES (2837, 'PROJ_120', '广州教育局信息化建设项目', 'UPS电源', 2, 6256.11, 3763.17, '陈明', '高静', '4年', '2024-04-13', '已入库');
INSERT INTO "public"."project_purchases" VALUES (2838, 'PROJ_120', '广州教育局信息化建设项目', 'UPS电源', 6, 2128.57, 21427.12, '王强', '高静', '3年', '2024-07-07', '已取消');
INSERT INTO "public"."project_purchases" VALUES (2839, 'PROJ_120', '广州教育局信息化建设项目', 'UPS电源', 1, 10253.71, 15951.51, '王强', '高静', '1年', '2024-06-27', '待发货');

-- ----------------------------
-- Table structure for sys_dictionaries
-- ----------------------------
DROP TABLE IF EXISTS "public"."sys_dictionaries";
CREATE TABLE "public"."sys_dictionaries" (
  "id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "name" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "type" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default",
  "created_at" timestamp(6) NOT NULL,
  "updated_at" timestamp(6) NOT NULL
)
;

-- ----------------------------
-- Records of sys_dictionaries
-- ----------------------------

-- ----------------------------
-- Table structure for sys_dictionary_items
-- ----------------------------
DROP TABLE IF EXISTS "public"."sys_dictionary_items";
CREATE TABLE "public"."sys_dictionary_items" (
  "id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "dictionary_id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "key" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "value" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "label" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "sort" int4 NOT NULL,
  "is_active" bool NOT NULL,
  "created_at" timestamp(6) NOT NULL,
  "updated_at" timestamp(6) NOT NULL
)
;

-- ----------------------------
-- Records of sys_dictionary_items
-- ----------------------------

-- ----------------------------
-- Table structure for sys_menus
-- ----------------------------
DROP TABLE IF EXISTS "public"."sys_menus";
CREATE TABLE "public"."sys_menus" (
  "id" varchar COLLATE "pg_catalog"."default" NOT NULL,
  "parent_id" varchar COLLATE "pg_catalog"."default",
  "sort" int4 NOT NULL,
  "name" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "code" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "path" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "icon" varchar(100) COLLATE "pg_catalog"."default",
  "is_active" bool NOT NULL,
  "created_at" timestamp(6) NOT NULL,
  "updated_at" timestamp(6) NOT NULL
)
;

-- ----------------------------
-- Records of sys_menus
-- ----------------------------

-- ----------------------------
-- Table structure for sys_permissions
-- ----------------------------
DROP TABLE IF EXISTS "public"."sys_permissions";
CREATE TABLE "public"."sys_permissions" (
  "id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "name" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "code" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default",
  "menu_id" varchar(36) COLLATE "pg_catalog"."default",
  "created_at" timestamp(6) NOT NULL,
  "updated_at" timestamp(6) NOT NULL
)
;

-- ----------------------------
-- Records of sys_permissions
-- ----------------------------

-- ----------------------------
-- Table structure for sys_role_permissions
-- ----------------------------
DROP TABLE IF EXISTS "public"."sys_role_permissions";
CREATE TABLE "public"."sys_role_permissions" (
  "role_id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "permission_id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "created_at" timestamp(6) NOT NULL
)
;

-- ----------------------------
-- Records of sys_role_permissions
-- ----------------------------

-- ----------------------------
-- Table structure for sys_roles
-- ----------------------------
DROP TABLE IF EXISTS "public"."sys_roles";
CREATE TABLE "public"."sys_roles" (
  "id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "name" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "code" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default",
  "created_at" timestamp(6) NOT NULL,
  "updated_at" timestamp(6) NOT NULL
)
;

-- ----------------------------
-- Records of sys_roles
-- ----------------------------

-- ----------------------------
-- Table structure for sys_users
-- ----------------------------
DROP TABLE IF EXISTS "public"."sys_users";
CREATE TABLE "public"."sys_users" (
  "id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "username" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "email" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "hashed_password" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "is_active" bool NOT NULL,
  "role" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "role_id" varchar(36) COLLATE "pg_catalog"."default",
  "is_deleted" bool NOT NULL,
  "created_at" timestamp(6) NOT NULL
)
;

-- ----------------------------
-- Records of sys_users
-- ----------------------------

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."kb_evaluations_id_seq"
OWNED BY "public"."kb_evaluations"."id";
SELECT setval('"public"."kb_evaluations_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."project_purchases_id_seq"
OWNED BY "public"."project_purchases"."id";
SELECT setval('"public"."project_purchases_id_seq"', 2839, true);

-- ----------------------------
-- Indexes structure for table api_authorizations
-- ----------------------------
CREATE UNIQUE INDEX "ix_api_authorizations_auth_code" ON "public"."api_authorizations" USING btree (
  "auth_code" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "ix_api_authorizations_vendor_name" ON "public"."api_authorizations" USING btree (
  "vendor_name" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table api_authorizations
-- ----------------------------
ALTER TABLE "public"."api_authorizations" ADD CONSTRAINT "api_authorizations_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table api_logs
-- ----------------------------
CREATE INDEX "ix_api_logs_auth_code" ON "public"."api_logs" USING btree (
  "auth_code" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "ix_api_logs_created_at" ON "public"."api_logs" USING btree (
  "created_at" "pg_catalog"."timestamp_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table api_logs
-- ----------------------------
ALTER TABLE "public"."api_logs" ADD CONSTRAINT "api_logs_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table chat_conversations
-- ----------------------------
CREATE INDEX "ix_chat_conversations_is_deleted" ON "public"."chat_conversations" USING btree (
  "is_deleted" "pg_catalog"."bool_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table chat_conversations
-- ----------------------------
ALTER TABLE "public"."chat_conversations" ADD CONSTRAINT "chat_conversations_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table chat_feedbacks
-- ----------------------------
CREATE INDEX "ix_chat_feedbacks_is_deleted" ON "public"."chat_feedbacks" USING btree (
  "is_deleted" "pg_catalog"."bool_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table chat_feedbacks
-- ----------------------------
ALTER TABLE "public"."chat_feedbacks" ADD CONSTRAINT "chat_feedbacks_message_id_key" UNIQUE ("message_id");

-- ----------------------------
-- Primary Key structure for table chat_feedbacks
-- ----------------------------
ALTER TABLE "public"."chat_feedbacks" ADD CONSTRAINT "chat_feedbacks_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table chat_logs
-- ----------------------------
CREATE INDEX "ix_chat_logs_created_at" ON "public"."chat_logs" USING btree (
  "created_at" "pg_catalog"."timestamp_ops" ASC NULLS LAST
);
CREATE INDEX "ix_chat_logs_is_deleted" ON "public"."chat_logs" USING btree (
  "is_deleted" "pg_catalog"."bool_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table chat_logs
-- ----------------------------
ALTER TABLE "public"."chat_logs" ADD CONSTRAINT "chat_logs_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table chat_messages
-- ----------------------------
CREATE INDEX "ix_chat_messages_is_deleted" ON "public"."chat_messages" USING btree (
  "is_deleted" "pg_catalog"."bool_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table chat_messages
-- ----------------------------
ALTER TABLE "public"."chat_messages" ADD CONSTRAINT "chat_messages_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table kb_document_chunks
-- ----------------------------
CREATE INDEX "ix_kb_document_chunks_is_deleted" ON "public"."kb_document_chunks" USING btree (
  "is_deleted" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "ix_kb_document_chunks_kb_id" ON "public"."kb_document_chunks" USING btree (
  "kb_id" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table kb_document_chunks
-- ----------------------------
ALTER TABLE "public"."kb_document_chunks" ADD CONSTRAINT "kb_document_chunks_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table kb_document_roles
-- ----------------------------
CREATE INDEX "ix_kb_document_roles_is_deleted" ON "public"."kb_document_roles" USING btree (
  "is_deleted" "pg_catalog"."bool_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table kb_document_roles
-- ----------------------------
ALTER TABLE "public"."kb_document_roles" ADD CONSTRAINT "kb_document_roles_pkey" PRIMARY KEY ("doc_id", "role_id");

-- ----------------------------
-- Indexes structure for table kb_documents
-- ----------------------------
CREATE INDEX "ix_kb_documents_is_deleted" ON "public"."kb_documents" USING btree (
  "is_deleted" "pg_catalog"."bool_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table kb_documents
-- ----------------------------
ALTER TABLE "public"."kb_documents" ADD CONSTRAINT "kb_documents_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table kb_domains
-- ----------------------------
CREATE INDEX "ix_kb_domains_is_deleted" ON "public"."kb_domains" USING btree (
  "is_deleted" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE UNIQUE INDEX "ix_kb_domains_name" ON "public"."kb_domains" USING btree (
  "name" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table kb_domains
-- ----------------------------
ALTER TABLE "public"."kb_domains" ADD CONSTRAINT "kb_domains_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table kb_evaluations
-- ----------------------------
CREATE INDEX "ix_kb_evaluations_is_deleted" ON "public"."kb_evaluations" USING btree (
  "is_deleted" "pg_catalog"."bool_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table kb_evaluations
-- ----------------------------
ALTER TABLE "public"."kb_evaluations" ADD CONSTRAINT "kb_evaluations_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table kb_knowledge_base_authorization_association
-- ----------------------------
ALTER TABLE "public"."kb_knowledge_base_authorization_association" ADD CONSTRAINT "kb_knowledge_base_authorization_association_pkey" PRIMARY KEY ("authorization_id", "knowledge_base_id");

-- ----------------------------
-- Primary Key structure for table kb_knowledge_base_domain_association
-- ----------------------------
ALTER TABLE "public"."kb_knowledge_base_domain_association" ADD CONSTRAINT "kb_knowledge_base_domain_association_pkey" PRIMARY KEY ("knowledge_base_id", "domain_id");

-- ----------------------------
-- Indexes structure for table kb_knowledge_base_roles
-- ----------------------------
CREATE INDEX "ix_kb_knowledge_base_roles_is_deleted" ON "public"."kb_knowledge_base_roles" USING btree (
  "is_deleted" "pg_catalog"."bool_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table kb_knowledge_base_roles
-- ----------------------------
ALTER TABLE "public"."kb_knowledge_base_roles" ADD CONSTRAINT "kb_knowledge_base_roles_pkey" PRIMARY KEY ("kb_id", "role_id");

-- ----------------------------
-- Primary Key structure for table kb_knowledge_base_tag_association
-- ----------------------------
ALTER TABLE "public"."kb_knowledge_base_tag_association" ADD CONSTRAINT "kb_knowledge_base_tag_association_pkey" PRIMARY KEY ("knowledge_base_id", "tag_id");

-- ----------------------------
-- Indexes structure for table kb_knowledge_bases
-- ----------------------------
CREATE INDEX "ix_kb_knowledge_bases_is_deleted" ON "public"."kb_knowledge_bases" USING btree (
  "is_deleted" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "ix_kb_knowledge_bases_name" ON "public"."kb_knowledge_bases" USING btree (
  "name" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table kb_knowledge_bases
-- ----------------------------
ALTER TABLE "public"."kb_knowledge_bases" ADD CONSTRAINT "kb_knowledge_bases_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table kb_tags
-- ----------------------------
CREATE INDEX "ix_kb_tags_is_deleted" ON "public"."kb_tags" USING btree (
  "is_deleted" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE UNIQUE INDEX "ix_kb_tags_name" ON "public"."kb_tags" USING btree (
  "name" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table kb_tags
-- ----------------------------
ALTER TABLE "public"."kb_tags" ADD CONSTRAINT "kb_tags_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table m_model_vendors
-- ----------------------------
CREATE INDEX "ix_m_model_vendors_id" ON "public"."m_model_vendors" USING btree (
  "id" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "ix_m_model_vendors_is_deleted" ON "public"."m_model_vendors" USING btree (
  "is_deleted" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE UNIQUE INDEX "ix_m_model_vendors_name" ON "public"."m_model_vendors" USING btree (
  "name" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table m_model_vendors
-- ----------------------------
ALTER TABLE "public"."m_model_vendors" ADD CONSTRAINT "m_model_vendors_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table m_models
-- ----------------------------
CREATE INDEX "ix_m_models_id" ON "public"."m_models" USING btree (
  "id" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "ix_m_models_is_active" ON "public"."m_models" USING btree (
  "is_active" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "ix_m_models_is_default" ON "public"."m_models" USING btree (
  "is_default" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "ix_m_models_is_deleted" ON "public"."m_models" USING btree (
  "is_deleted" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "ix_m_models_model" ON "public"."m_models" USING btree (
  "model" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "ix_m_models_name" ON "public"."m_models" USING btree (
  "name" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "ix_m_models_type" ON "public"."m_models" USING btree (
  "type" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "ix_m_models_vendor_id" ON "public"."m_models" USING btree (
  "vendor_id" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table m_models
-- ----------------------------
ALTER TABLE "public"."m_models" ADD CONSTRAINT "m_models_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table project_info
-- ----------------------------
ALTER TABLE "public"."project_info" ADD CONSTRAINT "project_info_pkey" PRIMARY KEY ("project_code");

-- ----------------------------
-- Primary Key structure for table project_purchases
-- ----------------------------
ALTER TABLE "public"."project_purchases" ADD CONSTRAINT "project_purchases_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Uniques structure for table sys_dictionaries
-- ----------------------------
ALTER TABLE "public"."sys_dictionaries" ADD CONSTRAINT "sys_dictionaries_type_key" UNIQUE ("type");

-- ----------------------------
-- Primary Key structure for table sys_dictionaries
-- ----------------------------
ALTER TABLE "public"."sys_dictionaries" ADD CONSTRAINT "sys_dictionaries_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table sys_dictionary_items
-- ----------------------------
ALTER TABLE "public"."sys_dictionary_items" ADD CONSTRAINT "sys_dictionary_items_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table sys_menus
-- ----------------------------
ALTER TABLE "public"."sys_menus" ADD CONSTRAINT "sys_menus_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Uniques structure for table sys_permissions
-- ----------------------------
ALTER TABLE "public"."sys_permissions" ADD CONSTRAINT "sys_permissions_code_key" UNIQUE ("code");

-- ----------------------------
-- Primary Key structure for table sys_permissions
-- ----------------------------
ALTER TABLE "public"."sys_permissions" ADD CONSTRAINT "sys_permissions_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table sys_role_permissions
-- ----------------------------
ALTER TABLE "public"."sys_role_permissions" ADD CONSTRAINT "sys_role_permissions_pkey" PRIMARY KEY ("role_id", "permission_id");

-- ----------------------------
-- Uniques structure for table sys_roles
-- ----------------------------
ALTER TABLE "public"."sys_roles" ADD CONSTRAINT "sys_roles_name_key" UNIQUE ("name");
ALTER TABLE "public"."sys_roles" ADD CONSTRAINT "sys_roles_code_key" UNIQUE ("code");

-- ----------------------------
-- Primary Key structure for table sys_roles
-- ----------------------------
ALTER TABLE "public"."sys_roles" ADD CONSTRAINT "sys_roles_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table sys_users
-- ----------------------------
CREATE UNIQUE INDEX "ix_sys_users_email" ON "public"."sys_users" USING btree (
  "email" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "ix_sys_users_is_deleted" ON "public"."sys_users" USING btree (
  "is_deleted" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE UNIQUE INDEX "ix_sys_users_username" ON "public"."sys_users" USING btree (
  "username" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table sys_users
-- ----------------------------
ALTER TABLE "public"."sys_users" ADD CONSTRAINT "sys_users_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Foreign Keys structure for table chat_conversations
-- ----------------------------
ALTER TABLE "public"."chat_conversations" ADD CONSTRAINT "chat_conversations_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."sys_users" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table chat_feedbacks
-- ----------------------------
ALTER TABLE "public"."chat_feedbacks" ADD CONSTRAINT "chat_feedbacks_message_id_fkey" FOREIGN KEY ("message_id") REFERENCES "public"."chat_messages" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table chat_logs
-- ----------------------------
ALTER TABLE "public"."chat_logs" ADD CONSTRAINT "chat_logs_conversation_id_fkey" FOREIGN KEY ("conversation_id") REFERENCES "public"."chat_conversations" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "public"."chat_logs" ADD CONSTRAINT "chat_logs_message_id_fkey" FOREIGN KEY ("message_id") REFERENCES "public"."chat_messages" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "public"."chat_logs" ADD CONSTRAINT "chat_logs_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."sys_users" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table chat_messages
-- ----------------------------
ALTER TABLE "public"."chat_messages" ADD CONSTRAINT "chat_messages_conversation_id_fkey" FOREIGN KEY ("conversation_id") REFERENCES "public"."chat_conversations" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table kb_document_chunks
-- ----------------------------
ALTER TABLE "public"."kb_document_chunks" ADD CONSTRAINT "kb_document_chunks_doc_id_fkey" FOREIGN KEY ("doc_id") REFERENCES "public"."kb_documents" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table kb_document_roles
-- ----------------------------
ALTER TABLE "public"."kb_document_roles" ADD CONSTRAINT "kb_document_roles_doc_id_fkey" FOREIGN KEY ("doc_id") REFERENCES "public"."kb_documents" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "public"."kb_document_roles" ADD CONSTRAINT "kb_document_roles_role_id_fkey" FOREIGN KEY ("role_id") REFERENCES "public"."sys_roles" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table kb_documents
-- ----------------------------
ALTER TABLE "public"."kb_documents" ADD CONSTRAINT "kb_documents_kb_id_fkey" FOREIGN KEY ("kb_id") REFERENCES "public"."kb_knowledge_bases" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table kb_knowledge_base_authorization_association
-- ----------------------------
ALTER TABLE "public"."kb_knowledge_base_authorization_association" ADD CONSTRAINT "kb_knowledge_base_authorization_associat_knowledge_base_id_fkey" FOREIGN KEY ("knowledge_base_id") REFERENCES "public"."kb_knowledge_bases" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "public"."kb_knowledge_base_authorization_association" ADD CONSTRAINT "kb_knowledge_base_authorization_associati_authorization_id_fkey" FOREIGN KEY ("authorization_id") REFERENCES "public"."api_authorizations" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table kb_knowledge_base_domain_association
-- ----------------------------
ALTER TABLE "public"."kb_knowledge_base_domain_association" ADD CONSTRAINT "kb_knowledge_base_domain_association_domain_id_fkey" FOREIGN KEY ("domain_id") REFERENCES "public"."kb_domains" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "public"."kb_knowledge_base_domain_association" ADD CONSTRAINT "kb_knowledge_base_domain_association_knowledge_base_id_fkey" FOREIGN KEY ("knowledge_base_id") REFERENCES "public"."kb_knowledge_bases" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table kb_knowledge_base_roles
-- ----------------------------
ALTER TABLE "public"."kb_knowledge_base_roles" ADD CONSTRAINT "kb_knowledge_base_roles_kb_id_fkey" FOREIGN KEY ("kb_id") REFERENCES "public"."kb_knowledge_bases" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "public"."kb_knowledge_base_roles" ADD CONSTRAINT "kb_knowledge_base_roles_role_id_fkey" FOREIGN KEY ("role_id") REFERENCES "public"."sys_roles" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table kb_knowledge_base_tag_association
-- ----------------------------
ALTER TABLE "public"."kb_knowledge_base_tag_association" ADD CONSTRAINT "kb_knowledge_base_tag_association_knowledge_base_id_fkey" FOREIGN KEY ("knowledge_base_id") REFERENCES "public"."kb_knowledge_bases" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "public"."kb_knowledge_base_tag_association" ADD CONSTRAINT "kb_knowledge_base_tag_association_tag_id_fkey" FOREIGN KEY ("tag_id") REFERENCES "public"."kb_tags" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table kb_knowledge_bases
-- ----------------------------
ALTER TABLE "public"."kb_knowledge_bases" ADD CONSTRAINT "kb_knowledge_bases_embedding_model_id_fkey" FOREIGN KEY ("embedding_model_id") REFERENCES "public"."m_models" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "public"."kb_knowledge_bases" ADD CONSTRAINT "kb_knowledge_bases_owner_id_fkey" FOREIGN KEY ("owner_id") REFERENCES "public"."sys_users" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "public"."kb_knowledge_bases" ADD CONSTRAINT "kb_knowledge_bases_rerank_model_id_fkey" FOREIGN KEY ("rerank_model_id") REFERENCES "public"."m_models" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table m_models
-- ----------------------------
ALTER TABLE "public"."m_models" ADD CONSTRAINT "m_models_vendor_id_fkey" FOREIGN KEY ("vendor_id") REFERENCES "public"."m_model_vendors" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table sys_dictionary_items
-- ----------------------------
ALTER TABLE "public"."sys_dictionary_items" ADD CONSTRAINT "sys_dictionary_items_dictionary_id_fkey" FOREIGN KEY ("dictionary_id") REFERENCES "public"."sys_dictionaries" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table sys_menus
-- ----------------------------
ALTER TABLE "public"."sys_menus" ADD CONSTRAINT "sys_menus_parent_id_fkey" FOREIGN KEY ("parent_id") REFERENCES "public"."sys_menus" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table sys_permissions
-- ----------------------------
ALTER TABLE "public"."sys_permissions" ADD CONSTRAINT "sys_permissions_menu_id_fkey" FOREIGN KEY ("menu_id") REFERENCES "public"."sys_menus" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table sys_role_permissions
-- ----------------------------
ALTER TABLE "public"."sys_role_permissions" ADD CONSTRAINT "sys_role_permissions_permission_id_fkey" FOREIGN KEY ("permission_id") REFERENCES "public"."sys_permissions" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "public"."sys_role_permissions" ADD CONSTRAINT "sys_role_permissions_role_id_fkey" FOREIGN KEY ("role_id") REFERENCES "public"."sys_roles" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table sys_users
-- ----------------------------
ALTER TABLE "public"."sys_users" ADD CONSTRAINT "sys_users_role_id_fkey" FOREIGN KEY ("role_id") REFERENCES "public"."sys_roles" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;
