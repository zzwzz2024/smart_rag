/*
 Navicat Premium Dump SQL

 Source Server         : 本地postgres
 Source Server Type    : PostgreSQL
 Source Server Version : 170007 (170007)
 Source Host           : localhost:5432
 Source Catalog        : rag
 Source Schema         : public

 Target Server Type    : PostgreSQL
 Target Server Version : 170007 (170007)
 File Encoding         : 65001

 Date: 14/03/2026 14:50:32
*/


-- ----------------------------
-- Type structure for modeltype
-- ----------------------------
DROP TYPE IF EXISTS "public"."modeltype";
CREATE TYPE "public"."modeltype" AS ENUM (
  'embedding',
  'chat',
  'rerank'
);

-- ----------------------------
-- Sequence structure for evaluations_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."evaluations_id_seq";
CREATE SEQUENCE "public"."evaluations_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for knowledge_bases_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "public"."knowledge_bases_id_seq";
CREATE SEQUENCE "public"."knowledge_bases_id_seq" 
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
  "start_time" timestamptz(6) NOT NULL,
  "end_time" timestamptz(6) NOT NULL,
  "is_active" bool DEFAULT true,
  "created_at" timestamptz(6) DEFAULT now(),
  "updated_at" timestamptz(6) DEFAULT now()
)
;
COMMENT ON COLUMN "public"."api_authorizations"."id" IS 'ID';
COMMENT ON COLUMN "public"."api_authorizations"."vendor_name" IS '模型厂商名称';
COMMENT ON COLUMN "public"."api_authorizations"."vendor_contact" IS '供应商负责人';
COMMENT ON COLUMN "public"."api_authorizations"."contact_phone" IS '联系电话';
COMMENT ON COLUMN "public"."api_authorizations"."authorized_ips" IS '授权IP地址，逗号分隔';
COMMENT ON COLUMN "public"."api_authorizations"."auth_code" IS '授权码';
COMMENT ON COLUMN "public"."api_authorizations"."start_time" IS '授权开始时间';
COMMENT ON COLUMN "public"."api_authorizations"."end_time" IS '授权结束时间';
COMMENT ON COLUMN "public"."api_authorizations"."is_active" IS '是否激活';
COMMENT ON COLUMN "public"."api_authorizations"."created_at" IS '创建时间';
COMMENT ON COLUMN "public"."api_authorizations"."updated_at" IS '更新时间';

-- ----------------------------
-- Records of api_authorizations
-- ----------------------------
INSERT INTO "public"."api_authorizations" VALUES ('84d68e67-fcf9-4a0b-a91c-13bcc7e9822a', '1', '2', '3', '', '5alt95NVlOxEA2AWLDpXlZot1onVNMXz', '2026-02-18 21:23:07.002+08', '2026-02-21 14:13:44+08', 't', '2026-02-20 13:23:20.651642+08', '2026-02-20 22:27:05.068648+08');

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
  "created_at" timestamptz(6) DEFAULT now()
)
;
COMMENT ON COLUMN "public"."api_logs"."id" IS 'ID';
COMMENT ON COLUMN "public"."api_logs"."auth_code" IS '授权码';
COMMENT ON COLUMN "public"."api_logs"."endpoint" IS 'API 端点';
COMMENT ON COLUMN "public"."api_logs"."method" IS 'HTTP 方法';
COMMENT ON COLUMN "public"."api_logs"."ip" IS '请求 IP 地址';
COMMENT ON COLUMN "public"."api_logs"."user_agent" IS '用户代理';
COMMENT ON COLUMN "public"."api_logs"."status" IS '处理状态';
COMMENT ON COLUMN "public"."api_logs"."response_time" IS '响应时间';
COMMENT ON COLUMN "public"."api_logs"."error_message" IS '错误消息';
COMMENT ON COLUMN "public"."api_logs"."created_at" IS '创建时间';

-- ----------------------------
-- Records of api_logs
-- ----------------------------
INSERT INTO "public"."api_logs" VALUES ('20601c85-e157-4700-a00f-a70bd5eda5ea', '5alt95NVlOxEA2AWLDpXlZot1onVNMXz', '/api-auth/chat', 'POST', '127.0.0.1', NULL, 200, 2129890, NULL, '2026-02-21 06:07:22.701021+08');
INSERT INTO "public"."api_logs" VALUES ('3ccc4f0e-0033-4396-9dfd-f47c869d5fb8', '5alt95NVlOxEA2AWLDpXlZot1onVNMXz', '/api-auth/chat', 'POST', '127.0.0.1', NULL, 401, 7588, '授权无效或已过期', '2026-02-21 06:23:05.89577+08');
INSERT INTO "public"."api_logs" VALUES ('afe10a74-e564-4f14-bec9-ccb220a9e37e', '5alt95NVlOxEA2AWLDpXlZot1onVNMXz', '/api-auth/chat', 'POST', '127.0.0.1', NULL, 401, 1630, '授权无效或已过期', '2026-02-21 06:23:10.040247+08');

-- ----------------------------
-- Table structure for chat_conversations
-- ----------------------------
DROP TABLE IF EXISTS "public"."chat_conversations";
CREATE TABLE "public"."chat_conversations" (
  "id" varchar COLLATE "pg_catalog"."default" NOT NULL,
  "user_id" varchar COLLATE "pg_catalog"."default" NOT NULL,
  "kb_id" varchar COLLATE "pg_catalog"."default",
  "title" varchar COLLATE "pg_catalog"."default",
  "created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "pinned" bool,
  "is_deleted" bool DEFAULT false
)
;
COMMENT ON COLUMN "public"."chat_conversations"."id" IS 'ID';
COMMENT ON COLUMN "public"."chat_conversations"."user_id" IS '用户 ID';
COMMENT ON COLUMN "public"."chat_conversations"."kb_id" IS '知识库ID';
COMMENT ON COLUMN "public"."chat_conversations"."title" IS '对话标题';
COMMENT ON COLUMN "public"."chat_conversations"."created_at" IS '创建时间';
COMMENT ON COLUMN "public"."chat_conversations"."updated_at" IS '更新时间';
COMMENT ON COLUMN "public"."chat_conversations"."pinned" IS '是否置顶';
COMMENT ON COLUMN "public"."chat_conversations"."is_deleted" IS '创建时间';

-- ----------------------------
-- Records of chat_conversations
-- ----------------------------
INSERT INTO "public"."chat_conversations" VALUES ('89513a6c-68a1-4aef-a0e5-bc16bb1de524', '70b550f3-f81b-45cb-a92e-1dd8bb8292fc', '60b4d637-6acb-45e2-8217-07ddb5a79cf5', '蔡依林拿过几个金曲奖', '2026-03-13 15:20:21.987653', '2026-03-13 15:20:21.987653', 'f', 'f');
INSERT INTO "public"."chat_conversations" VALUES ('f3d63cbb-5402-404f-a7e8-059243cec2a0', '70b550f3-f81b-45cb-a92e-1dd8bb8292fc', NULL, '是是是', '2026-03-13 15:32:14.625503', '2026-03-13 15:38:04.586286', 'f', 't');

-- ----------------------------
-- Table structure for chat_feedbacks
-- ----------------------------
DROP TABLE IF EXISTS "public"."chat_feedbacks";
CREATE TABLE "public"."chat_feedbacks" (
  "id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "message_id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "rating" int4 NOT NULL,
  "comment" text COLLATE "pg_catalog"."default",
  "created_at" timestamp(6) NOT NULL,
  "is_deleted" bool DEFAULT false
)
;
COMMENT ON COLUMN "public"."chat_feedbacks"."id" IS 'ID';
COMMENT ON COLUMN "public"."chat_feedbacks"."message_id" IS '消息ID';
COMMENT ON COLUMN "public"."chat_feedbacks"."rating" IS '评分（1-3）';
COMMENT ON COLUMN "public"."chat_feedbacks"."comment" IS '评论，可选';
COMMENT ON COLUMN "public"."chat_feedbacks"."created_at" IS '创建时间';
COMMENT ON COLUMN "public"."chat_feedbacks"."is_deleted" IS '创建时间';

-- ----------------------------
-- Records of chat_feedbacks
-- ----------------------------

-- ----------------------------
-- Table structure for chat_logs
-- ----------------------------
DROP TABLE IF EXISTS "public"."chat_logs";
CREATE TABLE "public"."chat_logs" (
  "id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "user_id" varchar(36) COLLATE "pg_catalog"."default",
  "conversation_id" varchar(36) COLLATE "pg_catalog"."default",
  "message_id" varchar(36) COLLATE "pg_catalog"."default",
  "query" text COLLATE "pg_catalog"."default" NOT NULL,
  "answer" text COLLATE "pg_catalog"."default" NOT NULL,
  "model_used" varchar(100) COLLATE "pg_catalog"."default",
  "knowledge_bases" jsonb,
  "response_time" float8,
  "created_at" timestamptz(6) DEFAULT CURRENT_TIMESTAMP,
  "is_deleted" bool DEFAULT false
)
;
COMMENT ON COLUMN "public"."chat_logs"."id" IS 'ID';
COMMENT ON COLUMN "public"."chat_logs"."user_id" IS '用户 ID';
COMMENT ON COLUMN "public"."chat_logs"."conversation_id" IS '对话ID';
COMMENT ON COLUMN "public"."chat_logs"."message_id" IS '消息ID';
COMMENT ON COLUMN "public"."chat_logs"."query" IS '查询内容';
COMMENT ON COLUMN "public"."chat_logs"."answer" IS '回答内容';
COMMENT ON COLUMN "public"."chat_logs"."model_used" IS '使用的模型';
COMMENT ON COLUMN "public"."chat_logs"."knowledge_bases" IS '使用的知识库';
COMMENT ON COLUMN "public"."chat_logs"."response_time" IS '响应时间';
COMMENT ON COLUMN "public"."chat_logs"."created_at" IS '创建时间';
COMMENT ON COLUMN "public"."chat_logs"."is_deleted" IS '创建时间';

-- ----------------------------
-- Records of chat_logs
-- ----------------------------
INSERT INTO "public"."chat_logs" VALUES ('b3e199d0-7270-4713-b964-10799b31012a', '70b550f3-f81b-45cb-a92e-1dd8bb8292fc', '89513a6c-68a1-4aef-a0e5-bc16bb1de524', NULL, '蔡依林拿过几个金曲奖', '**蔡依林共获得5座金曲奖**。

1. **2019年**：第30届金曲奖年度专辑奖（《Ugly Beauty》）  
2. **2019年**：第30届金曲奖年度歌曲奖（《玫瑰少年》）  
3. **2015年**：第26届金曲奖最佳国语专辑奖（《呸》）  
4. **2015年**：第26届金曲奖最佳演唱录音专辑奖（《呸》）  
5. **2013年**：第24届金曲奖年度最佳歌曲奖（《大艺术家》）  
6. **2007年**：第18届金曲奖年度最佳歌曲奖（《今天你要嫁给我》）  
7. **2007年**：第18届金曲奖最佳国语女演唱人奖（《舞娘》）

其中，**明确获奖的金曲奖共7项**。', 'qwen3-max', '["60b4d637-6acb-45e2-8217-07ddb5a79cf5"]', 6.276639699935913, '2026-03-13 15:20:35.569577+08', 'f');
INSERT INTO "public"."chat_logs" VALUES ('57512420-baed-43d2-b56b-0ad7f514ce02', '70b550f3-f81b-45cb-a92e-1dd8bb8292fc', 'f3d63cbb-5402-404f-a7e8-059243cec2a0', NULL, '是是是', '根据提供的信息，未检索到相关内容。', 'qwen3-max', '[]', 0.8400468826293945, '2026-03-13 15:32:20.344043+08', 'f');
INSERT INTO "public"."chat_logs" VALUES ('3475267c-f3f7-4892-a370-9dc99699aa40', '70b550f3-f81b-45cb-a92e-1dd8bb8292fc', '89513a6c-68a1-4aef-a0e5-bc16bb1de524', NULL, '李宗盛拿过几次奖', '根据提供的信息，未检索到相关内容。', 'qwen3-max', '["60b4d637-6acb-45e2-8217-07ddb5a79cf5"]', 4.795404434204102, '2026-03-14 03:29:38.20365+08', 'f');
INSERT INTO "public"."chat_logs" VALUES ('b4e611b2-5489-4770-bae0-7309661fcba7', '70b550f3-f81b-45cb-a92e-1dd8bb8292fc', '89513a6c-68a1-4aef-a0e5-bc16bb1de524', NULL, '王力宏拿过金曲歌王吗', '**王力宏共获得2次金曲奖“最佳国语男演唱人奖”（即“金曲歌王”）**。

1. **2006年**：第17届台湾金曲奖最佳国语男演唱人奖（获奖作品：《盖世英雄》）  
2. **1999年**：第10届台湾金曲奖最佳国语男演唱人奖（获奖作品：《公转自转》）

其中，**明确获奖的金曲歌王奖项共2项**。', 'qwen3-max', '["60b4d637-6acb-45e2-8217-07ddb5a79cf5"]', 11.614129543304443, '2026-03-14 03:43:17.716527+08', 'f');

-- ----------------------------
-- Table structure for chat_messages
-- ----------------------------
DROP TABLE IF EXISTS "public"."chat_messages";
CREATE TABLE "public"."chat_messages" (
  "id" varchar(48) COLLATE "pg_catalog"."default" NOT NULL,
  "conversation_id" varchar(48) COLLATE "pg_catalog"."default" NOT NULL,
  "role" varchar(10) COLLATE "pg_catalog"."default" NOT NULL,
  "content" text COLLATE "pg_catalog"."default" NOT NULL,
  "citations" text COLLATE "pg_catalog"."default",
  "confidence" float8,
  "retrieval_info" varchar(255) COLLATE "pg_catalog"."default",
  "token_usage" varchar(255) COLLATE "pg_catalog"."default",
  "created_at" timestamp(6) NOT NULL,
  "suggested_questions" varchar(255) COLLATE "pg_catalog"."default",
  "is_deleted" bool DEFAULT false
)
;
COMMENT ON COLUMN "public"."chat_messages"."id" IS 'ID';
COMMENT ON COLUMN "public"."chat_messages"."conversation_id" IS '对话ID';
COMMENT ON COLUMN "public"."chat_messages"."role" IS '角色';
COMMENT ON COLUMN "public"."chat_messages"."content" IS '文本内容';
COMMENT ON COLUMN "public"."chat_messages"."citations" IS '引用';
COMMENT ON COLUMN "public"."chat_messages"."confidence" IS '置信度';
COMMENT ON COLUMN "public"."chat_messages"."retrieval_info" IS '检索信息';
COMMENT ON COLUMN "public"."chat_messages"."token_usage" IS 'token使用情况，可选';
COMMENT ON COLUMN "public"."chat_messages"."created_at" IS '创建时间';
COMMENT ON COLUMN "public"."chat_messages"."is_deleted" IS '创建时间';

-- ----------------------------
-- Records of chat_messages
-- ----------------------------
INSERT INTO "public"."chat_messages" VALUES ('a589ea17-4b57-4f2a-9ec2-7c28d7f0c58d', '99f397ec-25c0-4456-a2c5-c0c61cc7b7f0', 'user', '啊', NULL, NULL, NULL, NULL, '2026-02-10 08:45:26.862219', NULL, 'f');
INSERT INTO "public"."chat_messages" VALUES ('672ebe71-d599-497f-ad8a-ac0987ddac49', '99f397ec-25c0-4456-a2c5-c0c61cc7b7f0', 'assistant', '抱歉，生成答案时出现错误，请稍后再试。', '[]', 0, NULL, '{"response_time": 1.6700975894927979}', '2026-02-10 08:45:28.578808', NULL, 'f');
INSERT INTO "public"."chat_messages" VALUES ('111ef4b1-1d50-4379-95d2-82df44aa08d9', '6e53a108-3e23-4b3c-9416-01e9fb740ee0', 'user', '大队', NULL, NULL, NULL, NULL, '2026-02-10 08:51:32.303485', NULL, 'f');
INSERT INTO "public"."chat_messages" VALUES ('757ac72e-740e-44f7-a586-d5f2cded98d7', '6e53a108-3e23-4b3c-9416-01e9fb740ee0', 'assistant', '抱歉，生成答案时出现错误，请稍后再试。', '[]', 0, NULL, '{"response_time": 8.221793413162231}', '2026-02-10 08:51:40.606786', NULL, 'f');
INSERT INTO "public"."chat_messages" VALUES ('53fd0097-342f-474d-9991-0fd0f1fd9deb', 'c1c81107-e14f-488b-9c00-71e28738f5ca', 'user', '啊', NULL, NULL, NULL, NULL, '2026-02-10 08:52:14.565118', NULL, 'f');
INSERT INTO "public"."chat_messages" VALUES ('fa62ee4e-8140-4189-a5f2-2a78c8a961ce', 'c1c81107-e14f-488b-9c00-71e28738f5ca', 'assistant', '抱歉，生成答案时出现错误，请稍后再试。', '[]', 0, NULL, '{"response_time": 1.9669647216796875}', '2026-02-10 08:52:16.602271', NULL, 'f');
INSERT INTO "public"."chat_messages" VALUES ('5a4f97c3-6bc3-4545-b1b7-9d3bc16329d6', 'c1c81107-e14f-488b-9c00-71e28738f5ca', 'user', '你好', NULL, NULL, NULL, NULL, '2026-02-10 08:52:23.815619', NULL, 'f');
INSERT INTO "public"."chat_messages" VALUES ('f1880603-b9da-4080-9b9f-e73b42d98b92', 'c1c81107-e14f-488b-9c00-71e28738f5ca', 'assistant', '抱歉，生成答案时出现错误，请稍后再试。', '[]', 0, NULL, '{"response_time": 1.2918357849121094}', '2026-02-10 08:52:25.142416', NULL, 'f');
INSERT INTO "public"."chat_messages" VALUES ('cf8a0068-6105-460c-8265-9a5bdc8868e7', '4e45e231-b513-4e40-a713-409a17094b96', 'user', '你好', NULL, NULL, NULL, NULL, '2026-02-10 08:56:24.047929', NULL, 'f');
INSERT INTO "public"."chat_messages" VALUES ('5a51cdab-01ea-4f48-9e79-f15a6941b9d9', '4e45e231-b513-4e40-a713-409a17094b96', 'assistant', '抱歉，生成答案时出现错误，请稍后再试。', '[]', 0, NULL, '{"response_time": 1.372351884841919}', '2026-02-10 08:56:25.494987', NULL, 'f');
INSERT INTO "public"."chat_messages" VALUES ('416157a8-73b1-4e46-b02b-336ebc2d51de', '4e45e231-b513-4e40-a713-409a17094b96', 'user', '我很好', NULL, NULL, NULL, NULL, '2026-02-10 08:56:55.050014', NULL, 'f');
INSERT INTO "public"."chat_messages" VALUES ('0494090d-0eef-4383-a3bd-b4a908d2b2c3', '4e45e231-b513-4e40-a713-409a17094b96', 'assistant', '很高兴听到你很好！如果你有任何问题或需要帮助，随时告诉我。', '[]', 0.3, NULL, '{"prompt": 112, "completion": 15, "total": 127, "response_time": 1.570603609085083}', '2026-02-10 08:56:56.69383', NULL, 'f');
INSERT INTO "public"."chat_messages" VALUES ('c36ecafe-e97e-4b5d-b15d-7d76b0994946', '4e45e231-b513-4e40-a713-409a17094b96', 'user', '周杰伦在文档中码', NULL, NULL, NULL, NULL, '2026-02-10 09:16:31.745125', NULL, 'f');
INSERT INTO "public"."chat_messages" VALUES ('669db8de-932a-4dd0-97d9-3be61e45eae0', '4e45e231-b513-4e40-a713-409a17094b96', 'assistant', '在您提供的信息中，并未包含任何文档内容，因此无法确认“周杰伦”是否出现在文档中。

如果您是指之前对话中提到的“参考信息”或某份具体文档，请提供该文档内容或更明确的上下文。目前系统提示：“如果参考信息中包含相关内容，请基于参考信息回答”，但当前并无参考信息可供检索。

请补充更多信息，以便我准确回答您的问题。', '[]', 0.3, NULL, '{"prompt": 149, "completion": 88, "total": 237, "response_time": 4.345095872879028}', '2026-02-10 09:16:36.13195', NULL, 'f');
INSERT INTO "public"."chat_messages" VALUES ('37b1e747-cffd-4da4-8785-4faf641f5fa8', 'a1161bab-9a1f-4af7-aa89-9b2243529883', 'user', '周杰伦在文档中吗', NULL, NULL, NULL, NULL, '2026-02-10 09:17:08.368061', NULL, 'f');
INSERT INTO "public"."chat_messages" VALUES ('cf019b6c-51a0-4c3c-a909-12f14d5d6f3e', 'a1161bab-9a1f-4af7-aa89-9b2243529883', 'assistant', '是的，周杰伦在文档中被提及。文档中多次提到周杰伦，例如：

- “周杰伦的歌迷横跨各个年龄层。”
- “周杰伦自2000年出道以来，便以其独特的音乐风格……”
- “周杰伦不仅是一位歌手，还是一位多才多艺的音乐制作人、演员和导演。”

这些内容表明文档对周杰伦的音乐成就、影响力及其多重身份进行了描述。', '[]', 0.3, NULL, '{"prompt": 100, "completion": 101, "total": 201, "response_time": 3.6354947090148926}', '2026-02-10 09:17:12.032568', NULL, 'f');
INSERT INTO "public"."chat_messages" VALUES ('95ad1d90-c60d-4b82-a955-cf54fcb311ac', 'a1161bab-9a1f-4af7-aa89-9b2243529883', 'user', '啊', NULL, NULL, NULL, NULL, '2026-02-10 09:27:30.742002', NULL, 'f');
INSERT INTO "public"."chat_messages" VALUES ('967497b7-2943-431f-b21e-e9bef3350ce1', 'a1161bab-9a1f-4af7-aa89-9b2243529883', 'assistant', '你好！你输入了“啊”，看起来可能是误操作，或者你想表达某种情绪。如果你有任何问题、需要帮助，或者想了解关于周杰伦或其他内容的信息，请随时告诉我！😊', '[]', 0.3, NULL, '{"prompt": 205, "completion": 41, "total": 246, "response_time": 2.2032222747802734}', '2026-02-10 09:27:32.976594', NULL, 'f');
INSERT INTO "public"."chat_messages" VALUES ('27bafe99-481b-45a8-ba56-e6dac2d68612', '89513a6c-68a1-4aef-a0e5-bc16bb1de524', 'user', '蔡依林拿过几个金曲奖', NULL, NULL, NULL, NULL, '2026-03-13 15:20:21.992474', NULL, 'f');
INSERT INTO "public"."chat_messages" VALUES ('bf2b40b5-11d9-41ca-b2b2-7f9d95033495', '89513a6c-68a1-4aef-a0e5-bc16bb1de524', 'assistant', '**蔡依林共获得5座金曲奖**。

1. **2019年**：第30届金曲奖年度专辑奖（《Ugly Beauty》）  
2. **2019年**：第30届金曲奖年度歌曲奖（《玫瑰少年》）  
3. **2015年**：第26届金曲奖最佳国语专辑奖（《呸》）  
4. **2015年**：第26届金曲奖最佳演唱录音专辑奖（《呸》）  
5. **2013年**：第24届金曲奖年度最佳歌曲奖（《大艺术家》）  
6. **2007年**：第18届金曲奖年度最佳歌曲奖（《今天你要嫁给我》）  
7. **2007年**：第18届金曲奖最佳国语女演唱人奖（《舞娘》）

其中，**明确获奖的金曲奖共7项**。', '[{"chunk_id": "e33d8c7a-3da7-4850-8a1f-d2c442ce514e", "content": "\u8521\u4f9d\u6797\u83b7\u5956\u60c5\u51b5\r\n\u97f3\u4e50\u7c7b\r\n\u83b7\u5956\u65f6\u95f4\t\u5956\u9879\u540d\u79f0\t\u83b7\u5956\u4f5c\u54c1\t\u83b7\u5956\u7ed3\u679c\r\n2025-8-24\t\u7b2c6\u5c4a\u817e\u8baf\u97f3\u4e50\u5a31\u4e50\u76db\u5178\u5e74\u5ea6\u5f71\u54cd\u529b\u6e2f\u53f0\u5973\u6b4c\u624b [246]\t\t\u83b7\u5956\r\n2024-8\t\u7b2c31\u5c4a\u4e1c\u65b9\u98ce\u4e91\u699c\u6e2f\u53f0\u5730\u533a\u6700\u4f73\u5973\u6b4c\u624b [225]\t\t\u83b7\u5956\r\n2024-5-16\t\u7b2c35\u5c4a\u91d1\u66f2\u5956\u6700\u4f73\u4f5c\u66f2\u4eba\u5956 [186]\tSomeday, Somewhere\t\u63d0\u540d\r\n2023-7\t2023TMEA\u817e\u8baf\u97f3\u4e50\u5a31\u4e50\u76db\u5178\u5e74\u5ea6\u8de8\u754c\u5408\u4f5c\u5355\u66f2 ", "score": 0.007}, {"chunk_id": "134794b7-2599-4f6d-a3aa-5e86cd011f78", "content": "\u5b59\u71d5\u59ff\u83b7\u5956\u60c5\u51b5\r\n\u83b7\u5956\u65f6\u95f4\t\u5956\u9879\u540d\u79f0\t\u83b7\u5956\u4f5c\u54c1\t\u83b7\u5956\u7ed3\u679c\r\n2015-5-15\t\u7b2c5\u5c4a\u5168\u7403\u6d41\u884c\u97f3\u4e50\u91d1\u699c\uff1a\u5e74\u5ea620\u5927\u91d1\u66f2\u5956 [133]\t\u300a\u514b\u535c\u52d2\u300b\t\u83b7\u5956\r\n2015-5-15\t\u7b2c5\u5c4a\u5168\u7403\u6d41\u884c\u97f3\u4e50\u91d1\u699c\uff1aUFM100.3\u70b9\u64ad\u51a0\u519b\u5956 [133]\t\u300a\u5c1a\u597d\u7684\u9752\u6625\u300b\t\u83b7\u5956\r\n2015-5-15\t\u7b2c5\u5c4a\u5168\u7403\u6d41\u884c\u97f3\u4e50\u91d1\u699c\uff1a\u5e74\u5ea6\u6700\u4f73\u5973\u6b4c\u624b\u5956 [133]\t\t\u83b7\u5956\r\n2014-11-7\t\u7b2c19\u5c4a\u65b0\u52a0\u5761\u91d1\u66f2\u5956\uff1a\u6700\u4f73\u4e13\u8f91\u5956 ", "score": 0.007}, {"chunk_id": "bef6761c-cc77-40eb-8e37-0752695b7f5e", "content": "Hebe\u83b7\u5956\u60c5\u51b5\r\n\u97f3\u4e50\u7c7b\r\n\u83b7\u5956\u65f6\u95f4\t\u5956\u9879\u540d\u79f0\t\u83b7\u5956\u4f5c\u54c1\t\u83b7\u5956\u7ed3\u679c\r\n2021-8-21\t\u7b2c32\u5c4a\u53f0\u6e7e\u91d1\u66f2\u5956\u6700\u4f73\u534e\u8bed\u5973\u6b4c\u624b\u5956 [89]\t\u65e0\u4eba\u77e5\u6653\t\u83b7\u5956\r\n2021-1-23\t\u7b2c\u4e8c\u5c4a\u817e\u8baf\u97f3\u4e50\u5a31\u4e50\u76db\u5178 \u5e74\u5ea6\u6700\u5177\u5f71\u54cd\u529b\u6e2f\u53f0\u5973\u6b4c\u624b [83]\t\t\u83b7\u5956\r\n2017-6-4\tFM\u6700\u7231\u6b4c\u624b\u3001HITO\u5973\u6b4c\u624b [62]\t\t\u83b7\u5956\r\nMusicRadio\u4e2d\u56fdTOP\u6392\u884c\u699c\r\n\u83b7\u5956\u65f6\u95f4\t\u5956\u9879\u540d\u79f0\t\u83b7\u5956\u4f5c\u54c1\t\u83b7\u5956\u7ed3\u679c\r\n20", "score": 0.007}]', 0.7263575163403572, NULL, '{"prompt": 11554, "completion": 226, "total": 11780, "response_time": 6.276639699935913}', '2026-03-13 15:20:35.566318', NULL, 'f');
INSERT INTO "public"."chat_messages" VALUES ('5f816cbc-1198-491c-809f-f8d7296723b0', '89513a6c-68a1-4aef-a0e5-bc16bb1de524', 'user', '李宗盛拿过几次奖', NULL, NULL, NULL, NULL, '2026-03-14 03:29:16.917009', NULL, 'f');
INSERT INTO "public"."chat_messages" VALUES ('1db50321-3d43-4b8d-857d-116a03ef5ba0', '89513a6c-68a1-4aef-a0e5-bc16bb1de524', 'assistant', '根据提供的信息，未检索到相关内容。', '[{"chunk_id": "5fb3efe5-b8a1-4c92-b8e8-1cbe051dc412", "content": "\u738b\u529b\u5b8f\u83b7\u5956\u60c5\u51b5\r\n\u97f3\u4e50\u7c7b\r\n\u83b7\u5956\u65f6\u95f4\t\u5956\u9879\u540d\u79f0\t\u83b7\u5956\u4f5c\u54c1\t\u83b7\u5956\u7ed3\u679c\r\n2019\t\u534e\u4eba\u6b4c\u66f2\u97f3\u4e50\u76db\u5178\u5e74\u5ea6\u6700\u4f73\u7537\u6b4c\u624b [172]\t\t\u83b7\u5956\r\n2019\t\u534e\u4eba\u6b4c\u66f2\u97f3\u4e50\u76db\u5178\u5e74\u5ea6\u91d1\u66f2\u5956 [170]\t\u661f\u5149\t\u83b7\u5956\r\n2019\t\u534e\u4eba\u6b4c\u66f2\u97f3\u4e50\u76db\u5178\u5e74\u5ea6\u516c\u76ca\u6b4c\u66f2\u5956 [171]\t\u661f\u5149\t\u83b7\u5956\r\n2019\t\u6d41\u884c\u97f3\u4e50\u5168\u91d1\u699c\u5e74\u5ea6\u6700\u53d7\u6b22\u8fce\u7537\u6b4c\u624b [185]\t\t\u83b7\u5956\r\n2019\t\u6d41\u884c\u97f3\u4e50\u5168\u91d1\u699c\u5e74\u5ea6\u542c\u4f17\u6700\u7231\u6f14\u5531\u4f1a [185]\t\t\u83b7\u5956\r\n2", "score": 0.024}, {"chunk_id": "31135770-9208-4ec4-b691-828b8cdbc3f5", "content": "\u6797\u4fca\u6770\u83b7\u5956\u8bb0\u5f55\r\n\u83b7\u5956\u65f6\u95f4\t\u5956\u9879\u540d\u79f0\t\u83b7\u5956\u4f5c\u54c1\t\u83b7\u5956\u7ed3\u679c\r\n2025-12\t\u7b2c10\u5c4a\u4e9a\u6d32\u660e\u661f\u76db\u5178\uff1a\u5e74\u5ea6\u4e9a\u6d32\u660e\u661f\u5956\u3001\u6700\u4f73\u827a\u4eba\u5956 [458]\t\t\u83b7\u5956\r\n2024-6\t\u7b2c2\u5c4a\u6d6a\u6f6e\u97f3\u4e50\u5927\u8d4f\uff1a\u6700\u4f73\u7537\u6b4c\u624b\u5956 [279]\t\u91cd\u62fe_\u5feb\u4e50\t\u83b7\u5956\r\n2024-6\t\u7b2c2\u5c4a\u6d6a\u6f6e\u97f3\u4e50\u5927\u8d4f\uff1a\u5e74\u5ea6\u4e13\u8f91\u5956 [383]\t\u91cd\u62fe_\u5feb\u4e50\t\u63d0\u540d\r\n2024-5\t\u7b2c35\u5c4a\u53f0\u6e7e\u91d1\u66f2\u5956\uff1a\u6700\u4f73\u534e\u8bed\u7537\u6b4c\u624b\u5956 [278]\t\u91cd\u62fe_\u5feb\u4e50\t\u63d0\u540d\r\n2024-", "score": 0.024}, {"chunk_id": "bac00767-ad06-4dfd-828d-bbf1b19914e2", "content": "\u5468\u6770\u4f26\u83b7\u5956\u8bb0\u5f55\r\n\u97f3\u4e50\u7c7b\r\n\u83b7\u5956\u65f6\u95f4\t\u5956\u9879\u540d\u79f0\t\u83b7\u5956\u4f5c\u54c1\t\u83b7\u5956\u7ed3\u679c\r\n2025-8\t\u7b2c6\u5c4a\u817e\u8baf\u97f3\u4e50\u5a31\u4e50\u76db\u5178\uff1a\u5e74\u5ea6\u6700\u4f73\u6e2f\u53f0\u7537\u6b4c\u624b\u5956 [458]\t\t\u83b7\u5956\r\n2025-4\t\u7b2c17\u5c4a\u97f3\u4e50\u76db\u5178\u54aa\u5495\u6c47\uff1a\u5341\u5927\u91d1\u66f2\u5956 [459]\t\u5723\u8bde\u661f\t\u83b7\u5956\r\n2023-8\t\u7b2c1\u5c4a\u6d6a\u6f6e\u97f3\u4e50\u5927\u8d4f\uff1a\u5e74\u5ea6\u5236\u4f5c\u5956\u3001\u6700\u4f73\u4f5c\u66f2\u5956 [343]\t\u6700\u4f1f\u5927\u7684\u4f5c\u54c1\t\u83b7\u5956\r\n2023-7\t\u7b2c4\u5c4a\u817e\u8baf\u97f3\u4e50\u5a31\u4e50\u76db\u5178\uff1a\u5e74\u5ea6\u6700\u5177\u5f71\u54cd\u529b\u6e2f\u53f0\u7537\u6b4c\u624b\u5956 [460]\t", "score": 0.023}]', 0.8428140204918898, NULL, '{"prompt": 22478, "completion": 9, "total": 22487, "response_time": 4.795404434204102}', '2026-03-14 03:29:38.20051', NULL, 'f');
INSERT INTO "public"."chat_messages" VALUES ('a42175b0-7aee-4c78-bdd4-b1c275ea7ee1', 'f3d63cbb-5402-404f-a7e8-059243cec2a0', 'user', '是是是', NULL, NULL, NULL, NULL, '2026-03-13 15:32:14.629351', NULL, 'f');
INSERT INTO "public"."chat_messages" VALUES ('a6aeea87-19f8-4ceb-8f6b-2e3ebcb69bc8', 'f3d63cbb-5402-404f-a7e8-059243cec2a0', 'assistant', '根据提供的信息，未检索到相关内容。', '[]', 0.3, NULL, '{"prompt": 363, "completion": 9, "total": 372, "response_time": 0.8400468826293945}', '2026-03-13 15:32:20.341479', NULL, 'f');
INSERT INTO "public"."chat_messages" VALUES ('88e6b40d-ed49-411b-954f-ee9b4ea5e0a6', '89513a6c-68a1-4aef-a0e5-bc16bb1de524', 'user', '王力宏拿过金曲歌王吗', NULL, NULL, NULL, NULL, '2026-03-14 03:42:48.579855', NULL, 'f');
INSERT INTO "public"."chat_messages" VALUES ('93997aaa-a5e7-4254-955a-89a42fc3053f', '89513a6c-68a1-4aef-a0e5-bc16bb1de524', 'assistant', '**王力宏共获得2次金曲奖“最佳国语男演唱人奖”（即“金曲歌王”）**。

1. **2006年**：第17届台湾金曲奖最佳国语男演唱人奖（获奖作品：《盖世英雄》）  
2. **1999年**：第10届台湾金曲奖最佳国语男演唱人奖（获奖作品：《公转自转》）

其中，**明确获奖的金曲歌王奖项共2项**。', '[{"chunk_id": "5fb3efe5-b8a1-4c92-b8e8-1cbe051dc412", "content": "\u738b\u529b\u5b8f\u83b7\u5956\u60c5\u51b5\r\n\u97f3\u4e50\u7c7b\r\n\u83b7\u5956\u65f6\u95f4\t\u5956\u9879\u540d\u79f0\t\u83b7\u5956\u4f5c\u54c1\t\u83b7\u5956\u7ed3\u679c\r\n2019\t\u534e\u4eba\u6b4c\u66f2\u97f3\u4e50\u76db\u5178\u5e74\u5ea6\u6700\u4f73\u7537\u6b4c\u624b [172]\t\t\u83b7\u5956\r\n2019\t\u534e\u4eba\u6b4c\u66f2\u97f3\u4e50\u76db\u5178\u5e74\u5ea6\u91d1\u66f2\u5956 [170]\t\u661f\u5149\t\u83b7\u5956\r\n2019\t\u534e\u4eba\u6b4c\u66f2\u97f3\u4e50\u76db\u5178\u5e74\u5ea6\u516c\u76ca\u6b4c\u66f2\u5956 [171]\t\u661f\u5149\t\u83b7\u5956\r\n2019\t\u6d41\u884c\u97f3\u4e50\u5168\u91d1\u699c\u5e74\u5ea6\u6700\u53d7\u6b22\u8fce\u7537\u6b4c\u624b [185]\t\t\u83b7\u5956\r\n2019\t\u6d41\u884c\u97f3\u4e50\u5168\u91d1\u699c\u5e74\u5ea6\u542c\u4f17\u6700\u7231\u6f14\u5531\u4f1a [185]\t\t\u83b7\u5956\r\n2", "score": 0.024}, {"chunk_id": "31135770-9208-4ec4-b691-828b8cdbc3f5", "content": "\u6797\u4fca\u6770\u83b7\u5956\u8bb0\u5f55\r\n\u83b7\u5956\u65f6\u95f4\t\u5956\u9879\u540d\u79f0\t\u83b7\u5956\u4f5c\u54c1\t\u83b7\u5956\u7ed3\u679c\r\n2025-12\t\u7b2c10\u5c4a\u4e9a\u6d32\u660e\u661f\u76db\u5178\uff1a\u5e74\u5ea6\u4e9a\u6d32\u660e\u661f\u5956\u3001\u6700\u4f73\u827a\u4eba\u5956 [458]\t\t\u83b7\u5956\r\n2024-6\t\u7b2c2\u5c4a\u6d6a\u6f6e\u97f3\u4e50\u5927\u8d4f\uff1a\u6700\u4f73\u7537\u6b4c\u624b\u5956 [279]\t\u91cd\u62fe_\u5feb\u4e50\t\u83b7\u5956\r\n2024-6\t\u7b2c2\u5c4a\u6d6a\u6f6e\u97f3\u4e50\u5927\u8d4f\uff1a\u5e74\u5ea6\u4e13\u8f91\u5956 [383]\t\u91cd\u62fe_\u5feb\u4e50\t\u63d0\u540d\r\n2024-5\t\u7b2c35\u5c4a\u53f0\u6e7e\u91d1\u66f2\u5956\uff1a\u6700\u4f73\u534e\u8bed\u7537\u6b4c\u624b\u5956 [278]\t\u91cd\u62fe_\u5feb\u4e50\t\u63d0\u540d\r\n2024-", "score": 0.024}, {"chunk_id": "134794b7-2599-4f6d-a3aa-5e86cd011f78", "content": "\u5b59\u71d5\u59ff\u83b7\u5956\u60c5\u51b5\r\n\u83b7\u5956\u65f6\u95f4\t\u5956\u9879\u540d\u79f0\t\u83b7\u5956\u4f5c\u54c1\t\u83b7\u5956\u7ed3\u679c\r\n2015-5-15\t\u7b2c5\u5c4a\u5168\u7403\u6d41\u884c\u97f3\u4e50\u91d1\u699c\uff1a\u5e74\u5ea620\u5927\u91d1\u66f2\u5956 [133]\t\u300a\u514b\u535c\u52d2\u300b\t\u83b7\u5956\r\n2015-5-15\t\u7b2c5\u5c4a\u5168\u7403\u6d41\u884c\u97f3\u4e50\u91d1\u699c\uff1aUFM100.3\u70b9\u64ad\u51a0\u519b\u5956 [133]\t\u300a\u5c1a\u597d\u7684\u9752\u6625\u300b\t\u83b7\u5956\r\n2015-5-15\t\u7b2c5\u5c4a\u5168\u7403\u6d41\u884c\u97f3\u4e50\u91d1\u699c\uff1a\u5e74\u5ea6\u6700\u4f73\u5973\u6b4c\u624b\u5956 [133]\t\t\u83b7\u5956\r\n2014-11-7\t\u7b2c19\u5c4a\u65b0\u52a0\u5761\u91d1\u66f2\u5956\uff1a\u6700\u4f73\u4e13\u8f91\u5956 ", "score": 0.023}]', 0.8699223453149065, NULL, '{"prompt": 15358, "completion": 119, "total": 15477, "response_time": 11.614129543304443}', '2026-03-14 03:43:17.711746', NULL, 'f');

-- ----------------------------
-- Table structure for kb_document_chunks
-- ----------------------------
DROP TABLE IF EXISTS "public"."kb_document_chunks";
CREATE TABLE "public"."kb_document_chunks" (
  "id" varchar(48) COLLATE "pg_catalog"."default" NOT NULL,
  "doc_id" varchar(48) COLLATE "pg_catalog"."default" NOT NULL,
  "kb_id" varchar(48) COLLATE "pg_catalog"."default" NOT NULL,
  "content" text COLLATE "pg_catalog"."default" NOT NULL,
  "chunk_index" int4 NOT NULL,
  "token_count" int4 NOT NULL,
  "meta" jsonb,
  "created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "is_deleted" bool DEFAULT false
)
;
COMMENT ON COLUMN "public"."kb_document_chunks"."id" IS 'ID';
COMMENT ON COLUMN "public"."kb_document_chunks"."doc_id" IS '文档ID';
COMMENT ON COLUMN "public"."kb_document_chunks"."kb_id" IS '知识库ID';
COMMENT ON COLUMN "public"."kb_document_chunks"."content" IS '文本内容';
COMMENT ON COLUMN "public"."kb_document_chunks"."chunk_index" IS '块索引';
COMMENT ON COLUMN "public"."kb_document_chunks"."token_count" IS 'token数量';
COMMENT ON COLUMN "public"."kb_document_chunks"."meta" IS '分页元数据';
COMMENT ON COLUMN "public"."kb_document_chunks"."created_at" IS '创建时间';
COMMENT ON COLUMN "public"."kb_document_chunks"."is_deleted" IS '创建时间';

-- ----------------------------
-- Records of kb_document_chunks
-- ----------------------------
INSERT INTO "public"."kb_document_chunks" VALUES ('134794b7-2599-4f6d-a3aa-5e86cd011f78', '5d8ff2e9-ba05-4a89-a47b-09d1e04c2a1e', '60b4d637-6acb-45e2-8217-07ddb5a79cf5', '孙燕姿获奖情况
获奖时间	奖项名称	获奖作品	获奖结果
2015-5-15	第5届全球流行音乐金榜：年度20大金曲奖 [133]	《克卜勒》	获奖
2015-5-15	第5届全球流行音乐金榜：UFM100.3点播冠军奖 [133]	《尚好的青春》	获奖
2015-5-15	第5届全球流行音乐金榜：年度最佳女歌手奖 [133]		获奖
2014-11-7	第19届新加坡金曲奖：最佳专辑奖 [137]	《克卜勒》	获奖
2014-11-7	第19届新加坡金曲奖：最受欢迎女歌手奖 [137]		获奖
2014-11-7	第19届新加坡金曲奖：醉心龙虎榜年度顶尖金曲奖 [137]	《天使的指纹》	获奖
2014-11-7	第19届新加坡金曲奖：最佳演绎女歌手奖 [137]		获奖
2012-1-19	2011年度北京流行音乐典礼：年度金曲奖 [139]	《是时候》	获奖
2012-1-19	2011年度北京流行音乐典礼：港台地区年度最受欢迎女歌手奖 [139]		获奖
2011-11-12	第17届新加坡金曲奖：最受欢迎女歌手奖 [130]		获奖
2011-11-12	第17届新加坡金曲奖：亚洲传媒大奖 [130]		获奖
2011-11-12	第17届新加坡金曲奖：最佳专辑制作人奖 [130]		获奖
2011-11-12	第17届新加坡金曲奖：933醉心龙虎榜顶尖金曲奖 [130]	《当冬夜渐暖》	获奖
2011-11-12	第17届新加坡金曲奖：榜上风光奖 [130]		获奖
2011-11-12	第17届新加坡金曲奖：933醉心龙虎榜十大金曲奖 [130]	《当冬夜渐暖》	获奖
2010-4-11	音乐风云榜十年盛典：港台十年最具影响力音乐人物奖 [26]		获奖
2010-4-11	音乐风云榜十年盛典：十年港台十大金曲奖 [26]	《遇见》	获奖
2008-8-2	第6届MTV亚洲奖：新加坡最受欢迎歌手奖 [158]		获奖
2008-5-22	第19届台湾金曲奖：最佳年度歌曲奖 [24]	《逆光》 [24]	提名
2007-5-29	中国原创音乐总评颁奖典礼：最佳专辑评审奖 [168]	《逆光》	获奖
2007-5-29	中国原创音乐总评颁奖典礼：最佳销量奖 [168]		获奖
2007-5-29	中国原创音乐总评颁奖典礼：最佳MV表演奖 [168]	《我怀念的》	获奖
2006-12-5	2006年度TVBS金曲榜颁奖礼：最受欢迎女歌手奖 [128]		获奖
2006-10-28	第6届全球华语歌曲排行榜：最受欢迎女歌手奖 [145]		获奖
2006-4-20	第6届音乐风云榜：港台最佳女歌手奖 [147]		获奖
2006-4-2	第6届音乐风云榜：三地联颁女歌手奖 [148]		获奖
2006-4-2	第6届音乐风云榜：港台地区最受欢迎女歌手奖 [147]		获奖
2005-9-3	第5届全球华语歌曲排行榜：最受欢迎对唱歌曲奖 [155]	《原点》	获奖
2005-5-29	MTV日本音乐录影带奖：最佳大中华歌手奖		获奖
2005-5-28	第16届台湾金曲奖：最佳国语女演唱人奖		获奖
2005-4-22	2004年度中国TOP排行榜：港台年度最佳唱片奖 [170]	《Stefanie》	获奖
2005-4-22	2004年度中国TOP排行榜：港台地区年度金曲奖 [170]	《我的爱》	获奖
2005-4-22	2004年度中国TOP排行榜：港台地区最受欢迎女歌手奖 [170]		获奖
2005-3-20	第5届音乐风云榜：港台地区年度最佳女歌手奖 [149]		获奖
2005-3-20	第5届音乐风云榜：台湾地区最受欢迎女歌手奖 [149]		获奖
2005-3-20	第5届音乐风云榜：港台十大金曲奖 [149]	《我的爱》	获奖
2005-3-20	第5届音乐风云榜：最佳年度录影带奖 [153]	《奔》	获奖
2005-3-19	第12届东方风云榜：华语五强 [161]		获奖
2005-3-19	第12届东方风云榜：全能艺人奖 [161]		获奖
2005-2-6	第4届MTV亚洲奖：新加坡最受欢迎歌手奖 [167]		获奖
2005-1-22	第12届中国歌曲排行榜：年度最受欢迎港台地区女歌手奖 [124]		获奖
2005-1-22	第12届中国歌曲排行榜：最受欢迎港台地区歌曲奖 [124]	《我的爱》	获奖
2005-1-19	第27届十大中文金曲：全国最受欢迎女歌手银奖 [181]		获奖
2005-1-19	第27届十大中文金曲：优秀流行国语歌曲奖 [154]	《我的爱》	获奖
2004-9-5	第4届全球华语歌曲排行榜：最佳专辑奖		获奖
2004-9-4	第4届全球华语歌曲排行榜：年度20大金曲奖 [136]	《遇见》	获奖
2004-9-4	第4届全球华语歌曲排行榜：最受欢迎女歌手奖 [135]		获奖
2004-9-4	第4届全球华语歌曲排行榜:新加坡地区杰出艺人奖 [141]		获奖
2004-8-20	第1届东南劲爆音乐榜：港台地区劲爆十大金曲奖 [156]	《神奇》	获奖
2004-6-22	2003年度中国TOP排行榜：港台地区年度金曲奖 [157]	《遇见》	获奖
2004-6-22	2003年度中国TOP排行榜：港台年度最佳唱片奖 [157]	《未完成》	获奖
2004-6-22	2003年度中国TOP排行榜：台湾地区最受欢迎女歌手奖 [157]		获奖
2004-3-28	第4届音乐风云榜：年度台湾地区最受欢迎女歌手奖 [151]		获奖
2004-3-28	第4届音乐风云榜：港台十大金曲奖 [151]	《遇见》	获奖
2004-3-28	第4届音乐风云榜：年度最佳影视歌曲奖 [151]	《遇见》	获奖
2004-2-14	第3届MTV亚洲奖：新加坡最受欢迎歌手奖 [166]		获奖
2004-1-9	第10届全球华语音乐榜中榜：最佳录影带奖 [169]	《我不难过》	获奖
2004-1-9	第10届全球华语音乐榜中榜：最佳音乐奖奖 [169]	《遇见》	获奖
2003-12-19	第26届十大中文金曲颁奖音乐会：全国最受欢迎中文歌曲奖铜奖 [144]	《遇见》	获奖
2003-12-19	第26届十大中文金曲颁奖音乐会：优秀流行国语歌曲奖银奖 [144]	《遇见》	获奖
2003-12-19	第26届十大中文金曲颁奖音乐会：全球最受欢迎女歌手金奖 [144]		获奖
2003-12-15	第1届天地英雄榜：年度最受欢迎港台歌手奖 [143]		获奖
2003-11-17	第4届中国金唱片奖：流行类新人奖		获奖
2003-9-19	第3届全球华语歌曲排行榜：新加坡杰出艺人奖 [165]		获奖
2003-9-19	第3届全球华语歌曲排行榜：最佳专辑奖 [165]	《未完成》	获奖
2003-9-19	第3届全球华语歌曲排行榜：年度金曲奖 [165]	《神奇》	获奖
2003-9-19	第3届全球华语歌曲排行榜：最受欢迎女歌手奖 [165]		获奖
2003-9-13	第5届CCTV-MTV音乐盛典：台湾地区年度最佳女歌手奖 [152]		获奖
2003-9-6	第10届新加坡金曲奖：新加坡最佳本地歌手奖 [146]		获奖
2003-9-6	第10届新加坡金曲奖：最受欢迎女歌手奖 [146]		获奖
2003-9-6	第10届新加坡金曲奖：亚太最受推崇女歌手奖 [146]		获奖
2003-3-29	第3届音乐风云榜：港台地区年度十大杰出金曲奖 [164]	《直来直往》	获奖
2003-3-29	第3届音乐风云榜：台湾地区最受欢迎女歌手奖 [164]		获奖
2003-3-29	第3届音乐风云榜：港台地区年度最佳女歌手奖 [164]		获奖
2003-1-24	第2届MTV亚洲奖：新加坡最受欢迎歌手奖 [162]		获奖
2003-1-19	第9届全球华语音乐榜中榜：港台地区最受欢迎女歌手奖 [150]		获奖
2003-1-1	2002年度中国TOP排行榜：港台十大金曲奖 [163]	《懂事》	获奖
2002-8-30	2002年度全球华语歌曲排行榜：最受欢迎女歌手奖 [160]		获奖
2002-8-30	2002年度全球华语歌曲排行榜：年度20大金曲奖 [160]	《我不爱》	获奖
2002-8-30	2002年度全球华语歌曲排行榜：杰出歌手奖 [160]		获奖
2002-8-30	2002年度全球华语歌曲排行榜：最佳专辑奖 [160]	《Leave》	获奖
2002-5-4	第13届台湾金曲奖：最佳流行音乐演唱专辑奖	《风筝》	提名
2002-5-4	第13届台湾金曲奖：最佳国语女演唱人		提名
2002-5-4	第13届台湾金曲奖：最佳音乐录影带奖	《风筝》	提名
2002-3-23	第2届音乐风云榜：台湾地区年度最佳女歌手奖 [125]		获奖
2002-3-23	第2届音乐风云榜：港台地区年度十大杰出金曲奖 [125]	《风筝》	获奖
2002-2-2	第1届MTV亚洲奖：新加坡地区最受欢迎歌手奖 [159]		获奖
2002-1-25	第8届全球华语音乐榜中榜：最受欢迎歌曲奖 [202]	《绿光》	获奖
2002-1-25 [246]	第8届全球华语榜中榜特别推荐新浪潮歌手(非奖项--港台)		获奖
2001-11-23	马来西亚第1届金曲红人颁奖典礼：最受欢迎红人金曲新人奖金奖 [132]		获奖
2001-9-8	第8届新加坡金曲奖：十大金曲奖 [129]	《开始懂了》	获奖
2001-9-8	第8届新加坡金曲奖：十大金曲奖 [129]	《我要的幸福》	获奖
2001-9-8	第8届新加坡金曲奖：最佳本地歌手奖 [129]		获奖
2001-9-8	第8届新加坡金曲奖：年度最畅销专辑奖 [129]	《我要的幸福》	获奖
2001-9-8	第8届新加坡金曲奖：最佳新人金奖 [129]		获奖
2001-7-20	第3届CCTV-MTV音乐盛典：台湾地区年度最具活力歌手奖 [138]		获奖
2001-5-18	第1届MTV封神榜音乐奖：十大人气歌手奖 [131]		获奖
2001-5-5	第12届台湾金曲奖：最佳国语女演唱人 [178]	《我要的幸福》	提名
2001-5-5	第12届台湾金曲奖：最佳新人奖 [102]		获奖
2001-5-5	第12届台湾金曲奖：最佳流行音乐演唱专辑奖	《我要的幸福》	获奖
2001-4-21	第1届音乐风云榜：港台地区年度最佳新人奖 [134]		获奖
2001-4-21	第1届音乐风云榜：港台地区年度十大金曲奖 [134]	《天黑黑》	获奖
2001-4-15	第7届全球华语榜中榜：最佳新人奖 [142]		获奖
2001-4-15	第7届全球华语榜中榜：最受欢迎歌曲奖 [142]	《爱情证书》	获奖
2001-2-24	第1届中国原创音乐流行榜：台湾地区最优秀男女新人奖 [140]		获奖
2001-2-24	第1届中国原创音乐流行榜：台湾地区优秀女歌手奖 [140]		获奖
2001-1-2	2000年度香港新城劲爆颁奖礼：新城劲爆新登场海外歌手奖 [126]		获奖
2000-9-16	第7届新加坡金曲奖：最具潜力本地新人奖		获奖
2000-9-1	TVB8频道金曲榜颁奖典礼：最佳新人奖 [127]		获奖', 0, 3581, '{"kb_id": "60b4d637-6acb-45e2-8217-07ddb5a79cf5", "doc_id": "5d8ff2e9-ba05-4a89-a47b-09d1e04c2a1e", "kb_name": "获奖情况知识库", "filename": "5d8ff2e9-ba05-4a89-a47b-09d1e04c2a1e.txt", "chunk_total": 1}', '2026-03-12 12:20:03.166409', 'f');
INSERT INTO "public"."kb_document_chunks" VALUES ('b9c193e0-da93-4647-bd7b-10cfa518d061', '400dc3e1-5853-499a-8499-fc13c2ebd84d', '69701332-85a5-431b-ab16-495b84b6f348', '周杰伦（Jay Chou），1979年1月18日出生于台湾省新北市，祖籍福建省永春县，华语流行乐男歌手、音乐人、演员、导演，毕业于淡江中学 [1]。', 0, 57, '{"kb_id": "69701332-85a5-431b-ab16-495b84b6f348", "doc_id": "400dc3e1-5853-499a-8499-fc13c2ebd84d", "filename": "400dc3e1-5853-499a-8499-fc13c2ebd84d.txt", "chunk_total": 4}', '2026-02-21 12:24:20.817376', 'f');
INSERT INTO "public"."kb_document_chunks" VALUES ('fb384198-6000-4400-9b5e-412110e4e85b', '400dc3e1-5853-499a-8499-fc13c2ebd84d', '69701332-85a5-431b-ab16-495b84b6f348', '2000年，发行个人首张音乐专辑《Jay》 [2]，并在华语乐坛获得广泛关注 [3]。2001年，凭借音乐专辑《范特西》奠定其乐坛地位 [4-5]，因此获得三座台湾金曲奖 [38]。2003年，登上美国《时代》杂志封面 [6]，此后相继推出《叶惠美》《七里香》《11月的萧邦》《依然范特西》等商业与口碑兼具的音乐专辑 [7-10]。2005年，主演个人首部电影《头文字D》 [13]，凭借该片获得香港电影金像奖和台湾电影金马奖“最佳新演员奖” [14]。2007年，成立“杰威尔音乐有限公司” [15]；同年首度担任导演，自编自导并主演爱情片《不能说的秘密》 [16-17]。2009年起，凭借音乐专辑《魔杰座》和《跨时代》两度获得台湾金曲奖“最佳国语男歌手奖” [18-19]；之后，持续产出作品并举行多轮世界巡演，成绩斐然 [22-23]。2023年，凭借音乐专辑《最伟大的作品》成为首位获得全球年度销量冠军的华语歌手 [26]。2024年，成为首位在台北大巨蛋举行演唱会的歌手 [24]。', 1, 340, '{"kb_id": "69701332-85a5-431b-ab16-495b84b6f348", "doc_id": "400dc3e1-5853-499a-8499-fc13c2ebd84d", "filename": "400dc3e1-5853-499a-8499-fc13c2ebd84d.txt", "chunk_total": 4}', '2026-02-21 12:24:20.817376', 'f');
INSERT INTO "public"."kb_document_chunks" VALUES ('588c2926-808f-4a47-94f9-5479da3fa937', '400dc3e1-5853-499a-8499-fc13c2ebd84d', '69701332-85a5-431b-ab16-495b84b6f348', '周杰伦共获得15座台湾金曲奖，是获得该奖项最多的音乐人 [28]；他四次获得世界音乐大奖“中国区最畅销艺人奖” [11-12]、两次获得MTV亚洲大奖“最受欢迎歌手奖” [29]，并被美国CNN评为“25位亚洲最具影响力人物”之一 [20]、被《Fast Company》杂志评为“全球百大创意人物”之一 [21]。作为音乐人，他为自己的所有原唱歌曲作曲并担任制作人 [28]，更将R&B、嘻哈等风格的唱法与中国传统音乐融合，使“中国风”这一名词登上流行音乐行列 [27]。', 2, 166, '{"kb_id": "69701332-85a5-431b-ab16-495b84b6f348", "doc_id": "400dc3e1-5853-499a-8499-fc13c2ebd84d", "filename": "400dc3e1-5853-499a-8499-fc13c2ebd84d.txt", "chunk_total": 4}', '2026-02-21 12:24:20.817376', 'f');
INSERT INTO "public"."kb_document_chunks" VALUES ('8beb2b11-49f2-4e50-8869-7267485c55c2', '400dc3e1-5853-499a-8499-fc13c2ebd84d', '69701332-85a5-431b-ab16-495b84b6f348', '2008年10月15日，周杰伦全亚洲发行个人第九张音乐专辑《魔杰座》，整张专辑共收录了《给我一首歌的时间》《花海》《魔术先生》等11首歌曲 [229]；该专辑通过魔术元素来让音乐变幻无穷 [80]，其中融合了嘻哈、民谣、R&B等多种类型的音乐风格，专辑中的每一首歌曲也都有不同的声音表情 [83]；这张专辑于推出首周在G-Music音乐排行榜、五大唱片排行榜上获得冠军，发行一星期在亚洲的销量突破100万张 [231]；在该专辑中，融合说唱与民谣元素的主打歌曲《稻香》由周杰伦亲自包办词曲创作 [82]，并透过童年主题传达知足的人生理念 [81]，发行后登上中国歌曲排行榜、全球华语歌曲排行榜、音乐之声中国TOP排行榜等多家主流音乐排行榜的冠军位置，并收获了来自听众与多家电台的诸多好评 [598]；与此同时，该曲还获得了2008年度北京流行音乐典礼“年度金曲奖” [508]、第9届全球华语歌曲排行榜“年度20大金曲奖” [504]；而周杰伦与方文山联手创作的情歌作品《说好的幸福呢》则是该专辑的第二主打歌曲 [229]，发行后也获得了中国原创音乐流行榜“全国至尊金曲奖” [500]。11月，凭借个人音乐专辑《我很忙》第四次获得世界音乐大奖“中国区最畅销艺人奖”（且是连续第三年获奖） [12]，由此成为继张学友之后首位连续三届获得该奖项的华人歌手 [230]。此外，他还凭借这一年中在音乐专辑、演唱会、商业演出、影视和广告五个方面取得的7.03亿元台币收入（约合人民币1.0521亿元），成为2008年度中国台湾地区全年收入最高的艺人 [599]。', 3, 495, '{"kb_id": "69701332-85a5-431b-ab16-495b84b6f348", "doc_id": "400dc3e1-5853-499a-8499-fc13c2ebd84d", "filename": "400dc3e1-5853-499a-8499-fc13c2ebd84d.txt", "chunk_total": 4}', '2026-02-21 12:24:20.817376', 'f');
INSERT INTO "public"."kb_document_chunks" VALUES ('f1e9bc20-1586-43c2-b846-650622195db4', '3c4670c3-cddc-4b87-a974-13c67f9d8176', '76a18674-1a4a-4e33-a520-78f9ec509e56', 'PMP（Project Management Professional），既指项目管理专业人员， [10]，也指项目管理专业人员认证 [11] [12]，1984年由美国项目管理协会(PMI)提出并设立，是针对评价个人项目管理知识能力而设计的一项全世界范围内的资格认证体系，通过该考试的人员可获得PMP资格证书。 [11] [12] [17]PMP考试每年四次，时间一般是在每个季度最后一个月的某个周末。 [10] [26]
1987年，PMI公布了PMP认证的基准——PMBOK® 的第1版草稿。 [16-17]；1991年，正式推广PMP。 [17]1999年，PMP成为全球第一个获得ISO 9001认证的认证考试。 [16]同年，中国国际人才交流基金会（原国家外国专家局培训中心）与PMI签署协议 [22]，将PMP引入中国，成为PMI在中国大陆唯一一家项目管理认证考试机构。 [18]2000年的6月及12月，中国大陆分别举行了PMP考试。 [11] 截至2021年底，中国大陆约有88万余人次参加了PMP考试，约50万人持有证书，持证人数占全球约1/3。 [18]2024年5月，PMI（中国）开通了证书有效性查验平台。 [21]截至2025年4月，PMP证书已得到170多个国家和地区的认可。 [24]
PMP可同时用英语、德语、法语、日语、朝语、西班牙语、葡萄牙语和中文等九种语言进行认证考试。 [11] [12]考试限时230分钟。 [10] [26]考试内容包括人员、过程、业务环境三个领域。 [26]PMP是项目管理领域最重要的认证之一 [11]，推动了中国在项目管理的实践上与国际接轨，提高了项目管理人员的整体从业水平和能力。 [18]', 0, 461, '{"kb_id": "76a18674-1a4a-4e33-a520-78f9ec509e56", "doc_id": "3c4670c3-cddc-4b87-a974-13c67f9d8176", "filename": "3c4670c3-cddc-4b87-a974-13c67f9d8176.txt", "chunk_total": 1}', '2026-03-11 16:37:28.572888', 'f');
INSERT INTO "public"."kb_document_chunks" VALUES ('a0fb3681-96b6-4b39-b24b-7c1318979543', '6e8b7134-145b-48a9-8a48-886d30e3fb7a', '76a18674-1a4a-4e33-a520-78f9ec509e56', 'PMP介绍
PMP（Project Management Professional），既指项目管理专业人员 [10]，也指项目管理专业人员认证 [11] [12]，是指由PMI发起的，针对评价个人项目管理知识能力而设计的一项全世界范围内的资格认证体系，通过该认证的人员可获得PMP资格证书。 其目的是为了给项目管理人员提供统一的行业标准。 [11] [24]
PMP是项目管理领域最重要的认证之一，受到业内广泛认可。 与其他专注于特定地区或特定行业的认证不同，PMP是真正全球通用的认证，不局限于某种项目管理方法论、某一行业或地区。 [12]PMP作为项目管理资格认证考试为美国培养了一大批项目管理专业人才，项目管理职业已成为美国的“黄金职业”。 在中国，许多媒体已把PMP称为继MBA、MPA 之后的三大金字招牌之一，在国际上树立了其权威性。 [11]
PMP认证已成为一个国际性的认证标准，可同时用英语、德语、法语、日语、朝语、西班牙语、葡萄牙语和中文等九种语言进行认证考试。 [11]
PMP认证的基准是美国的《PMBOK·指南》，其将项目管理的知识领域分为十大模块，即范围管理、时间管理成本管理、质量管理、人力资源管理、风险管理、沟通管理、采购管理、利益相关者管理和综合集成管理。 [17]
历史沿革
播报
编辑
设立及推广
1969年，美国项目管理协会(Project ManagementInstitute，PMl)在美国宾州成立，倡议发起人是恩格曼，他是McAUTO CPM软件销售人员。 [16]
随着项目管理科学体系的发展和应用的需要，项目管理证书体系也随之产生，主要是为了证明项目管理从业人员的能力及资质水平。 1984年，PMI最早提出并设立了项目管理资质认证制度(PMP) [17]，该认证制度是严格的、以考试为依据的专家资质认证制度。', 0, 482, '{"kb_id": "76a18674-1a4a-4e33-a520-78f9ec509e56", "doc_id": "6e8b7134-145b-48a9-8a48-886d30e3fb7a", "filename": "6e8b7134-145b-48a9-8a48-886d30e3fb7a.txt", "chunk_total": 3}', '2026-03-11 16:37:42.90212', 'f');
INSERT INTO "public"."kb_document_chunks" VALUES ('bf9ed0a1-5eb9-4a79-bec4-e1512ede3960', '6e8b7134-145b-48a9-8a48-886d30e3fb7a', '76a18674-1a4a-4e33-a520-78f9ec509e56', '[16]
随着项目管理科学体系的发展和应用的需要，项目管理证书体系也随之产生，主要是为了证明项目管理从业人员的能力及资质水平。 1984年，PMI最早提出并设立了项目管理资质认证制度(PMP) [17]，该认证制度是严格的、以考试为依据的专家资质认证制度。 [16]
1987年，PMI在ESA研究报告基础上公布了PMP认证的基准——《PMBOK》的第1版草稿。 [16-17]
1991年，PMI正式推广PMP。 [17]1999年，PMP成为全球第一个获得ISO 9001认证的认证考试。 [16]
中国引入
1999年，中国国际人才交流基金会（原国家外国专家局培训中心）与PMI签署协议 [22]，将《项目管理知识体系指南》（PMBOK Guide）和“项目管理专业人士职业资格认证”（PMP）引入中国，成为PMI在中国大陆唯一一家项目管理认证考试机构。 [18]
2000年的6月及12月，中国大陆分别举行了PMP 考试，有二百多人参加考试；2001年6月、11月又分别举行了PMP 资格认证考试，采用中英文对照考试形式，近八百人参加了考试。 [11]
2010年，国务院国资委、国家外专局联合主办了“中央企业国际化人才国际项目管理师（PMP）职业资格认证培训”。 [7]
截至2019年，中国大陆PMP资格考试为中英文对照形式，题型为单项选择题，共200道题。 笔试时间是从早上9点到下午1点，考试时间为4小时。 PMP认证考试一年有四次，分别在3月、6月、9 月、12月。 考试的内容涉及PMBOK中的知识内容，包括项目管理的五大过程组以及十大知识领域。 [11]
2021年，从该年第二次考试开始，为满足项目管理专业人士职业发展的相关需求，中国大陆PMP认证考试进行改版。 新版专注于以下人、过程、业务互不干涉等三个新领域。', 1, 494, '{"kb_id": "76a18674-1a4a-4e33-a520-78f9ec509e56", "doc_id": "6e8b7134-145b-48a9-8a48-886d30e3fb7a", "filename": "6e8b7134-145b-48a9-8a48-886d30e3fb7a.txt", "chunk_total": 3}', '2026-03-11 16:37:42.90212', 'f');
INSERT INTO "public"."kb_document_chunks" VALUES ('3c31628c-213d-41d0-94b3-f1795f5626c8', '6e8b7134-145b-48a9-8a48-886d30e3fb7a', '76a18674-1a4a-4e33-a520-78f9ec509e56', '考试的内容涉及PMBOK中的知识内容，包括项目管理的五大过程组以及十大知识领域。 [11]
2021年，从该年第二次考试开始，为满足项目管理专业人士职业发展的相关需求，中国大陆PMP认证考试进行改版。 新版专注于以下人、过程、业务互不干涉等三个新领域。 同时，新版考试调整为: 考试题目由原来的200道题改为180 道题；考试时间由原来的240分钟改为230分钟；题型调整为包括单选题和多选题，多选题将说明需选择几个正确选项。 [19]', 2, 141, '{"kb_id": "76a18674-1a4a-4e33-a520-78f9ec509e56", "doc_id": "6e8b7134-145b-48a9-8a48-886d30e3fb7a", "filename": "6e8b7134-145b-48a9-8a48-886d30e3fb7a.txt", "chunk_total": 3}', '2026-03-11 16:37:42.90212', 'f');
INSERT INTO "public"."kb_document_chunks" VALUES ('31135770-9208-4ec4-b691-828b8cdbc3f5', '16c330ba-b341-4fc4-9f18-ee6ecedfe702', '60b4d637-6acb-45e2-8217-07ddb5a79cf5', '林俊杰获奖记录
获奖时间	奖项名称	获奖作品	获奖结果
2025-12	第10届亚洲明星盛典：年度亚洲明星奖、最佳艺人奖 [458]		获奖
2024-6	第2届浪潮音乐大赏：最佳男歌手奖 [279]	重拾_快乐	获奖
2024-6	第2届浪潮音乐大赏：年度专辑奖 [383]	重拾_快乐	提名
2024-5	第35届台湾金曲奖：最佳华语男歌手奖 [278]	重拾_快乐	提名
2024-5	第35届台湾金曲奖：最佳作曲人奖 [278]	愿与愁	提名
2023-7	第4届腾讯音乐娱乐盛典：年度最佳港台男歌手奖、最具影响力制作人奖 [382]		获奖
2023-7	第4届腾讯音乐娱乐盛典：年度十大金曲奖 [382]	裹着心的光	获奖
2021-12	第3届腾讯音乐娱乐盛典：最具影响力港台男歌手奖 [384]		获奖
2021-11	第28届MTV欧洲音乐奖：最佳东南亚艺人奖 [16]		获奖
2021-5	第32届台湾金曲奖：最佳华语男歌手奖 [385]	幸存者·如你	提名
2021-1	第2届腾讯音乐娱乐盛典：年度最佳港台男歌手奖、年度最佳制作人奖 [386]		获奖
2020-12	亚洲流行音乐大奖2020：华语最佳男歌手奖、华语最佳专辑奖、华语最佳制作人奖 [387]	幸存者·如你	获奖
2020-12	亚洲流行音乐大奖2020：华语最佳音乐录影带奖 [387]	幸存者	获奖
2019-12	第1届腾讯音乐娱乐盛典：年度最佳港台男歌手奖 [388]		获奖
2019-1	2018微博之夜：微博国际影响力音乐人奖 [234]		获奖
2018-12	2018Mnet亚洲音乐大奖：亚洲最佳艺人奖（华语） [25]		获奖
2018-8	2018华人歌曲音乐盛典：港台及海外地区年度最佳男歌手奖、年度最佳专辑奖、年度最佳专辑制作人奖 [229]	伟大的渺小	获奖
2018-8	2018华人歌曲音乐盛典：年度金曲奖 [229]	伟大的渺小	获奖
2018-7	第2届唱工委音乐奖：年度男歌手奖 [223]	伟大的渺小	获奖
2018-6	中华音乐人交流协会：2017年度十大单曲奖 [389]	伟大的渺小	获奖
2018-6	2018hito流行音乐奖：年度十大华语歌曲奖、年度百首单曲冠军 [390]	伟大的渺小	获奖
2018-6	2018hito流行音乐奖：最受欢迎男歌手奖、新加坡推崇歌手奖 [390]		获奖
2018-5	第29届台湾金曲奖：最佳国语男歌手奖、最佳国语专辑奖、最佳年度专辑奖、最佳专辑制作人奖 [222]	伟大的渺小	提名
2018-5	第29届台湾金曲奖：最佳年度歌曲奖、最佳作曲人奖 [222]	伟大的渺小	提名
2018-4	第22届全球华语榜中榜：Channel [V]国际最受欢迎华语艺人奖、亚洲影响力最佳专辑奖 [221]	伟大的渺小	获奖
2017-7	2017亚洲金曲大赏：港台地区最佳男歌手奖 [391]		获奖
2017-6	2017hito流行音乐奖：最受欢迎男歌手奖、新加坡推崇歌手奖 [392]		获奖
2017-6	2017hito流行音乐奖：年度十大华语歌曲奖、年度百首单曲冠军 [392]	不为谁而作的歌	获奖
2017-4	第5届音悦V榜年度盛典：港台地区年度最具人气艺人奖 [393]		获奖
2016-12	2016Mnet亚洲音乐大奖：亚洲年度最佳艺人奖（新加坡） [394]		获奖
2016-8	第2届美国Pensado Awards颁奖典礼：最佳外语歌曲奖 [211]	不为谁而作的歌	获奖
2016-6	第27届台湾金曲奖：最佳国语男歌手奖 [14]	和自己对话	获奖
2016-6	第27届台湾金曲奖：最佳作曲人奖 [206]	不为谁而作的歌	获奖
2016-6	第27届台湾金曲奖：最佳年度歌曲奖、最佳音乐录影带奖 [395]	不为谁而作的歌	提名
2016-6	第27届台湾金曲奖：最佳专辑制作人奖 [395]	和自己对话	提名
2016-6	第9届城市至尊音乐榜：年度至尊男歌手奖、年度20大金曲奖 [397]	不为谁而作的歌	获奖
2016-6	2016hito流行音乐奖：hito男歌手奖 [396]		获奖
2016-5	2015年度中国TOP排行榜：港台地区年度最佳男歌手奖、年度最佳唱片奖 [398]	和自己对话	获奖
2016-5	2015年度中国TOP排行榜：年度金曲奖 [398]	不为谁而作的歌	获奖
2016-4	第20届全球华语榜中榜：港台地区最佳专辑奖、亚洲影响力最受欢迎歌手奖 [399]	和自己对话	获奖
2016-4	第6届全球流行音乐金榜：年度最佳男歌手奖、年度最受欢迎专辑奖 [400]	和自己对话	获奖
2016-3	2016QQ音乐巅峰盛典：年度最佳港台男歌手奖、年度最佳唱作专辑奖 [401]		获奖
2015-8	2014年度中国TOP排行榜：港台地区年度最佳男歌手奖 [402]	新地球	获奖
2015-8	2014年度中国TOP排行榜：港台地区年度金曲奖 [402]	可惜没如果	获奖
2015-6	第26届台湾金曲奖：最佳作曲人奖、最佳单曲制作人奖 [194]	你给我听好	提名
2015-6	第8届城市至尊音乐榜：年度20大金曲奖 [403]	可惜没如果	获奖
2015-5	第5届全球流行音乐金榜：年度最受欢迎男歌手奖、年度最佳制作人奖、UFM100.3年度电台推崇大奖 [404]		获奖
2015-5	第5届全球流行音乐金榜：年度20大金曲奖 [404]	新地球	获奖
2015-3	2015QQ音乐年度盛典：最受欢迎港台男歌手奖、港台地区年度最佳音乐制作人奖 [405]		获奖
2015-3	2015QQ音乐年度盛典：港台地区年度最佳国语专辑奖 [405]	新地球	获奖
2014-12	2014Mnet亚洲音乐大奖：亚洲年度最佳艺人奖（新加坡）		获奖
2014-6	第25届台湾金曲奖：最佳国语男歌手奖 [13]		获奖
2014-6	中华音乐人交流协会：2013年度十大单曲奖 [185]	黑暗骑士	获奖
2014-6	第7届城市至尊音乐榜：年度至尊男歌手奖、联盟点播冠军王奖、年度20大金曲奖 [406]	修炼爱情	获奖
2014-6	2014hito流行音乐奖：hito最佳男歌手奖 [184]		获奖
2014-6	2014hito流行音乐奖：年度十大华语歌曲奖、2013年度百首单曲冠军 [184]	修炼爱情	获奖
2014-4	2013年度中国TOP排行榜：港台地区年度最佳男歌手奖、年度最受欢迎唱片奖 [407]	因你而在	获奖
2014-4	2013年度中国TOP排行榜：港台地区年度金曲奖 [407]	修炼爱情	获奖
2014-4	第2届音悦V榜年度盛典：年度最佳男歌手奖、最佳创作歌手奖 [408]		获奖
2014-4	第4届全球流行音乐金榜：年度进榜最久冠军单曲奖、年度20大金曲奖、HIT FM联播网年度点播冠军奖 [409]	修炼爱情	获奖
2014-3	2014QQ音乐年度盛典：港台最佳男歌手奖、年度最佳国语专辑奖 [410]	因你而在	获奖
2013-10	第13届全球华语歌曲排行榜：年度20大金曲奖 [411]	修炼爱情	获奖
2013-6	2013hito流行音乐奖：hito最佳男歌手奖、hito制作人奖 [176]		获奖
2013-6	2013hito流行音乐奖：年度K歌奖、年度十大华语歌曲奖 [176]	学不会	获奖
2013-4	第1届音悦V榜年度盛典：港台地区最佳男歌手奖、最佳创作歌手奖、最佳制作人奖、现场直播人气奖 [175]		获奖
2013-4	第1届音悦V榜年度盛典：年度最佳MV奖 [175]	学不会	获奖
2013-3	第20届东方风云榜：亚洲人气歌手奖、华语五强新加坡最受欢迎歌手奖 [173]		获奖
2012-11	第12届全球华语歌曲排行榜：最受欢迎男歌手五强奖、全能艺人奖 [161]		获奖
2012-11	第12届全球华语歌曲排行榜：年度20大金曲奖 [161]	学不会	获奖
2012-11	第12届全球华语歌曲排行榜：最佳专辑奖 [161]	学不会	获奖
2012-8	2012新城国语力颁奖礼：新城国语力亚洲创作歌手奖、新城国语力制作人奖 [412]		获奖
2012-7	第17届新加坡词曲版权协会奖：最佳本地歌手奖、最佳本地歌曲创作人奖 [159]		获奖
2012-7	第17届新加坡词曲版权协会奖：最佳本地中文流行歌曲奖 [159]	记得	获奖
2012-6	第2届全球流行音乐金榜：年度最佳男歌手奖、洛杉矶AM1300中文电台推崇大奖 [413]	学不会	获奖
2012-6	第2届全球流行音乐金榜：年度金曲奖 [413]	学不会	获奖
2012-5	第4届新加坡e乐大赏：最佳本地歌手奖、人气本地歌手奖、传媒推荐全方位艺人奖 [414]		获奖
2012-5	2012hito流行音乐奖：hito长寿专辑奖 [415]	她说	获奖
2012-4	2011年度中国TOP排行榜：港台地区年度最佳男歌手奖、年度最佳制作人奖 [157]		获奖
2012-4	2011年度中国TOP排行榜：港台地区年度最佳作曲奖、年度金曲奖 [416]	学不会	获奖
2012-4	第16届全球华语榜中榜：台湾地区最佳男歌手奖、港台地区最佳创作歌手奖 [417]		获奖
2012-2	2011年度中国原创音乐流行榜：台湾地区最受欢迎男歌手奖、最优秀创作歌手奖 [418]		获奖
2012-2	2011年度中国原创音乐流行榜：港台金曲奖 [418]	她说	获奖
2012-1	第7届KKBOX数位音乐风云榜：年度十大风云歌手奖 [419]		获奖
2011-10	第11届全球华语歌曲排行榜：最受欢迎男歌手五强奖 [420]		获奖
2011-5	第22届台湾金曲奖：最佳国语男歌手奖 [421]	她说	提名
2011-4	第1届全球流行音乐金榜：年度最佳创作歌手奖、新加坡电台1003推崇大奖 [422]		获奖
2011-4	第1届全球流行音乐金榜：年度最佳制作人奖 [422]	她说	获奖
2011-4	第1届全球流行音乐金榜：年度20大金曲奖 [422]	第几个100天	获奖
2011-3	第3届新加坡e乐大赏：e乐最佳本地歌手奖 [423]	她说	获奖
2011-1	2010年度中国原创音乐流行榜：台湾地区最受欢迎男歌手奖、最优秀创作歌手奖、传媒推荐大奖 [424]		获奖
2011-1	2010年度中国原创音乐流行榜：港台金曲奖 [424]	背对背拥抱	获奖
2011-1	2010年度北京流行音乐典礼：港台地区年度最佳创作歌手奖 [142]		获奖
2011-1	2010年度北京流行音乐典礼：年度金曲奖 [143]	背对背拥抱	获奖
2010-12	第10届全球华语歌曲排行榜：最佳男歌手奖、最受欢迎创作歌手奖、新加坡地区杰出歌手奖、最受欢迎男歌手五强奖 [141]		获奖
2010-12	第10届全球华语歌曲排行榜：年度20大金曲奖 [141]	背对背拥抱	获奖
2010-12	第8届东南劲爆音乐榜：港台地区最受欢迎男歌手奖、最佳唱作歌手奖 [127]		获奖
2010-12	第8届东南劲爆音乐榜：最佳专辑奖 [127]	100天	获奖
2010-10	第10届CCTV-MTV音乐盛典：港澳台地区年度最受欢迎男歌手奖 [425]		获奖
2010-7	第15届新加坡词曲版权协会奖：最佳本地歌手奖、最佳本地歌曲创作人奖 [133]		获奖
2010-5	第21届台湾金曲奖：最佳国语男歌手奖 [131]	100天	提名
2010-4	音乐风云榜十年盛典：港台地区十年十大金曲奖 [130]	江南	获奖
2010-2	2009年度中国原创音乐流行榜：港台金曲奖 [426]	第几个100天	获奖
2010-2	2009年度中国原创音乐流行榜：台湾地区最佳男歌手奖、最优秀创作歌手奖 [426]		获奖
2010-2	2009年度北京流行音乐典礼：年度最佳舞台演绎男歌手奖、最佳编曲奖 [111]		获奖
2010-2	2009年度北京流行音乐典礼：年度金曲奖 [111]	不潮不用花钱	获奖
2009-12	第3届中国移动无线音乐盛典咪咕汇：无线音乐最畅销对唱金曲奖 [427]	小酒窝	获奖
2009-11	第9届全球华语歌曲排行榜：最受欢迎男歌手奖、新加坡地区杰出歌手奖、最受欢迎男歌手五强奖 [428-429]		获奖
2009-11	第9届全球华语歌曲排行榜：最受欢迎对唱金曲奖 [429]	小酒窝	获奖
2009-8	2009新城国语力颁奖礼：新城国语力亚洲唱跳歌手奖、最受欢迎偶像奖 [430]		获奖
2009-8	2009新城国语力颁奖礼：新城国语力歌曲奖、新城国语力热爆K歌奖 [430]	小酒窝	获奖
2009-5	第14届新加坡词曲版权协会奖：最佳本地影剧歌曲奖、最佳本地创作人奖、最佳本地歌手奖 [117]		获奖
2009-4	2008年度中国原创音乐流行榜：台湾地区最受欢迎男歌手奖、最优秀创作歌手奖 [431]		获奖
2009-4	2008年度中国原创音乐流行榜：最优秀合唱歌曲奖 [431]	小酒窝	获奖
2009-4	2008年度中国原创音乐流行榜：港台金曲奖 [431]	爱与希望	获奖
2009-4	第9届音乐风云榜：港台最佳制作人奖 [432]	JJ陆	获奖
2009-4	2008年度中国TOP排行榜：港台地区年度最佳编曲奖 [459]	不潮不用花钱	获奖
2009-3	第16届东方风云榜：华语五强奖（新加坡地区） [433]		获奖
2009-1	第31届十大中文金曲：全国最佳中文歌曲奖 [110]	小酒窝	获奖
2009-1	2008年度十大劲歌金曲颁奖典礼：最受欢迎华语歌曲奖（银奖） [108]	小酒窝	获奖
2009-1	2008年度北京流行音乐典礼：年度最佳舞台演绎男歌手奖 [106]		获奖
2009-1	2008年度北京流行音乐典礼：港台地区年度最佳专辑奖 [105]	JJ陆	获奖
2009-1	2008年度北京流行音乐典礼：年度金曲奖 [109]	小酒窝	获奖
2008-12	2008新城劲爆颁奖礼：新城全国乐迷投选劲爆歌手奖、新城劲爆亚洲跳唱歌手奖 [107]		获奖
2008-12	2008新城劲爆颁奖礼：新城劲爆卡拉OK歌曲奖、新城劲爆合唱歌曲奖 [107]	小酒窝	获奖
2008-12	音乐先锋榜：最受欢迎对唱金曲奖 [434]	小酒窝	获奖
2008-1	2007年度中国原创音乐流行榜：港台地区最受欢迎男歌手奖 [436]		获奖
2008-1	2007年度中国原创音乐流行榜：港台金曲奖 [436]	西界	获奖
2008-1	2007年度中国原创音乐流行榜：最佳深情故事奖 [436]	杀手	获奖
2008-1	2007年度北京流行音乐典礼：年度最佳舞台演绎男歌手奖 [91]	西界	获奖
2008-1	2007年度北京流行音乐典礼：年度金曲奖 [91]	西界	获奖
2008-1	2007年度百度娱乐沸点颁奖典礼：年度十大金曲奖 [92]	杀手	获奖
2007-10	第7届全球华语歌曲排行榜：二十大最受欢迎金曲奖 [88]	杀手	获奖
2007-8	2007新城国语力颁奖礼：新城国语力舞台大奖 [438]		获奖
2007-8	2007新城国语力颁奖礼：新城国语力歌曲奖 [438]	杀手	获奖
2007-6	2006年度中国TOP排行榜：最佳唱片销售男歌手奖 [439]	曹操	获奖
2007-5	第18届台湾金曲奖：最佳国语男歌手奖 [440]	曹操	提名
2007-1	2006年度北京流行音乐典礼：年度最受欢迎男歌手奖、唱作真英雄奖 [78]		获奖
2007-1	2006年度北京流行音乐典礼：年度最佳专辑奖、年度最佳制作人奖 [78]	曹操	获奖
2006-10	第6届全球华语歌曲排行榜：最受欢迎创作歌手奖 [77]		获奖
2006-10	第6届全球华语歌曲排行榜：二十大最受欢迎金曲奖 [77]	曹操	获奖
2006-10	第8届CCTV-MTV音乐盛典：台湾地区年度最受欢迎男歌手奖 [76]		获奖
2006-4	2005年度北京流行音乐典礼：年度最佳创作歌手奖 [69]		获奖
2006-4	2006年度北京流行音乐典礼：年度最受欢迎金曲奖 [68]	一千年以后	获奖
2006-4	2005年度中国TOP排行榜：港台年度金曲奖、港台年度最佳作曲奖 [441-442]	一千年以后	获奖
2006-4	2005年度中国TOP排行榜：港台最受欢迎男歌手奖 [441]		获奖
2006-3	第13届东方风云榜：华语五强奖（新加坡） [443]		获奖
2006-2	TVBS“华众曲宠”华语金曲榜：海外杰出男歌手奖、票选海外歌手奖、十大专辑奖 [460]	编号89757	获奖
2006-1	2006hito流行音乐奖：新加坡hito海外歌手奖 [444]		获奖
2006-1	2006hito流行音乐奖：2005年度十大华语歌曲奖 [444]	简简单单	获奖
2006-1	2005年度中国原创音乐流行榜：台湾地区最优秀创作歌手奖 [445]		获奖
2005-11	第12届新加坡金曲奖：最佳演绎男歌手奖、最佳本地男歌手奖、最佳创作歌手奖 [4]		获奖
2005-11	第12届新加坡金曲奖：最佳本地作曲奖 [4]	一千年以后	获奖
2005-10	第3届东南劲爆音乐榜：台湾地区最佳唱作男歌手奖、最受欢迎男歌手奖 [446]		获奖
2005-10	第3届东南劲爆音乐榜：台湾地区十大金曲奖、内地十大金曲奖 [446]	一千年以后（台湾地区）, 被风吹过的夏天（内地）	获奖
2005-9	第5届全球华语歌曲排行榜：最受欢迎创作歌手奖、新加坡地区杰出歌手奖 [57]	一千年以后	获奖
2005-9	第5届全球华语歌曲排行榜：最佳专辑奖 [57]	编号89757	获奖
2005-9	第5届全球华语歌曲排行榜：25大歌曲奖 [57]	一千年以后	获奖
2005-7	第7届CCTV-MTV音乐盛典：年度最佳单曲奖 [55]	一千年以后	获奖
2005-5	第2届劲歌王全球华人乐坛年度总选：劲歌唱作人王奖、网络人气男歌手奖 [54]		获奖
2005-5	第2届劲歌王全球华人乐坛年度总选：十大国语金曲奖 [54]	江南	获奖
2005-4	2004年度中国TOP排行榜：港台地区年度最佳创作歌手奖 [53]		获奖
2005-4	2004年度中国TOP排行榜：港台地区年度金曲奖、港台地区年度最佳作曲奖 [53]	江南	获奖
2005-4	第16届台湾金曲奖：最佳作曲人奖 [448]	江南	提名
2005-3	第5届音乐风云榜：港台地区十大金曲奖 [42]	江南	获奖
2005-1	第12届中国歌曲排行榜：港台地区年度最佳创作歌手奖 [47]		获奖
2005-1	第12届中国歌曲排行榜：最受欢迎港台地区歌曲奖 [47]	江南	获奖
2004-10	第2届中国原创歌曲奖：港台地区最受欢迎男歌手奖、海外最佳创作人奖、最佳制作奖 [46]	第二天堂	获奖
2004-9	第2届东南劲爆音乐榜：港台地区劲爆最佳新锐创作人奖 [44]		获奖
2004-9	第2届东南劲爆音乐榜：港台劲爆十大金曲奖 [44]	江南	获奖
2004-9	第4届全球华语歌曲排行榜：年度20大金曲奖 [41]	江南	获奖
2004-6	2003年度中国TOP排行榜：港台地区最受欢迎新人奖 [449]		获奖
2004-6	2003年度中国TOP排行榜：港台地区年度最佳作曲奖 [449]	放手	获奖
2004-5	第15届台湾金曲奖：最佳新人奖 [2]	乐行者	获奖
2004-4	第4届音乐风云榜：港台十大金曲奖 [38]	就是我	获奖
2004-2	第2届hito流行音乐奖：年度Hito声猛男新人奖 [447]		获奖
2003-9	第10届新加坡金曲奖：最佳新人奖（金奖） [30]	乐行者	获奖
2003	第1届hito流行音乐奖：第二季Hito十大金曲奖 [30]	翅膀	获奖
社会类
获奖时间	奖项名称	获奖结果
2014-11	第5届通商中国青年奖 [367]	获奖
2009-7	新加坡杰出青年奖 [366]	获奖
2008-10	第1届中国海西时尚娱乐盛典：时尚亚洲杰出艺人奖 [435]	获奖', 0, 6272, '{"kb_id": "60b4d637-6acb-45e2-8217-07ddb5a79cf5", "doc_id": "16c330ba-b341-4fc4-9f18-ee6ecedfe702", "kb_name": "获奖情况知识库", "filename": "16c330ba-b341-4fc4-9f18-ee6ecedfe702.txt", "chunk_total": 1}', '2026-03-12 12:20:12.92345', 'f');
INSERT INTO "public"."kb_document_chunks" VALUES ('5fb3efe5-b8a1-4c92-b8e8-1cbe051dc412', '6a68d4b9-6e37-4c70-bd93-0adac1b60505', '60b4d637-6acb-45e2-8217-07ddb5a79cf5', '王力宏获奖情况
音乐类
获奖时间	奖项名称	获奖作品	获奖结果
2019	华人歌曲音乐盛典年度最佳男歌手 [172]		获奖
2019	华人歌曲音乐盛典年度金曲奖 [170]	星光	获奖
2019	华人歌曲音乐盛典年度公益歌曲奖 [171]	星光	获奖
2019	流行音乐全金榜年度最受欢迎男歌手 [185]		获奖
2019	流行音乐全金榜年度听众最爱演唱会 [185]		获奖
2019	流行音乐全金榜年度最佳公益歌曲 [185]	星光	获奖
2018	娱协30最佳原创金曲奖 [184]	飘向北方	获奖
2018	娱协30最受欢迎K歌金奖 [184]	飘向北方	获奖
2016	第20届全球华语榜中榜 亚洲影响力全能华语艺人 [70]		获奖
2016	第20届全球华语榜中榜Channel V 年度最佳歌手 [70]		获奖
2016	第3届QQ音乐巅峰盛典最受欢迎港台男歌手 [183]		获奖
2016	第3届QQ音乐巅峰盛典年度最佳音乐制作人 [183]		获奖
2016	第3届QQ音乐巅峰盛典港台最佳国语专辑	你的爱	获奖
2015	第15届华鼎奖全球最佳歌唱演员奖		获奖
2015	第2届QQ音乐年度盛典台湾地区最佳男歌手		获奖
2015	第2届QQ音乐年度盛典年度最佳现场录音专辑	The Free Show 2014	获奖
2015	第2届QQ音乐年度盛典年度最佳国际单曲	忘我	获奖
2015	第2届QQ音乐年度盛典年度最高人气艺人		获奖
2012	第11届CCTV-MTV音乐盛典港澳台地区年度最佳男歌手		获奖
2012	第14届Mnet亚洲音乐大奖亚洲最佳艺人 [175]		获奖
2011	第6届kkbox数位音乐风云榜百大专辑	十八般武艺	获奖
2011	年度百度娱乐沸点最热门港台男歌手	你不知道的事	获奖
2011	第1届全球流行音乐金榜年度最佳男歌手奖 [174]		获奖
2011	第15届全球华语榜中榜最佳港台男歌手 [56]		获奖
2011	雪碧音乐榜最受欢迎电影金曲	你不知道的事	获奖
2011	MusicRadio音乐之声DJ推荐2010年度20大华语碟	十八般武艺	获奖
2011	第5届真维斯娱乐大典年度最具影响力港台男歌手		获奖
2011	2010年度北京流行音乐颁奖典礼年度最佳制作人手（港台）		获奖
2011	第22届台湾金曲奖最佳年度歌曲奖	你不知道的事	提名
2011	第22届台湾金曲奖最佳国语专辑奖	十八般武艺	提名
2011	第22届台湾金曲奖最佳国语男歌手奖	十八般武艺	提名
2011	2010年度北京流行音乐颁奖典礼年度最佳男歌手 （港台）		获奖
2011	2010年度北京流行音乐颁奖典礼年度金曲	你不知道的事	获奖
2011	第15届全球华语榜中榜最佳专辑奖 [56]		获奖
2011	第1届全球流行音乐金榜最佳作曲奖		获奖
2011	第1届全球流行音乐金榜年度二十大金曲	你不知道的事	获奖
2011	第1届全球流行音乐金榜Hit FM推崇大奖		获奖
2011	第6届kkbox数位音乐风云榜百大单曲	你不知道的事、柴米油盐酱醋茶	获奖
2010	第5届kkbox数位音乐风云榜百大专辑	心跳	获奖
2010	雪碧音乐榜最优秀视像音乐奖	畅爽开怀	获奖
2010	第10届全球华语歌曲排行榜20大金曲	柴米油盐酱醋茶	获奖
2010	蒙牛酸酸乳音乐风云榜十年盛典十年最具影响力音乐人物(港台)		获奖
2010	蒙牛酸酸乳音乐风云榜十年盛典十年港台十大金曲	唯一	获奖
2010	kkbox数位音乐风云榜		获奖
2010	2009年度北京流行音乐典礼年度最受欢迎男歌手 [54]		获奖
2010	2009年度北京流行音乐典礼年度最佳作曲（港台） [54]	春雨里洗过的太阳	获奖
2010	2009年度北京流行音乐典礼年度最佳制作人（港台） [54]		获奖
2010	2009年度北京流行音乐典礼年度全能艺人（港台） [54]		获奖
2010	2009年度北京流行音乐典礼年度金曲 [54]	春雨里洗过的太阳	获奖
2009	MusicRadio中国TOP排行榜最佳男歌手		获奖
2009	第15届新加坡金曲奖Y.E.S.93.3FM醉心龙虎榜年度顶尖金曲	心跳	获奖
2009	全球华语歌曲排行榜年度最佳男女对唱歌曲奖	另一个天堂	获奖
2009	BQ红人榜颁奖盛典年度金曲	春雨里洗过的太阳	获奖
2009	Hito流行音乐奖		获奖
2009	MusicRadio中国TOP排行榜最佳金曲	心跳	获奖
2009	MusicRadio中国TOP排行榜最佳专辑制作人		获奖
2009	无线音乐咪咕汇无线音乐最佳创作歌手 [50]		获奖
2009	无线音乐咪咕汇无线音乐全曲下载专辑最畅销男歌手 [50]		获奖
2008	第6届中国金唱奖北京2008年奥运会优秀歌曲奖	One World One Dream、站起来、点燃激情,传递梦想	获奖
2008	IFPI2007香港唱片销售大奖十大畅销国语唱片	改变自己	获奖
2008	Hito流行音乐奖Hito男歌手		获奖
2008	Music Radio中国TOP排行榜音乐创作奖港台最佳制作人	改变自己	获奖
2008	SINA MUSIC乐坛民意指数颁奖礼全国我最喜欢男歌手		获奖
2008	第8届全球华语歌曲排行榜最受欢迎对唱歌曲		获奖
2008	年度雪碧音乐榜港台金曲奖	改变自己	获奖
2008	Hito流行音乐奖Hito创作歌手		获奖
2008	Hito流行音乐奖Hito网络播人气		获奖
2008	Hito流行音乐奖年度10大金曲	Kiss Goodbye	获奖
2007	飞碟KKBOX传媒点播人气奖	Kiss Goodbye	获奖
2007	第13届全球华语音乐榜中榜港台地区最受欢迎男歌手奖		获奖
2007	新城国语力制作人大奖亚洲创作人奖		获奖
2007	Hito流行音乐奖Hito男歌手		获奖
2007	第7届音乐风云榜最佳录影带奖	花田错	获奖
2007	第2届KKBOX数位音乐风云榜年度10大专辑	盖世英雄	获奖
2007	第7届全球华语歌曲排行榜年度最受欢迎金曲	落叶归根	获奖
2007	全球华语歌曲排行榜年度最受欢迎创作歌手		获奖
2007	第2届KKBOX数位音乐风云榜年度20大单曲	Kiss Goodbye	获奖
2007	Hito流行音乐奖Hito蝉连冠军最久专辑奖	盖世英雄	获奖
2007	Hito流行音乐奖Hito年度十大金曲	Kiss Goodbye	获奖
2007	第13届全球华语音乐榜中榜港台地区最佳创作歌手奖榜		获奖
2007	第13届全球华语音乐榜中榜年度人气歌曲奖	大城小爱	获奖
2007	IFPI香港颁奖典礼十大畅销国语唱片	盖世英雄、盖世英雄演唱会DVD	获奖
2006	2006MTV封神榜音乐奖TOP20人气歌手之一		获奖
2006	第6届全球华语歌曲排行榜年度金曲	心中的日月	获奖
2006	第12届全球华语音乐榜中榜年度最佳歌曲	心中的日月	获奖
2006	第17届台湾金曲奖最佳国语男演唱人 [6]	盖世英雄	获奖
2006	第13届东方风云榜台湾地区华语五强奖		获奖
2006	TVB最佳华语歌曲	Kiss Goodbye	获奖
2006	劲歌金曲优秀选第一回最受欢迎华语歌曲奖	Kiss Goodbye	获奖
2006	Hito流行音乐颁奖典礼Hito男歌手		获奖
2006	MTV亚洲音乐大奖台湾区最受欢迎男歌手		获奖
2006	香港新城国语力亚洲专辑奖	盖世英雄	获奖
2006	MusicRadio中国TOP排行榜港台最佳男歌手		获奖
2006	MusicRadio中国TOP排行榜港台最佳制作人	花田错	获奖
2006	MusicRadio中国TOP排行榜港台年度最佳编曲	花田错	获奖
2006	Hito流行音乐颁奖典礼Hito编曲票选最受欢迎创作歌手		获奖
2006	Hito流行音乐颁奖典礼十大华语歌曲	心中的日月	获奖
2005	第5届全球华语歌曲排行榜最受欢迎男歌手		获奖
2005	香港劲歌金曲季选最受欢迎歌曲奖	Forever Love	获奖
2005	加拿大至Hit中文歌曲排行榜加拿大全国推崇男歌手奖		获奖
2005	TVB8频道金曲榜最佳监制奖	Forever Love	获奖
2005	中华音乐人交流协会2004年推荐十大单曲之一	心中的日月	获奖
2005	第3届东南劲爆音乐榜台湾地区十大金曲	心中的日月	获奖
2005	TVB8金曲榜最佳歌曲监制	Forever Love	获奖
2005	新加坡金曲奖2005亚太区域（台湾）最受欢迎男歌手奖		获奖
2005	第7届CCTV-MTV音乐盛典台湾区最佳男歌手 [34]		获奖
2005	KKBOX线上音乐风云榜颁奖典礼年度十大单曲	一首简单的歌	获奖
2005	KKBOX线上音乐风云榜颁奖典礼年度十大专辑	心中的日月	获奖
2005	KKBOX线上音乐风云榜颁奖典礼年度十大艺人		获奖
2005	KKBOX线上音乐风云榜颁奖典礼年度爆量大赏		获奖
2005	第5届全球华语歌曲排行榜25大歌曲奖 [35]	心中的日月	获奖
2005	第5届全球华语歌曲排行榜最佳作曲人奖 [200]	Forever Love [200]	获奖
2004	泰国Channel V颁奖典礼港台最佳华语歌手		获奖
2004	华语音乐传媒奖第四季十佳专辑奖	不可思议	获奖
2004	第3届日本MTV音乐录像带大奖大中华地区最具影响力艺人歌手 [130]		获奖
2004	第4届全球华语歌曲排行榜年度20大金曲奖 [131]	你不在	获奖
2004	第10届华语榜中榜颁奖典礼港台最佳男歌手 [132]		获奖
2004	第2届HIT FM2003年流行音乐年度颁奖典礼DJ年度最爱专辑奖	不可思议	获奖
2004	2003Music in中国Top排行榜音乐之声DJ推荐唱片	不可思议	获奖
2004	第15届台湾金曲奖最佳国语男演唱人奖 [133]	不可思议	提名
2004	全球华语歌曲排行榜年度最受欢迎创作歌手 [131]		获奖
2004	第2届HIT FM2003年流行音乐年度颁奖典礼年度十大华语歌曲奖	你不在	获奖
2004	第2届HIT FM2003年流行音乐年度颁奖典礼年度Hit Fm特别奖	手牵手	获奖
2004	第15届台湾金曲奖最佳唱片制作人奖 [5]	不可思议	获奖
2003	第3届全球华语歌曲榜最受欢迎创作歌手		获奖
2003	HITO流行音乐奖HITO最受欢迎男歌手		获奖
2003	第9届全球华语榜中榜最受欢迎媒体推荐奖个人奖 [134]		获奖
2003	全球华语榜中榜最佳音乐录像带奖	两个人不等于我们	获奖
2003	HITO流行音乐奖年度HITO蝉连冠军最久单曲奖		获奖
2003	HITO流行音乐奖HITO华语歌曲奖	W-H-Y	获奖
2003	第3届全球华语歌曲榜20大金曲	两个人不等于我们	获奖
2002	第4届CCTV-MTV音乐盛典台湾地区年度最佳男歌手 [135]		获奖
2002	第2届马来西亚金曲红人最佳创作男歌手	W-H-Y	获奖
2002	音乐风云榜台湾区最佳创作歌手	唯一	获奖
2002	第8届全球华语音乐榜中榜年度港台二十大金曲 [24]	唯一	获奖
2002	第2届台北流行音乐节MTV封神榜音乐奖“人气歌手Top20”		获奖
2002	第24届十大中文金曲飞跃大奖男歌手金奖 [136]		获奖
2002	第24届十大中文金曲全国最受欢迎中文流行歌曲奖银奖 [136]	唯一	获奖
2001	Channel V Top 20 台湾地区最佳创作歌手奖		获奖
2001	第1届华语歌曲排行榜最佳创作歌手		获奖
2001	CCTV-MTV音乐盛典台湾地区最佳单曲 [137]	龙的传人	获奖
2001	十大劲歌金曲杰出表现奖银奖 [138]		获奖
2001	十大劲歌金曲最受欢迎国语歌曲奖铜奖 [138]	不要害怕	获奖
2001	第23届十大中文金曲飞跃大奖男歌手铜奖 [140]		获奖
2001	第23届十大中文金曲全国最受欢迎歌手奖男歌手银奖		获奖
2001	叱咤乐坛颁奖礼四台联颁音乐大奖卓越表现大奖铜奖 [139]		获奖
2001	第23届十大中文金曲全国最受欢迎男歌手银奖 [140]		获奖
2000	新城电台新城劲爆华语歌曲	不要害怕	获奖
2000	Channel V年度Top20歌曲奖	不可能错过你 [19]	获奖
2000	第1届马来西亚亚洲金曲奖最佳男演唱人奖	永远的第一天	获奖
2000	中华音乐人交流协会十大优良专辑 [19]	不可能错过你	获奖
2000	CCTV-MTV音乐盛典台湾地区最佳男歌手		获奖
2000	第6届华语音乐榜中榜歌曲奖 [141]	julia	获奖
2000	CCTV-MTV音乐盛典台湾地区最受欢迎男歌手奖		获奖
2000	第1届亚洲中文金曲奖15大金曲	永远的第一天	获奖
2000	中华音乐人交流协会十大单曲 [19]	流泪手心	获奖
2000	精选104好友音乐奖香港地区最受欢迎之台湾歌手		获奖
2000	第22届十大中文金曲最有前途新人奖男歌手金奖 [142]		获奖
1999	第10届台湾金曲奖最佳国语男演唱人奖	公转自转	获奖
1999	新加坡金曲奖年度最佳制作人奖		获奖
1999	第10届台湾金曲奖最佳唱片制作人奖	公转自转	获奖
1999	Channel V年度Top20 歌曲奖	公转自转	获奖
1999	中华音乐人交流协会十大唱片奖	公转自转	获奖
1999	中华音乐人交流协会十大歌曲奖	公转自转	获奖
1996	《民生报》十大偶像最佳新人奖		获奖
影视类
获奖时间	奖项名称	获奖作品	获奖结果
2018	第10届澳门国际电影节最佳男主角奖 [128]	无问西东	获奖
2017	第4届丝绸之路国际电影节最佳音乐纪录片 [129]	火力全开	获奖
2011	第23届哈尔滨冰雪电影节最具商业价值新导演 [8]	恋爱通告	获奖
2011	第15届全球华语榜中榜最佳新锐导演 [56]		获奖
2001	第20届香港电影金像奖最佳新人奖 [23]	雷霆战警	提名
荣誉称号
获奖时间	奖项名称	获奖结果
2007	亚洲杰出艺人奖	获奖', 0, 4315, '{"kb_id": "60b4d637-6acb-45e2-8217-07ddb5a79cf5", "doc_id": "6a68d4b9-6e37-4c70-bd93-0adac1b60505", "kb_name": "获奖情况知识库", "filename": "6a68d4b9-6e37-4c70-bd93-0adac1b60505.txt", "chunk_total": 1}', '2026-03-12 12:20:23.053677', 'f');
INSERT INTO "public"."kb_document_chunks" VALUES ('bac00767-ad06-4dfd-828d-bbf1b19914e2', '9bd9a14f-11e8-4584-b9af-09ee6d2cc700', '60b4d637-6acb-45e2-8217-07ddb5a79cf5', '周杰伦获奖记录
音乐类
获奖时间	奖项名称	获奖作品	获奖结果
2025-8	第6届腾讯音乐娱乐盛典：年度最佳港台男歌手奖 [458]		获奖
2025-4	第17届音乐盛典咪咕汇：十大金曲奖 [459]	圣诞星	获奖
2023-8	第1届浪潮音乐大赏：年度制作奖、最佳作曲奖 [343]	最伟大的作品	获奖
2023-7	第4届腾讯音乐娱乐盛典：年度最具影响力港台男歌手奖 [460]		获奖
2023-6	2023hito流行音乐奖：年度十大华语歌曲奖 [465]	最伟大的作品	获奖
2023-6	2023hito流行音乐奖：hito男歌手奖 [465]	最伟大的作品	获奖
2023-5	第34届台湾金曲奖：年度歌曲奖 [316]	最伟大的作品	提名
2023-3	国际唱片业协会（IFPI）：2022年度“全球畅销专辑榜”冠军（含奖杯，是首位获奖的华语歌手） [26]	最伟大的作品	获奖
2022-12	亚洲流行音乐大奖2022：华语年度最佳专辑奖、年度最佳男歌手奖 [461]	最伟大的作品	提名
2022-12	亚洲流行音乐大奖2022：华语年度歌曲奖 [462]	最伟大的作品	提名
2022-12	亚洲流行音乐大奖2022：华语年度制作奖、最佳音乐录影带奖 [461]	最伟大的作品	提名
2021-12	第13届华语金曲奖：年度国语歌曲奖 [468]	Mojito	获奖
2021-5	第32届台湾金曲奖：最佳单曲制作人奖 [302]	Mojito	提名
2021-1	中国歌曲TOP排行榜：最佳男歌手奖 [141]		获奖
2020-7	第27届东方风云榜：动感101年度金曲奖 [135]	说好不哭	获奖
2019-12	第13届音乐盛典咪咕汇：年度十大金曲奖 [134]	说好不哭	获奖
2019-8	2019华人歌曲音乐盛典：港台及海外地区年度最受欢迎男歌手奖 [466]		获奖
2019-8	2019华人歌曲音乐盛典：年度金曲奖 [466]	不爱我就拉倒	获奖
2018-8	2018华人歌曲音乐盛典：港台及海外地区年度最受欢迎男歌手奖 [467]		获奖
2018-8	2018华人歌曲音乐盛典：年度金曲奖 [467]	等你下课	获奖
2017-8	2017华语金曲奖致敬香港回归20周年颁奖盛典：年度最佳国语专辑奖 [281]	周杰伦的床边故事	获奖
2017-7	第1届唱工委音乐奖：年度专辑奖、最佳流行专辑奖 [469]	周杰伦的床边故事	获奖
2017-7	第1届唱工委音乐奖：最佳作曲奖 [469]	告白气球	获奖
2017-7	第1届唱工委音乐奖：最佳音乐录影带奖 [469]	床边故事	获奖
2017-6	2017hito流行音乐奖：hito男歌手奖 [126]		获奖
2017-6	2017hito流行音乐奖：年度十大华语歌曲奖 [126]	不该	获奖
2017-5	第28届台湾金曲奖：最佳国语男歌手奖 [279]	周杰伦的床边故事	提名
2017-5	第28届台湾金曲奖：最佳年度歌曲奖 [279]	告白气球	提名
2017-5	第28届台湾金曲奖：最佳音乐录影带奖 [279]	床边故事	提名
2016-12	第10届音乐盛典咪咕汇：年度港台最受欢迎男歌手奖、十年最佳男歌手奖、十年最具影响力歌手奖 [471]		获奖
2016-12	第10届音乐盛典咪咕汇：十年十大金曲奖 [471]	稻香	获奖
2016-12	第10届音乐盛典咪咕汇：年度十大金曲奖 [471]	告白气球	获奖
2016-6	2016hito流行音乐奖：hito冠军王奖、最受欢迎全球华语歌手奖 [472]		获奖
2016-6	2016hito流行音乐奖：hito长寿专辑奖 [472]	哎呦，不错哦	获奖
2016-6	2016hito流行音乐奖：年度十大华语歌曲奖 [472]	算什么男人	获奖
2016-3	2016QQ音乐巅峰盛典：年度音乐全能艺人奖、QQ音乐年度巅峰人气歌手奖、年度最具影响力演唱会奖 [120]		获奖
2015-12	第9届音乐盛典咪咕汇：年度最畅销专辑奖 [475]	哎呦，不错哦	获奖
2015-6	第26届台湾金曲奖：最佳国语专辑奖、最佳专辑制作人奖 [116]	哎呦，不错哦	提名
2015-5	第5届全球流行音乐金榜：年度二十大金曲奖 [474]	鞋子特大号	获奖
2015-4	第19届全球华语榜中榜：亚洲影响力最受欢迎全能华语艺人奖、华语乐坛跨时代实力创作人奖 [264]		获奖
2015-3	2015QQ音乐年度盛典：最佳全能艺人奖 [473]		获奖
2015-3	2015QQ音乐年度盛典：年度畅销数字专辑奖 [473]	哎哟，不错哦	获奖
2014-12	第8届无线音乐盛典咪咕汇：年度最佳人气王奖 [477]		获奖
2014-12	第8届无线音乐盛典咪咕汇：年度最畅销十大金曲奖 [477]	红尘客栈	获奖
2014-6	2014hito流行音乐奖：Hit FM年度推崇艺人奖 [479]		获奖
2014-6	2014hito流行音乐奖：hito电影主题曲奖 [479]	哪里都是你	获奖
2014-6	2014hito流行音乐奖：年度十大华语歌曲奖 [479]	明明就	获奖
2014-4	第14届音乐风云榜：港台最受欢迎男歌手奖 [478]		获奖
2014-3	2014QQ音乐年度盛典：港台最受欢迎男歌手奖、全能艺人奖 [476]		获奖
2014-3	2014QQ音乐年度盛典：最佳影视原声带奖 [476]	天台爱情	获奖
2014-1	第36届十大中文金曲：优秀流行国语歌曲银奖 [256]	红尘客栈	获奖
2013-12	第7届无线音乐盛典咪咕汇：年度最畅销专辑奖 [480]	12新作	获奖
2013-12	第7届无线音乐盛典咪咕汇：年度最佳歌手奖 [480]		获奖
2013-11	第56届亚太影展：最佳音乐奖 [483]	天台爱情	提名
2013-10	第13届全球华语歌曲排行榜：二十大金曲奖 [255]	红尘客栈	获奖
2013-10	第13届全球华语歌曲排行榜：最佳专辑制作人奖 [255]	12新作	获奖
2013-5	第24届台湾金曲奖：最佳国语专辑奖、最佳国语男歌手奖、最佳专辑制作人奖 [104]	12新作	提名
2013-4	第13届音乐风云榜：港台最受欢迎男歌手奖 [481]		获奖
2013-4	第3届全球流行音乐金榜：年度最佳男歌手奖 [482]		获奖
2012-12	第6届无线音乐盛典咪咕汇：年度特别贡献奖、年度最受欢迎港台男歌手奖 [487]		获奖
2012-12	第6届无线音乐盛典咪咕汇：年度最畅销金曲奖 [487]	皮影戏	获奖
2012-12	百度音乐十周年盛典：百度音乐10年最佳男歌手奖、10年音乐领袖人物奖、10年最具传唱力歌手奖 [488]		获奖
2012-5	第23届台湾金曲奖：最佳国语男歌手奖 [101]	惊叹号！	提名
2012-5	第23届台湾金曲奖：最佳编曲人奖 [101]	水手怕水	提名
2012-5	2012hito流行音乐奖：最受欢迎全球华语歌手奖、全球传媒大奖 [486]		获奖
2012-5	2012hito流行音乐奖：Hit FM听众最爱歌曲奖 [486]	水手怕水	获奖
2012-4	第16届全球华语榜中榜：亚洲影响力最佳华语艺人奖、榜中榜最佳数字音乐奖 [251]		获奖
2012-4	第16届全球华语榜中榜：港台地区最佳专辑奖 [252]	惊叹号！	获奖
2012-2	2011年度中国原创音乐流行榜：台湾地区最优秀专辑奖、亚太地区最优秀创作歌手奖、全国最杰出全能艺人奖、亚太区最受欢迎男歌手奖、最优秀舞台演绎奖 [485]	惊叹号！	获奖
2012-2	2011年度中国原创音乐流行榜：最优秀合唱歌曲奖 [485]	天地一斗	获奖
2012-2	2011年度中国原创音乐流行榜：港台金曲奖 [485]	惊叹号	获奖
2012-1	2011年度北京流行音乐典礼：港台地区年度最受欢迎男歌手奖、年度全能艺人奖 [489]		获奖
2012-1	2011年度北京流行音乐典礼：港台地区年度最佳单曲制作人奖 [489]	皮影戏	获奖
2011-10	第48届台湾电影金马奖：最佳原创电影歌曲奖 [495]	阿爸	提名
2011-6	第22届台湾金曲奖：最佳国语专辑奖、最佳国语男歌手奖 [19]	跨时代	获奖
2011-6	第5届无线音乐盛典咪咕汇：年度最高销量港台男歌手奖、年度试听超人气男歌手奖、无线音乐搜索超人气男歌手奖 [490]		获奖
2011-6	第5届无线音乐盛典咪咕汇：无线音乐最畅销创作金曲奖 [490]	烟花易冷	获奖
2011-5	第22届台湾金曲奖：最佳专辑制作人奖 [247]	跨时代	提名
2011-5	第22届台湾金曲奖：最佳年度歌曲奖 [247]	超人不会飞	提名
2011-5	第22届台湾金曲奖：最佳作曲人奖 [247]	烟花易冷	提名
2011-5	中华音乐人交流协会：年度十大专辑奖 [496]	跨时代	获奖
2011-5	中华音乐人交流协会：年度十大单曲奖 [496]	阿爸	获奖
2011-4	第1届全球流行音乐金榜：年度最佳中文专辑奖、年度最受欢迎男歌手奖、全球华人音乐杰出艺人奖、加拿大以及洛杉矶中文电台推崇大奖 [241]	跨时代	获奖
2011-4	第1届全球流行音乐金榜：年度20大金曲奖 [241]	超人不会飞	获奖
2011-4	第15届全球华语榜中榜：无线音乐年度特别大奖 [491]		获奖
2011-4	2010年度中国TOP排行榜：港台最佳男歌手奖 [492]		获奖
2011-4	第3届新加坡e乐大赏：e乐最佳男歌手奖 [494]	跨时代	获奖
2011-1	2010年度北京流行音乐典礼：港台年度最受欢迎男歌手奖 [493]		获奖
2011-1	2010年度北京流行音乐典礼：港台地区年度最佳专辑奖 [493]	跨时代	获奖
2010-12	第10届全球华语歌曲排行榜：年度20大金曲奖 [498]	超人不会飞	获奖
2010-12	第10届全球华语歌曲排行榜：最受欢迎男歌手五强奖 [498]	跨时代	获奖
2010-4	第10届音乐风云榜：港台地区十年最具影响力人物奖 [499]		获奖
2010-4	第10届音乐风云榜：十年十大港台金曲奖 [499]	稻香	获奖
2010-4	2010福布斯中国名人榜：第二名 [502]		提名
2010-3	第14届全球华语榜中榜：12530无线音乐年度大奖 [501]		获奖
2010-2 [587]	2009年度中国原创音乐流行榜：亚太地区最受欢迎男歌手奖、最优秀创作歌手奖、最杰出全能艺人奖 [500]		获奖
2010-2 [587]	2009年度中国原创音乐流行榜：全国至尊金曲奖 [500]	说好的幸福呢	获奖
2010-1	2009年度KKBOX数位音乐风云榜：年度十大风云歌手奖 [592]		获奖
2009-11	第9届全球华语歌曲排行榜：年度20大金曲奖 [504]	稻香	获奖
2009-6	第20届台湾金曲奖：最佳国语男歌手奖 [18]	魔杰座	获奖
2009-6	第20届台湾金曲奖：最佳年度歌曲奖 [18]	稻香	获奖
2009-6	第20届台湾金曲奖：最佳音乐录影带奖 [18]	魔术先生	获奖
2009-5	第20届台湾金曲奖：最佳国语专辑奖 [503]	魔杰座	提名
2009-5	第20届台湾金曲奖：最佳作词人奖、最佳作曲人奖 [503]	稻香	获奖
2009-5	中华音乐人交流协会：年度十大专辑奖 [505]	魔杰座	获奖
2009-5	中华音乐人交流协会：年度十大单曲奖 [505]	魔术先生	获奖
2009-4	2008年度中国TOP排行榜：年度最畅销歌手奖 [506]	稻香	获奖
2009-4	2008年度中国TOP排行榜：港台地区年度金曲奖 [585]	稻香	获奖
2009-2	2008年度中国原创音乐流行榜：港台地区歌曲奖 [584]	稻香	获奖
2009-2	2008年度KKBOX数位音乐风云榜：年度十大单曲奖 [588]	说好的幸福呢, 稻香, 我不配	获奖
2009-2	2008年度KKBOX数位音乐风云榜：年度十大专辑奖 [588]	魔杰座	获奖
2009-1	2008年度北京流行音乐典礼：港台年度最受欢迎男歌手奖、年度最佳创作歌手奖、年度全能艺人奖 [507]		获奖
2009-1	2008年度北京流行音乐典礼：港台年度最佳制作人奖 [508-509]	魔杰座	获奖
2009-1	2008年度北京流行音乐典礼：年度金曲奖 [508]	稻香	获奖
2008-12	2008年度TVB8金曲榜颁奖典礼：最佳音乐录影带演绎奖、最佳歌曲监制奖 [514]	牛仔很忙	获奖
2008-12	第3届无线音乐年度盛典咪咕汇：无线音乐最高销量男歌手奖、无线音乐最佳创作歌手奖 [515]		获奖
2008-12	第3届无线音乐年度盛典咪咕汇：无线最畅销电影金曲奖 [515]	彩虹	获奖
2008-11	世界音乐大奖：中国最畅销艺人奖 [12]		获奖
2008-10	第8届全球华语歌曲排行榜：年度20大金曲奖 [512]	不能说的秘密	获奖
2008-10	第45届台湾电影金马奖：最佳原创电影歌曲奖 [517]	周大侠	提名
2008-7	第19届台湾金曲奖：最佳年度歌曲奖、最佳作曲人奖 [221]	青花瓷	获奖
2008-7	第19届台湾金曲奖：演奏类最佳专辑制作人奖 [221]	不能说的秘密	获奖
2008-7	第19届台湾金曲奖：演奏类最佳作曲人奖 [221]	琴房	获奖
2008-5	第19届台湾金曲奖：最佳国语专辑奖 [510]	我很忙	提名
2008-4	2007年度中国TOP排行榜：年度最畅销男歌手奖、最佳唱作歌手奖 [513]		获奖
2008-4	2007年度中国TOP排行榜：港台年度最佳唱片奖 [513]	我很忙	获奖
2008-1	第30届十大中文金曲：优秀流行国语歌曲奖 [511]	不能说的秘密	获奖
2008-1	第2届无线音乐年度盛典：年度最高销量男歌手奖 [516]		获奖
2008-1	第2届无线音乐年度盛典：年度最畅销季度金曲奖 [516]	迷迭香	获奖
2008-1	第2届无线音乐年度盛典：无线音乐首发劲爆金曲奖 [516]	不能说的秘密	获奖
2007-12	第44届台湾电影金马奖：最佳原创电影歌曲奖 [216]	不能说的秘密	获奖
2007-12	第44届台湾电影金马奖：最佳原创电影音乐奖 [527]	不能说的秘密	提名
2007-10	第7届全球华语歌曲排行榜：二十大最受欢迎金曲奖 [533]	菊花台	获奖
2007-8	2007新城国语力颁奖礼：新城国语力亚洲专辑奖 [535]	依然范特西	获奖
2007-6	第18届台湾金曲奖：最佳单曲制作人奖 [219]	霍元甲	获奖
2007-6	第18届台湾金曲奖：最佳音乐录影带导演奖 [71]	红模仿	提名
2007-6	第18届台湾金曲奖：最佳年度歌曲奖 [71]	千里之外	提名
2007-6	第7届华语音乐传媒大奖：年度国语歌曲奖、最佳企划奖 [530]	千里之外	获奖
2007-6	中华音乐人交流协会：年度十大专辑奖 [538]	依然范特西	获奖
2007-6	中华音乐人交流协会：年度十大单曲奖 [538]	菊花台	获奖
2007-4	第26届香港电影金像奖：最佳原创电影歌曲奖（同时凭《霍元甲》提名） [207]	菊花台	获奖
2007-4	第7届音乐风云榜：港台地区最佳男歌手奖、港台地区最受欢迎男歌手奖、港台地区最佳唱作人奖、港台地区最佳专辑奖 [201]	依然范特西	获奖
2007-4	第7届音乐风云榜：港台地区最佳歌曲奖 [534]	千里之外	获奖
2007-4	第7届音乐风云榜：最佳影视歌曲奖 [534]	菊花台	获奖
2007-4	第7届音乐风云榜：港台地区最佳作词奖 [201]	夜的第七章	获奖
2007-3	IFPI香港唱片销量大奖：十大销量国语唱片奖 [210]	我很忙, 黄金甲	获奖
2007-1	第29届十大中文金曲：优秀流行歌手奖 [529]		获奖
2007-1	第29届十大中文金曲：全国最受欢迎中文歌曲奖 [198]	千里之外	获奖
2007-1	第1届无线音乐颁奖盛典：年度最畅销首发单曲奖 [209]	黄金甲	获奖
2007	世界音乐大奖：中国最畅销艺人奖 [12]		获奖
2006-10	第6届全球华语歌曲排行榜：二十大最受欢迎金曲奖、最佳编曲奖 [537]	夜曲	获奖
2006-10	第6届全球华语歌曲排行榜：最受欢迎对唱金曲奖 [537]	珊瑚海	获奖
2006-10	第8届CCTV-MTV音乐盛典：亚洲地区最杰出艺人奖 [540]		获奖
2006-8	2006新城国语力颁奖礼：新城国语力亚洲专辑奖 [541]	十一月的萧邦	获奖
2006-5	中华音乐人交流协会：年度十大专辑奖 [194]	11月的萧邦	获奖
2006-4	第6届音乐风云榜：港台最受欢迎男歌手奖 [539]		获奖
2006-4	第6届音乐风云榜：三地联颁奖-男歌手奖 [539]		获奖
2006-4	第6届音乐风云榜：三地联颁奖-最佳专辑奖 [539]	十一月的萧邦	获奖
2006-4	2005年度中国TOP排行榜：港台年度金曲奖 [542]	夜曲	获奖
2006-4	2005年度北京流行音乐典礼：港台最受欢迎男歌手奖、年度最佳专辑奖 [543-544]		获奖
2006-4	2005年度北京流行音乐典礼：年度最受欢迎金曲奖 [544]	夜曲	获奖
2006-3	第25届香港电影金像奖：最佳原创电影歌曲奖 [536]	飘移	提名
2006-2	“华众曲宠”2006TVBS华语金曲榜：最佳男歌手奖、传媒大奖、最佳专辑奖 [545]		获奖
2006-1	第28届十大中文金曲：全年最高销量男歌手奖、优秀流行歌手奖 [206]		获奖
2006-1	第12届全球华语榜中榜：港台地区最佳男歌手奖、最佳创作歌手奖、最受欢迎男歌手奖 [192]		获奖
2006-1	第12届全球华语榜中榜：年度最佳歌曲奖、最受欢迎音乐录影带奖 [192]	夜曲	获奖
2006-1	2006hito流行音乐奖：票选最受欢迎男歌手奖、亚洲传媒大奖、年度hito创作歌手奖 [552]		获奖
2006-1	2006hito流行音乐奖：年度十大华语歌曲奖、年度听众最爱歌曲奖 [553]	夜曲	获奖
2006	世界音乐大奖：中国最畅销艺人奖 [12]		获奖
2005-12	2005新城劲爆颁奖礼：新城全球劲爆歌手奖、新城全球劲爆创作歌手奖、新城全国投选劲爆歌手奖 [191]		获奖
2005-12	2005新城劲爆颁奖礼：新城劲爆国语歌曲奖 [191]	夜曲	获奖
2005-12	2005新城劲爆颁奖礼：新城劲爆创作大碟奖 [191]	11月的萧邦	获奖
2005-11	第12届新加坡金曲奖：最受欢迎男歌手奖、亚太最受推崇男歌手奖 [549]		获奖
2005-11	第42届台湾电影金马奖：最佳原创电影歌曲奖 [551]	飘移	提名
2005-9	第5届全球华语歌曲排行榜：台湾地区杰出艺人奖 [548]		获奖
2005-9	第5届全球华语歌曲排行榜：年度25大歌曲奖 [548]	七里香	获奖
2005-8	2005新城国语力颁奖礼：新城国语力亚洲大碟奖 [556]	七里香	获奖
2005-5	第16届台湾金曲奖：最佳作曲人奖 [59]	七里香	提名
2005-5	第16届台湾金曲奖：最佳流行音乐演唱专辑奖、最佳国语男歌手奖 [59]	七里香	提名
2005-4	2004年度中国TOP排行榜：港台年度金曲奖 [557]	七里香	获奖
2005-4	2004年度中国TOP排行榜：港台最受欢迎男歌手奖 [557]		获奖
2005-4	2004年度中国TOP排行榜：年度最畅销唱片奖、港台年度最佳制作人奖 [557]	七里香	获奖
2005-3	第5届音乐风云榜：港台地区年度最佳男歌手奖、台湾地区最受欢迎男歌手奖 [550]		获奖
2005-3	第5届音乐风云榜：港台地区年度最佳专辑奖 [550]	七里香	获奖
2005-3	第5届音乐风云榜：港台地区十大金曲奖 [550]	七里香	获奖
2005-3	第5届音乐风云榜：最佳粤语作曲奖 [550]	献世	获奖
2005-2	第4届MTV亚洲大奖：中国台湾地区最受欢迎歌手奖 [29]		获奖
2005-1	第27届十大中文金曲：全国最受欢迎男歌手奖（银奖）、优秀流行歌手奖 [182]		获奖
2005-1	第27届十大中文金曲：十大金曲奖、优秀流行国语歌曲奖（金奖） [182]	七里香	获奖
2005-1	第11届全球华语音乐榜中榜：港台最佳男歌手奖、港台最受欢迎男歌手奖、最佳创作歌手奖 [184]		获奖
2005-1	第11届全球华语音乐榜中榜：港台年度最佳歌曲奖 [184]	七里香	获奖
2005-1	2005hito流行音乐奖：hito男歌手奖、年度华语歌曲奖、DJ最爱专辑奖、听众最爱歌曲奖、hito创作歌手奖 [554]		获奖
2005-1	第12届中国歌曲排行榜：年度最受欢迎港台地区男歌手奖 [558]		获奖
2005-1	第12届中国歌曲排行榜：最受欢迎港台地区歌曲奖 [558]	七里香	获奖
2004-12	2004年度TVB8金曲榜颁奖典礼：最佳作曲奖、最佳歌曲监制奖 [562]	七里香	获奖
2004-9	世界音乐大奖：中国区最畅销艺人奖 [11]		获奖
2004-9	第11届新加坡金曲奖：十大金曲奖、最佳唱片制作奖、最受欢迎男歌手奖 [161]		获奖
2004-9	第4届全球华语歌曲排行榜：最受欢迎男歌手奖、台湾地区最佳艺人奖、最受欢迎创作歌手奖 [559]		获奖
2004-9	第4届全球华语歌曲排行榜：年度最受欢迎专辑奖 [167]	叶惠美	获奖
2004-9	第4届全球华语歌曲排行榜：年度20大金曲奖 [559]	晴天	获奖
2004-8	2004新城国语力颁奖礼：新城国语力亚洲歌手奖、亚洲创作歌手奖、国语力歌王奖 [532]		获奖
2004-8	2004新城国语力颁奖礼：新城国语力亚洲大碟奖 [532]	叶惠美	获奖
2004-8	2004新城国语力颁奖礼：新城国语力歌曲奖 [532]	回到过去	获奖
2004-7	第4届华语音乐传媒大奖：年度艺人奖 [563]		获奖
2004-7	第4届华语音乐传媒大奖：最佳作曲人奖、十大华语歌曲奖 [563]	东风破	获奖
2004-7	第4届华语音乐传媒大奖：十大华语唱片奖 [563]	叶惠美	获奖
2004-5	第15届台湾金曲奖：最佳流行音乐演唱专辑奖 [166]	叶惠美	获奖
2004-4	IFPI香港唱片销量大奖：十大销量国语唱片奖、最高销量国语唱片奖 [161]	叶惠美	获奖
2004-3	中华音乐人交流协会：年度十大专辑奖 [161]	叶惠美	获奖
2004-3	中华音乐人交流协会：年度十大单曲奖 [161]	东风破, 梯田	获奖
2004-3	第15届台湾金曲奖：最佳国语男演唱人奖、最佳专辑制作人奖 [560]	叶惠美	提名
2004-3	第15届台湾金曲奖：最佳作曲人奖 [560]	东风破	提名
2004-3	第15届台湾金曲奖：最佳作词人奖 [560]	梯田	提名
2004-3	第4届音乐风云榜：台湾地区最受欢迎男歌手奖、年度风云奖、年度港台及海外华人最佳制作人奖 [176]		获奖
2004-3	第4届音乐风云榜：港台地区年度最佳专辑奖 [176]	叶惠美	获奖
2004-3	第4届音乐风云榜：港台地区十大金曲奖 [176]	晴天, 三年二班, 东风破	获奖
2004-3	第11届中国歌曲排行榜：港台最受欢迎男歌手奖 [57]		获奖
2004-3	第11届中国歌曲排行榜：最受欢迎港台地区歌曲奖 [57]	东风破	获奖
2004-2	第2届hito流行音乐奖：年度hito男歌手奖、年度票选最受欢迎男歌手奖 [171]		获奖
2004-2	第2届hito流行音乐奖：年度亚洲传媒推荐专辑奖 [171]	叶惠美	获奖
2004-2	第2届hito流行音乐奖：年度hito华语歌曲奖 [171]	晴天	获奖
2004-1	第10届全球华语榜中榜：港台最佳创作歌手奖 [170]		获奖
2004-1	第10届全球华语榜中榜：港台地区最佳歌曲奖 [170]	晴天	获奖
2004	2003年度中国TOP排行榜：港台地区年度金曲奖 [565]	东风破	获奖
2004	2003年度中国TOP排行榜：港台年度最佳制作人奖 [565]	布拉格广场	获奖
2004	2003年度叱咤乐坛流行榜颁奖典礼：叱咤乐坛唱作人金奖 [161]		获奖
2003-12	第26届十大中文金曲：全年最高销量男歌手奖、全国最受欢迎男歌手奖（银奖）、优秀流行歌手奖 [561]		获奖
2003-11	第4届中国金唱片奖：引进版类专辑奖 [564]	八度空间	获奖
2003-11	第4届中国金唱片奖：引进版类新人奖 [564]		获奖
2003-9	第3届全球华语歌曲排行榜：台湾地区杰出歌手奖 [531]		获奖
2003-9	第10届新加坡金曲奖：年度最畅销男歌手奖、亚太最受推崇男歌手奖、最受欢迎男歌手奖 [158]	八度空间	获奖
2003-9	第5届CCTV-MTV音乐盛典：台湾地区年度最佳男歌手奖 [567]		获奖
2003-8	新城国语力颁奖礼：新城国语力最佳创作歌手奖 [161]		获奖
2003-7	第3届华语流行乐传媒大奖：2002年度艺人奖、我最喜爱的华语歌手奖、最佳作曲人奖 [526]		获奖
2003-7	第3届华语流行乐传媒大奖：年度十大华语歌曲奖 [526]	半岛铁盒	获奖
2003-7	第3届华语流行乐传媒大奖：年度十大华语唱片奖 [526]	八度空间	获奖
2003-4	G-Music风云榜白金音乐奖：十大金碟奖、白金大碟奖 [157]	八度空间	获奖
2003-3	第14届台湾金曲奖：最佳流行音乐演唱专辑奖、最佳专辑制作人奖 [161]	八度空间	提名
2003-3	第3届音乐风云榜：港台年度最佳唱作人奖、年度风云奖 [163]		获奖
2003-3	第3届音乐风云榜：港台年度十大金曲奖 [163]	暗号	获奖
2003-1	第25届十大中文金曲：全年最高销量男歌手奖、全国最受欢迎男歌手奖（银奖）、优秀流行歌手奖 [524]		获奖
2003-1	第25届十大中文金曲：优秀国语歌曲金奖 [524]	安静	获奖
2003-1	2002年度十大劲歌金曲颁奖典礼：最受欢迎国语歌曲奖（金奖） [546]	回到过去	获奖
2003-1	2002年度十大劲歌金曲颁奖典礼：最佳歌曲监制奖 [546]	安静	获奖
2003-1	第2届MTV亚洲大奖：中国台湾地区最受欢迎歌手奖 [555]		获奖
2003-1	第1届hito流行音乐奖：hito最佳男歌手奖 [566]		获奖
2003-1	第1届hito流行音乐奖：hito华语歌曲奖 [566]	暗号	获奖
2003-1	第1届hito流行音乐奖：hito男生最爱K歌奖、hito长寿单曲奖 [566]	回到过去	获奖
2003	2002年度中国TOP排行榜：最受欢迎台湾男歌手奖、港台年度最佳创作歌手奖、港台年度最受欢迎唱片奖 [525]	八度空间	获奖
2003	2002年度中国TOP排行榜：港台十大金曲奖 [525]	半岛铁盒	获奖
2002-12	2002年度TVB8金曲榜颁奖礼：全球传媒男歌手奖 [547]		获奖
2002-12	2002年度TVB8金曲榜颁奖礼：最佳作曲奖、金曲奖 [547]	开不了口	获奖
2002-10	2002年度CASH金帆音乐奖：最佳唱片奖 [589]	范特西	获奖
2002-10	2002年度CASH金帆音乐奖：最佳男歌手演绎奖 [590]	开不了口	获奖
2002-9	2002年度新加坡金曲奖：年度最畅销专辑奖、年度最畅销男歌手专辑奖、最佳唱片制作奖 [155]	范特西	获奖
2002-9	2002年度新加坡金曲奖：亚太最受推崇男歌手奖 [155]		获奖
2002-9	2002年度新加坡金曲奖：YES933醉心龙虎榜顶尖金曲奖 [155]	世界末日	获奖
2002-8	第2届全球华语歌曲排行榜：最受欢迎创作歌手、最佳制作人奖、杰出歌手奖 [162]		获奖
2002-8	第2届全球华语歌曲排行榜：最佳专辑奖 [162]	范特西	获奖
2002-8	第2届全球华语歌曲排行榜：年度20大金曲奖 [162]	安静	获奖
2002-5	第1届MTV日本音乐录影带大奖：亚洲最杰出艺人奖 [161]		获奖
2002-5	第13届台湾金曲奖：最佳流行音乐演唱专辑奖、最佳专辑制作人奖 [38]	范特西	获奖
2002-5	第13届台湾金曲奖：最佳作曲人奖 [38]	爱在西元前	获奖
2002-5	第13届台湾金曲奖：最佳国语男演唱人奖 [523]	范特西	提名
2002-4	中华音乐人交流协会：年度十大专辑奖 [591]	范特西	获奖
2002-4	中华音乐人交流协会：年度十大单曲奖 [591]	威廉古堡	获奖
2002-3	第2届音乐风云榜：台湾地区年度最佳男歌手奖、年度杰出新人奖 [522]		获奖
2002-3	第2届音乐风云榜：台湾地区年度最佳专辑奖 [522]	范特西	获奖
2002-3	第2届音乐风云榜：年度十大杰出金曲奖 [522]	简单爱	获奖
2002-3	第2届音乐风云榜：港台年度最佳对唱奖 [522]	屋顶	获奖
2002-1	第8届全球华语音乐榜中榜：港台最受欢迎男歌手奖、台湾地区新生代创作歌手奖、特别推荐新浪潮歌手奖 [521]		获奖
2002-1	2001年度十大劲歌金曲颁奖典礼：最受欢迎唱作歌星奖（金奖）、最受欢迎男新人奖（金奖）、四台联颁音乐大奖卓越表现奖（铜奖） [49]		获奖
2002-1	2001年度十大劲歌金曲颁奖典礼：最受欢迎国语歌曲奖（金奖） [49]	开不了口	获奖
2002-1	第24届十大中文金曲：最有前途新人男歌手奖（金奖） [154]		获奖
2002-1	第24届十大中文金曲：优秀国语歌曲金奖 [154]	星晴	获奖
2001-12	2001年度新城劲爆颁奖礼：新城劲爆新登场海外歌手奖 [520]		获奖
2001-12	2001年度新城劲爆颁奖礼：新城劲爆国语歌曲奖 [520]	星晴	获奖
2001-12	2001年度新城劲爆颁奖礼：新城劲爆卡拉OK歌曲奖 [520]	龙卷风	获奖
2001-11	第1届MTV亚洲大奖：台湾地区最受欢迎歌手奖 [161]		提名
2001-5	第1届MTV封神榜颁奖典礼：十大人气歌手奖 [161]		获奖
2001-2	中华音乐人交流协会：年度十大单曲奖 [519]	印地安老斑鸠	获奖
2001	第12届台湾金曲奖：最佳流行音乐演唱专辑奖 [40]	Jay	获奖
2001	第12届台湾金曲奖：最佳作曲人奖 [44]	可爱女人	提名
2001	第12届台湾金曲奖：最佳新人奖、最佳专辑制作人奖 [45]	Jay	提名
2001	第一届全球华语歌曲排行榜：最佳新人奖 [45]		获奖
2001	第一届全球华语歌曲排行榜：年度金曲奖 [45]	星晴	获奖
2001	2000年度TVB8金曲榜颁奖典礼：最佳男新人金奖、最佳制作人奖 [45]		获奖
2001	2000年度TVB8金曲榜颁奖典礼：年度金曲奖 [45]	星晴	获奖
2001	第1届马来西亚金曲红人颁奖典礼：十大华语歌曲、最佳作曲人奖 [45]	黑色幽默	获奖
2001	叱咤乐坛流行榜颁奖典礼：叱咤乐坛生力军男歌手奖（金奖）、叱咤乐坛唱作人银奖 [50]		获奖
2001	叱咤乐坛流行榜颁奖典礼：叱咤乐坛我最喜爱的歌曲奖 [50]	开不了口	获奖
2001	IFPI香港唱片销量大奖：十大销量国语唱片奖 [45]	Jay, 范特西	获奖
社会类
获奖时间	奖项名称	获奖结果
2021-8	2021福布斯中国名人榜：第五名 [463]	获奖
2020-8	2020福布斯中国名人榜：第四名 [464]	获奖
2017-9	2017福布斯中国名人榜：第九名 [470]	获奖
2015-5	2015福布斯中国名人榜：第二名 [265]	获奖
2014-5	2014福布斯中国名人榜：第三名 [263]	获奖
2013-4	2013福布斯中国名人榜：第二名 [484]	获奖
2012-5	2012福布斯中国名人榜：第一名 [253]	获奖
2011-5	2011福布斯中国名人榜：第二名 [497]	获奖
影视类
获奖时间	奖项名称	获奖作品	获奖结果
2011-5	第20届美国MTV电影奖：最具突破演员奖 [248]	青蜂侠	提名
2008-8	第29届大众电影百花奖：最佳男配角奖 [518]	满城尽带黄金甲	提名
2007-12	第44届台湾电影金马奖：年度台湾杰出电影奖 [216]	不能说的秘密	获奖
2007-6	第16届上海影评人奖：最佳男演员奖 [205]	满城尽带黄金甲	获奖
2007-4	第26届香港电影金像奖：最佳男配角奖 [528]	满城尽带黄金甲	提名
2006-4	第25届香港电影金像奖：最佳新演员奖 [14]	头文字D	获奖
2005-11	第42届台湾电影金马奖：最佳新演员奖 [185]	头文字D	获奖', 0, 10478, '{"kb_id": "60b4d637-6acb-45e2-8217-07ddb5a79cf5", "doc_id": "9bd9a14f-11e8-4584-b9af-09ee6d2cc700", "kb_name": "获奖情况知识库", "filename": "9bd9a14f-11e8-4584-b9af-09ee6d2cc700.txt", "chunk_total": 1}', '2026-03-12 12:18:21.695661', 'f');
INSERT INTO "public"."kb_document_chunks" VALUES ('0c311068-4069-4134-b1a9-21860b9050be', '8d2ae925-aaa2-4362-bac0-09cb5470082a', '60b4d637-6acb-45e2-8217-07ddb5a79cf5', '你好，你是谁？
我是周杰伦', 0, 9, '{"kb_id": "60b4d637-6acb-45e2-8217-07ddb5a79cf5", "doc_id": "8d2ae925-aaa2-4362-bac0-09cb5470082a", "kb_name": "获奖情况知识库", "filename": "8d2ae925-aaa2-4362-bac0-09cb5470082a.txt", "chunk_total": 1}', '2026-03-13 15:40:09.220769', 'f');
INSERT INTO "public"."kb_document_chunks" VALUES ('4c0be454-34f9-40e1-853f-fde4dec0bc7e', '741e7288-9a3e-48fa-b808-8ecc62bc360f', '60b4d637-6acb-45e2-8217-07ddb5a79cf5', '你好，你是谁？
我是周杰伦', 0, 9, '{"kb_id": "60b4d637-6acb-45e2-8217-07ddb5a79cf5", "doc_id": "741e7288-9a3e-48fa-b808-8ecc62bc360f", "kb_name": "获奖情况知识库", "filename": "741e7288-9a3e-48fa-b808-8ecc62bc360f.txt", "chunk_total": 1}', '2026-03-13 15:43:37.551927', 'f');
INSERT INTO "public"."kb_document_chunks" VALUES ('bef6761c-cc77-40eb-8e37-0752695b7f5e', 'e3ae5786-72d1-4ed5-b17f-b11074d60d17', '60b4d637-6acb-45e2-8217-07ddb5a79cf5', 'Hebe获奖情况
音乐类
获奖时间	奖项名称	获奖作品	获奖结果
2021-8-21	第32届台湾金曲奖最佳华语女歌手奖 [89]	无人知晓	获奖
2021-1-23	第二届腾讯音乐娱乐盛典 年度最具影响力港台女歌手 [83]		获奖
2017-6-4	FM最爱歌手、HITO女歌手 [62]		获奖
MusicRadio中国TOP排行榜
获奖时间	奖项名称	获奖作品	获奖结果
2017-06-21	第十四届港台地区最受欢迎女歌手		获奖
2014-04-26	第十一届港台地区MusicRadio音乐之声点播冠军	你就不要想起我	获奖
2014-04-26	第十一届年度最佳金曲	你就不要想起我	获奖
2012-04-23	第十届年度最受欢迎女歌手		获奖
2012-04-23	第十届港台地区年度金曲	My Love	获奖
2011-04-24	第九届港台地区年度最受欢迎新人		获奖
2011-04-24	第九届港台地区年度全能艺人		获奖
2011-04-24	第九届港台地区年度最佳金曲	Love!	获奖
KKBOX数位音乐风云榜
获奖时间	奖项名称	获奖结果
2017	第十二届十大风云歌手	获奖
2014	第十届十大风云歌手	获奖
2011	第七届十大风云歌手	获奖
2010	第六届年度最佳新人	获奖
hito流行音乐奖
获奖时间	奖项名称	获奖作品	获奖结果
2016-06-05	2016年hito电影主题曲	小幸运	获奖
2015-12-31	2015年HitFm百首单曲第一名	小幸运	获奖
2014-06-01	2014年hito流行音乐奖最佳女歌手奖 [100]		获奖
2014-06-01	2014年hito流行音乐奖年度十大华语歌曲奖 [100]	你就不要想起我	获奖
2014-06-01	2014hito流行音乐奖hito长寿专辑奖 [100]	渺小	获奖
2012-05-06	2012年年度华语歌曲	My Love	获奖
2012-05-06	2012hito流行音乐奖最受欢迎女歌手奖 [98]		获奖
2012-05-06	2012hito流行音乐奖网络首播人气奖 [98]		获奖
台湾金曲奖
获奖时间	奖项名称	获奖作品	获奖结果
2016-05-13	第27届台湾金曲奖年度最佳歌曲	小幸运	提名
2016-05-13	第27届台湾金曲奖最佳作曲人	小幸运	提名
2014-05-20	第25届台湾金曲奖最佳音乐录影带	渺小	提名
2014-05-20	第25届台湾金曲奖最佳专辑包装	渺小	提名
2012-05-15	第23届台湾金曲奖最佳国语女歌手	My Love	提名
2012-05-15	第23届台湾金曲奖最佳国语专辑	My Love	提名
2012-05-15	第23届台湾金曲奖最佳音乐录影带	My Love	提名
2012-05-15	第23届台湾金曲奖最佳作曲人	请你给我好一点的情敌	提名
2012-05-15	第23届台湾金曲奖最佳作词人	请你给我好一点的情敌	提名
2012-05-15	第23届台湾金曲奖最佳编曲人	请你给我好一点的情敌	提名
2012-05-15	第23届台湾金曲奖最佳单曲制作人	请你给我好一点的情敌	提名
2011-05-13	第22届台湾金曲奖最佳国语专辑	To Hebe	提名
2011-05-13	第22届台湾金曲奖最佳单曲制作人奖	Love!	获奖
2011-05-13	第22届台湾金曲奖最佳音乐录影带	寂寞寂寞就好	获奖
2011-05-13	第22届台湾金曲奖最佳专辑包装	To Hebe	获奖
全球流行音乐金榜
获奖时间	奖项名称	获奖作品	获奖结果
2016-04-03	第六届年度20大金曲	小幸运	获奖
2014-04-05	第四届全球流行音乐金榜颁奖典礼年度最受欢迎女歌手奖 [107]		获奖
2014-04-05	第四届全球流行音乐金榜颁奖典礼年度20大金曲奖 [107]	渺小	获奖
2014-04-05	第四届全球流行音乐金榜颁奖典礼年度最佳专辑奖 [107]	渺小	获奖
2012-06-30	第二届年度进榜最久专辑	My Love	获奖
2012-06-30	第二届年度二十大金曲	还是要幸福	获奖
2012-06-30	第二届洛杉矶AM1300中文电台单曲点播冠军	还是要幸福	获奖
2011-04-09	第一届年度最佳新人		获奖
2011-04-09	第一届传媒推荐大奖		获奖
2011-04-09	第一届年度20大金曲	寂寞寂寞就好	获奖
FM男人帮全球百大美女
获奖时间	奖项名称	获奖结果
2016	FHM全球百大性感美女台湾区第六名	获奖
2015	FHM全球百大性感美女台湾区第三名	获奖
台湾金马奖
获奖时间	奖项名称	获奖作品	获奖结果
2015-10-31	第52届台湾电影金马奖最佳原创电影歌曲	小幸运	提名
福布斯中国名人榜
获奖时间	奖项名称	获奖结果
2015	福布斯中国名人榜第九十名	获奖
2014	福布斯中国名人榜第七十名	获奖
2013	福布斯中国名人榜第六十六名	获奖
2012	福布斯中国名人榜第五十七名	获奖
新加坡e乐大赏
获奖时间	奖项名称	获奖作品	获奖结果
2014-05-17	第六届e乐人气女歌手		获奖
2011-04-02	第三届e乐人气女歌手		获奖
2011-04-02	第三届最佳年度专辑	To Hebe	获奖
2011-04-02	第三届最佳本地作曲	超级玛丽	获奖
音悦V榜
获奖时间	奖项名称	获奖作品	获奖结果
2014-04-15	第二届港台最佳女歌手		获奖
2014-04-15	第二届港台最具人气歌手		获奖
2014-04-15	第二届年度最佳专辑	渺小	获奖
QQ音乐巅峰盛典
获奖时间	奖项名称	获奖作品	获奖结果
2014-03-27	第一届年度最佳港台女歌手		获奖
2014-03-27	第一届年度热歌金曲	渺小	获奖
2014-03-27	第一届年度最佳国语专辑	渺小	获奖
音乐风云榜
获奖时间	奖项名称	获奖作品	获奖结果
2012-04-08	第十二届最佳女歌手		获奖
2011-04-11	第十一届港台最佳新人		获奖
2011-04-11	第十一届港台最佳女歌手		获奖
2011-04-11	第十一届港台最佳专辑	To Hebe	获奖
新加坡金曲奖
获奖时间	奖项名称	获奖作品	获奖结果
2011-11-12	第十七届海外杰出歌手（台湾）		获奖
2011-11-12	第十七届最佳专辑制作人	To Hebe	提名
2011-11-12	第十七届最佳演绎女歌手		提名
2011-11-12	第十七届最受欢迎女歌手		提名
2011-11-12	第十七届年度专辑大奖	To Hebe	提名
2011-11-12	第十七届Y.E.S.93.3FM醉心龙虎榜十大金曲	寂寞寂寞就好	获奖
中华音乐人交流协会
获奖时间	奖项名称	获奖作品	获奖结果
2011-06-06	十大单曲	Love!	获奖
2011-06-06	十大专辑	To Hebe	获奖
音乐风云榜新人盛典
获奖时间	奖项名称	获奖作品	获奖结果
2010-12-09	第三届年度最佳新人专辑	To Hebe	获奖
新城国语力颁奖礼
获奖时间	奖项名称	获奖作品	获奖结果
2007-08-04	第六届新城国语力热爆K歌奖	只对你有感觉	获奖
雪碧中国原创音乐流行榜
获奖时间	奖项名称	获奖作品	获奖结果
2007-01-20	第六届最优秀合唱歌曲奖	只对你有感觉	获奖', 0, 2345, '{"kb_id": "60b4d637-6acb-45e2-8217-07ddb5a79cf5", "doc_id": "e3ae5786-72d1-4ed5-b17f-b11074d60d17", "kb_name": "获奖情况知识库", "filename": "e3ae5786-72d1-4ed5-b17f-b11074d60d17.txt", "chunk_total": 1}', '2026-03-12 12:19:41.137667', 'f');
INSERT INTO "public"."kb_document_chunks" VALUES ('e33d8c7a-3da7-4850-8a1f-d2c442ce514e', 'b6949801-bb57-4cc3-a825-64d0055c54b6', '60b4d637-6acb-45e2-8217-07ddb5a79cf5', '蔡依林获奖情况
音乐类
获奖时间	奖项名称	获奖作品	获奖结果
2025-8-24	第6届腾讯音乐娱乐盛典年度影响力港台女歌手 [246]		获奖
2024-8	第31届东方风云榜港台地区最佳女歌手 [225]		获奖
2024-5-16	第35届金曲奖最佳作曲人奖 [186]	Someday, Somewhere	提名
2023-7	2023TMEA腾讯音乐娱乐盛典年度跨界合作单曲 [142]	都没差	获奖
2021-12	第三届腾讯音乐娱乐盛典港台地区年度最佳女歌手 [134]		获奖
2019	第30届金曲奖年度专辑奖 [83]	Ugly Beauty	获奖
2019	第30届金曲奖年度歌曲奖	玫瑰少年	获奖
2019	第30届金曲奖最佳国语专辑奖	Ugly Beauty	提名
2019	第30届金曲奖最佳国语女歌手奖		提名
2019	第30届金曲奖最佳演唱录音专辑奖 [84]	Ugly Beauty	提名
2019	2019Hito流行音乐奖年度十大华语歌曲 [135]	怪美的	获奖
2019	2019Hito流行音乐奖女歌手 [135]		获奖
2019	2019Hito流行音乐奖冠军王 [135]		获奖
2019	2019Hito流行音乐奖年度百首单曲冠军 [135]	怪美的	获奖
2017	MTV全球华语音乐盛典最受欢迎女歌手 [85]		获奖
2017	MTV全球华语音乐盛典最佳十大金曲		获奖
2017	MTV全球华语音乐盛典全球华语艺人大奖		获奖
2015	第26届金曲奖最佳国语专辑奖 [87]	呸	获奖
2015	第26届金曲奖最佳年度歌曲	Play 我呸	提名
2015	第26届金曲奖最佳演唱录音专辑 [87]	呸	获奖
2015	第5届全球流行音乐金榜年度最佳专辑	呸	获奖
2015	第5届全球流行音乐金榜Hit Fm联播网点播冠军	PLAY我呸	获奖
2015	第5届全球流行音乐金榜年度20大金曲	第三人称	获奖
2015	第十一届HITO年度女歌手	Play我呸	获奖
2015	第十一届HITO年度蝉连冠军最久单曲 [88]	Play我呸	获奖
2015	第十一届HITO年度最佳专辑 [88]	呸	获奖
2015	第十一届HITO年度五大金曲 [88]	Play我呸	获奖
2015	第十一届HITO年度蝉连冠军最久专辑 [88]	呸	获奖
2015	第十一届KKBOX数位音乐风云榜年度十大风云歌手 [89]	呸	获奖
2014	第九届KKBOX数位音乐风云榜年度十大风云歌手	MUSE	获奖
2013	第24届金曲奖最佳国语专辑 [90]	MUSE	提名
2013	第24届金曲奖年度最佳歌曲奖	大艺术家	获奖
2013	第24届金曲奖最佳国语女演唱人 [90]	MUSE	提名
2013	第九届HITO年度女歌手 [91]	MUSE	获奖
2013	第九届全球传媒推崇女歌手 [91]	MUSE	获奖
2013	第九届HITO年度十大华语歌曲 [91]	大艺术家	获奖
2013	第八届KKBOX数位音乐风云榜年度十大风云歌手	MUSE	获奖
2013	第十一届MusicRadio中国TOP排行榜年度最受欢迎女歌手	MUSE	获奖
2013	第十一届MusicRadio中国TOP排行榜年度最佳金曲	大艺术家	获奖
2013	第三届全球流行音乐金榜20大金曲 [92]	大艺术家	获奖
2013	第三届全球流行音乐金榜年度最佳女歌手 [92]	MUSE	获奖
2013	第三届全球流行音乐金榜年度最佳专辑奖 [92]	MUSE	获奖
2012	第十九届MTV欧洲大奖年度亚洲歌手	大艺术家	提名
2011	第六届KKBOX数位音乐风云榜年度十大风云歌手	Myself	获奖
2011	第九届MusicRadio中国TOP排行榜年度最受欢迎女歌手	Myself	获奖
2011	第九届MusicRadio中国TOP排行榜音乐之声点播冠军	美人计	获奖
2011	第九届MusicRadio中国TOP排行榜年度最佳金曲	美人计	获奖
2011	第十届中国原创音乐流行榜最佳女歌手	Myself	获奖
2010	第五届KKBOX数位音乐风云榜年度十大风云歌手	花蝴蝶	获奖
2010	第八届MusicRadio中国TOP排行榜年度最佳金曲 [95]	花蝴蝶	获奖
2010	第八届MusicRadio中国TOP排行榜年度最佳歌手 [95]	花蝴蝶	获奖
2010	第八届MusicRadio中国TOP排行榜年度最佳唱片 [95]	花蝴蝶	获奖
2010	第九届中国原创音乐流行榜最佳女歌手	花蝴蝶	获奖
2010	第十届音乐风云榜年度盛典港台十年最具影响力音乐人物	-	获奖
2010	第十届音乐风云榜年度盛典港台十年十大金曲	花蝴蝶	获奖
2010	第十届全球华语歌曲排行榜最受欢迎女歌手五强	Myself	获奖
2010	第五届中国移动无线音乐盛典年度搜索超人气女歌手	Myself	获奖
2010	第四届腾迅星光大典最受欢迎女歌手	花蝴蝶	获奖
2009	第四届KKBOX数位音乐风云榜年度十大会员收藏次数最多专辑	舞娘	获奖
2009	第四届KKBOX数位音乐风云榜年度十大会员收藏次数最多专辑	爱的练习语	获奖
2009	第四届KKBOX数位音乐风云榜年度十大会员收藏次数最多专辑	特务J	获奖
2009	第四届KKBOX数位音乐风云榜年度二十大专辑	特务J	获奖
2009	第四届中国移动无线音乐盛典全曲下载专辑最畅销女歌手	花蝴蝶	获奖
2009	第四届中国移动无线音乐盛典最高销量女歌手	花蝴蝶	获奖
2009	第八届国语力全球唱跳歌手	花蝴蝶	获奖
2009	第八届国语力跳舞歌曲	大丈夫	获奖
2009	第八届国语力全球至尊舞台大奖	花蝴蝶	获奖
2009	第八届国语力年度歌手	花蝴蝶	获奖
2009	第八届国语力歌曲	妥协	获奖
2009	第一回TVB劲歌金曲优秀选最受欢迎华语歌曲	大丈夫	获奖
2008	第六届HITO年度女歌手 [96]	特务J	获奖
2008	第六届HITO年度十大华语歌曲 [96]	特务J	获奖
2008	第六届HITO年度最长寿专辑奖 [96]	特务J	获奖
2008	第六届HITO年度十大华语歌曲 [96]	日不落	获奖
2008	第六届HITO年度听众最爱歌曲 [96]	日不落	获奖
2008	第三届KKBOX数位音乐风云榜年度十大风云歌手	特务J	获奖
2008	第三届KKBOX数位音乐风云榜年度最佳女歌手	特务J	获奖
2008	第六届MusicRadio中国TOP排行榜年度最佳销售女歌手	特务J	获奖
2008	第六届MusicRadio中国TOP排行榜年度全能艺人	特务J	获奖
2008	第六届MusicRadio中国TOP排行榜年度最佳金曲	特务J	获奖
2008	第八届音乐风云榜年度盛典最佳音乐录影带	特务J	获奖
2008	第八届全球华语歌曲排行榜最佳舞台演绎	特务J	获奖
2008	第八届全球华语歌曲排行榜最受欢迎歌手	特务J	获奖
2008	第八届全球华语歌曲排行榜台湾杰出歌手	特务J	获奖
2008	第八届全球华语歌曲排行榜最受欢迎二十大金曲	日不落	获奖
2008	第三届中国移动无线音乐盛典最高销量女歌手	特务J	获奖
2008	第三届中国移动无线音乐盛典最具影响力奥运歌曲	北京欢迎你	获奖
2008	第三届腾迅星光大典最受欢迎女歌手	特务J	获奖
2008	第九届CCTV-MTV音乐盛典台湾最受欢迎女歌手	特务J	获奖
2008	第十五届中歌榜北京流行音乐典礼年度最受欢迎女歌手	特务J	获奖
2008	第十五届中歌榜北京流行音乐典礼年度金曲	日不落	获奖
2007	第18届金曲奖年度最佳歌曲奖 [97]	今天你要嫁给我	获奖
2007	第18届台湾金曲奖最佳国语女演唱人奖 [97]	舞娘	获奖
2007	第十八届金曲奖最佳国语专辑 [98]	舞娘	提名
2007	第十八届金曲奖最受欢迎女歌手 [99]	舞娘	获奖
2007	第五届HITO年度十大华语歌曲	舞娘	获奖
2007	第五届HITO年度女歌手	舞娘	获奖
2007	第五届HITO年度最受欢迎女歌手	舞娘	获奖
2007	第五届HITO年度十大华语歌曲	假装	获奖
2007	第五届HITO年度十大华语歌曲	马德里不思议	获奖
2007	第二届KKBOX数位音乐风云榜年度风云女歌手	舞娘	获奖
2007	第二届KKBOX数位音乐风云榜年度连续攻榜冠军单曲	马德里不思议	获奖
2007	第二届KKBOX数位音乐风云榜年度十大专辑	舞娘	获奖
2007	第五届MusicRadio中国TOP排行榜年度最佳唱片	舞娘	获奖
2007	第五届MusicRadio中国TOP排行榜年度最佳销售女歌手	舞娘	获奖
2007	第五届MusicRadio中国TOP排行榜年度最佳金曲	今天你要嫁给我	获奖
2007	第五届MusicRadio中国TOP排行榜年度最佳金曲	舞娘	获奖
2007	第七届音乐风云榜年度盛典最佳专辑制作人	舞娘	获奖
2007	第七届全球华语歌曲排行榜最受欢迎对唱金曲 [100]	今天你要嫁给我	获奖
2007	第二届中国移动无线音乐盛典最畅销对唱奖歌曲	今天你要嫁给我	获奖
2007	第二届中国移动无线音乐盛典最高销量女歌手	特务J	获奖
2007	第二届中国移动无线音乐盛典最畅销劲舞金曲	爱情36计	获奖
2006	第四届HITO年度进榜最多单曲歌手 [101]	J-game	获奖
2006	第四届HITO年度女歌手 [101]	J-game	获奖
2006	第四届HITO年度蝉联冠军最久专辑 [101]	J-game	获奖
2006	第四届HITO年度网路首播最具人气歌手 [101]	J-game	获奖
2006	第一届KKBOX数位音乐风云榜年度十大K歌	天空	获奖
2006	第一届KKBOX数位音乐风云榜年度十大单曲	睁一只眼闭一只眼	获奖
2006	第一届KKBOX数位音乐风云榜年度十大专辑	J-game	获奖
2006	第一届KKBOX数位音乐风云榜年度十大艺人	J-game	获奖
2006	第四届MusicRadio中国TOP排行榜年度最佳女歌手	J-game	获奖
2006	第四届MusicRadio中国TOP排行榜年度最佳舞台演绎	J-game	获奖
2006	第四届MusicRadio中国TOP排行榜年度电台DJ票选最爱艺人	J-game	获奖
2006	第六届全球华语歌曲排行榜最受欢迎女歌手五强	舞娘	获奖
2006	第六届全球华语歌曲排行榜最受欢迎二十大金曲	舞娘	获奖
2006	第六届全球华语歌曲排行榜台湾杰出歌手	舞娘	获奖
2006	第五届国语力亚洲歌手 [103]	舞娘	获奖
2006	第五届国语力舞台大奖 [103]	舞娘	获奖
2006	第五届国语力歌曲 [103]	真命天子	获奖
2006	第五届国语力年度歌曲大奖 [103]	舞娘	获奖
2006	第五届国语力歌曲 [103]	舞娘	获奖
2006	第五届国语力歌曲 [103]	假装	获奖
2006	第二十八届十大中文金曲颁奖礼全国最受欢迎女歌手铜奖	J-game	获奖
2005	第三届HITO年度女歌手	城堡	获奖
2005	第三届HITO年度十大华语歌曲	就是爱	获奖
2005	第五届音乐风云榜年度盛典年度在榜时间最长歌手	城堡	获奖
2005	第五届音乐风云榜年度盛典港台榜单夺冠最多歌手	城堡	获奖
2005	第五届音乐风云榜年度盛典年度单周上榜最多歌曲歌手	城堡	获奖
2005	第四届国语力舞台大奖	J-game	获奖
2005	第四届国语力亚洲歌手	J-game	获奖
2005	第四届国语力年度歌曲大奖	野蛮游戏	获奖
2005	第四届国语力歌曲	野蛮游戏	获奖
2005	第四届国语力歌曲	天空	获奖
2005	第七届CCTV-MTV音乐盛典台湾年度最佳女歌手 [104]	J-game	获奖
2005	第四届MTV日本音乐录影带大奖buzz Asia中华艺人	海盗	提名
2004	第十五届金曲奖最佳国语专辑 [106]	看我72变	提名
2004	第十五届金曲奖最佳国语女演唱人 [106]	看我72变	提名
2004	第二届HITO年度蝉连冠军最久单曲 [107]	说爱你	获奖
2004	第二届HITO年度女歌手 [107]	看我72变	获奖
2004	第二届HITO年度十大华语歌曲 [107]	说爱你	获奖
2004	第二届HITO年度最长寿专辑 [107]	看我72变	获奖
2004	第二届MusicRadio中国TOP排行榜年度最佳编曲	布拉格广场	获奖
2004	第二届MusicRadio中国TOP排行榜年度最佳制作 [109]	布拉格广场	获奖
2004	第四届音乐风云榜年度盛典港台十大金曲	说爱你	获奖
2004	第三届国语力舞台大奖	城堡	获奖
2004	第三届国语力女歌手	城堡	获奖
2004	第三届国语力歌曲	就是爱	获奖
2004	第六届CCTV-MTV音乐盛典台湾年度最佳女歌手 [108]	城堡	获奖
2003	第二届国语力女歌手	看我72变	获奖
2003	第二届国语力歌曲	说爱你	获奖
2003	第二回TVB劲歌金曲优秀选最受欢迎国语歌曲	说爱你	获奖
2001-9-7	第18届MTV音乐录影带大奖台湾地区观众选择奖	爱上了一条街	获奖
2001	第一届音乐风云榜年度盛典港台最佳舞曲	DON''T STOP	获奖
社会类
获奖时间	奖项名称	获奖结果
2017	福布斯中国名人榜第83名 [86]	获奖
其他奖项
获奖时间	奖项名称	获奖作品	获奖结果
2015	FHM全球百大性感美女台湾区第四名		获奖
2014	台湾五大唱片华语金榜冠军	呸	获奖
2014	台湾博客来网路书店华语音乐畅销榜周榜三版冠军	呸	获奖
2014	台湾光南发烧榜华语榜冠军	呸	获奖
2014	台湾博客来网路书店华语音乐CD即时畅销榜三版冠军	呸	获奖
2014	台湾博客来网路书店全馆CD即时排行榜冠军	呸	获奖
2014	台湾佳佳唱片行华语音乐排行榜冠军	呸	获奖
Channel[V]全球华语榜中榜
获奖时间	奖项名称	获奖作品	获奖结果
2013	第十七届亚洲最具影响力歌手 [93]	MUSE	获奖
2013	第十七届年度网络金曲 [93]	大艺术家	获奖
2013	第十七届年度最佳专辑 [93]	MUSE	获奖
2007	第十三届年度最佳歌曲	舞娘	获奖
2006	第十二届年度最受欢迎女歌手 [102]	J-game	获奖
2006	第十二届年度最佳歌曲 [102]	天空	获奖
2005	第十一届年度最受欢迎女歌手 [105]	城堡	获奖
2005	第十一届最佳音乐录影带 [105]	海盗	获奖
2002	第八届最受欢迎歌曲	Lucky Number	获奖
2001	第七届最受欢迎歌曲	Don''t Stop	获奖
2000	第六届最受欢迎女新人赏	Jolin 1019	获奖
全球流行音乐金榜
获奖时间	奖项名称	获奖作品	获奖结果
2011	第一届年度DJ最爱艺人 [94]	Myself	获奖
2011	第一届年度电台点播冠军 [94]	美人计	获奖
2011	第一届年度最受欢迎女歌手 [94]	Myself	获奖
2011	第一届20大金曲 [94]	美人计	获奖
MY Astro至尊流行榜
获奖时间	奖项名称	获奖作品	获奖结果
2011	第二届至尊舞曲	美人计	获奖
2011	第二届全台主持联颁海外至尊歌手	Myself	获奖
2011	第二届至尊金曲	美人计	获奖
2011	第二届海外至尊女歌手	Myself	获奖
2011	第二届至尊金曲	玩爱之徒	获奖
2010	第一届至尊舞曲	大丈夫	获奖
2010	第一届十大金曲	大丈夫	获奖
新加坡金曲奖
获奖时间	奖项名称	获奖作品	获奖结果
2008	第14届亚太最受推崇女歌手	特务J	获奖
2004	第11届区域最受欢迎歌手	城堡	获奖
2004	第11届最受欢迎十大金曲	爱情36计	获奖
2004	第11届最受欢迎女歌手奖	城堡	获奖
2000	第7届年度最佳新人奖	Jolin1019	获奖
新城劲爆颁奖礼
获奖时间	奖项名称	获奖作品	获奖结果
2007	第十三届劲爆亚洲女歌手	特务J	获奖
2007	第十三届全国乐迷投选劲爆歌手	特务J	获奖
2007	第十三届劲爆国语歌曲奖	特务J	获奖
2004	第十届劲爆亚洲女歌手	城堡	获奖
2004	第十届劲爆国语女歌手	城堡	获奖
2004	第十届劲爆国语歌曲奖	海盗	获奖
2003	第九届劲爆国语歌曲奖	说爱你	获奖
2003	第九届劲爆国语女歌手	看我72变	获奖
全球华语歌曲排行榜
获奖时间	奖项名称	获奖作品	获奖结果
2005	第五届最佳舞台演绎奖	J-game	获奖
2005	第五届最受欢迎二十五大金曲	招牌动作	获奖
2005	第五届最受欢迎女歌手	J-game	获奖
2004	第四届传媒推荐大奖 [110]	城堡	获奖
2004	第四届年度最佳编曲 [110]	海盗	获奖
2004	第四届年度全能艺人 [110]	城堡	获奖
2004	第四届最受欢迎二十大金曲 [110]	海盗	获奖', 0, 5125, '{"kb_id": "60b4d637-6acb-45e2-8217-07ddb5a79cf5", "doc_id": "b6949801-bb57-4cc3-a825-64d0055c54b6", "kb_name": "获奖情况知识库", "filename": "b6949801-bb57-4cc3-a825-64d0055c54b6.txt", "chunk_total": 1}', '2026-03-12 12:19:49.637227', 'f');

-- ----------------------------
-- Table structure for kb_documents
-- ----------------------------
DROP TABLE IF EXISTS "public"."kb_documents";
CREATE TABLE "public"."kb_documents" (
  "id" varchar(48) COLLATE "pg_catalog"."default" NOT NULL,
  "kb_id" varchar(48) COLLATE "pg_catalog"."default" NOT NULL,
  "filename" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "file_path" text COLLATE "pg_catalog"."default" NOT NULL,
  "file_type" varchar(100) COLLATE "pg_catalog"."default",
  "file_size" int8,
  "status" varchar(50) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'pending'::character varying,
  "chunk_count" int4 DEFAULT 0,
  "meta" jsonb,
  "error_msg" text COLLATE "pg_catalog"."default",
  "created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "is_deleted" bool DEFAULT false
)
;
COMMENT ON COLUMN "public"."kb_documents"."id" IS 'ID';
COMMENT ON COLUMN "public"."kb_documents"."kb_id" IS '知识库ID';
COMMENT ON COLUMN "public"."kb_documents"."filename" IS '文件名';
COMMENT ON COLUMN "public"."kb_documents"."file_path" IS '文件路径';
COMMENT ON COLUMN "public"."kb_documents"."file_type" IS '文件类型';
COMMENT ON COLUMN "public"."kb_documents"."file_size" IS '文件大小（字节）';
COMMENT ON COLUMN "public"."kb_documents"."status" IS '处理状态';
COMMENT ON COLUMN "public"."kb_documents"."chunk_count" IS '分块数量';
COMMENT ON COLUMN "public"."kb_documents"."meta" IS '分页元数据';
COMMENT ON COLUMN "public"."kb_documents"."error_msg" IS '错误信息，可选';
COMMENT ON COLUMN "public"."kb_documents"."created_at" IS '创建时间';
COMMENT ON COLUMN "public"."kb_documents"."is_deleted" IS '创建时间';

-- ----------------------------
-- Records of kb_documents
-- ----------------------------
INSERT INTO "public"."kb_documents" VALUES ('400dc3e1-5853-499a-8499-fc13c2ebd84d', '69701332-85a5-431b-ab16-495b84b6f348', '3.txt', 'E:\ai_code\github workplace\zzwzz_rag\backend\uploads\69701332-85a5-431b-ab16-495b84b6f348\400dc3e1-5853-499a-8499-fc13c2ebd84d.txt', 'txt', 3657, 'completed', 4, NULL, NULL, '2026-02-21 12:24:20.793175', 'f');
INSERT INTO "public"."kb_documents" VALUES ('3c4670c3-cddc-4b87-a974-13c67f9d8176', '76a18674-1a4a-4e33-a520-78f9ec509e56', 'pmp_01.txt', 'E:\ai_code\github workplace\zzwzz_rag\backend\uploads\76a18674-1a4a-4e33-a520-78f9ec509e56\3c4670c3-cddc-4b87-a974-13c67f9d8176.txt', 'txt', 1641, 'completed', 1, NULL, NULL, '2026-03-11 16:37:28.534434', 'f');
INSERT INTO "public"."kb_documents" VALUES ('6e8b7134-145b-48a9-8a48-886d30e3fb7a', '76a18674-1a4a-4e33-a520-78f9ec509e56', 'pmp_02.txt', 'E:\ai_code\github workplace\zzwzz_rag\backend\uploads\76a18674-1a4a-4e33-a520-78f9ec509e56\6e8b7134-145b-48a9-8a48-886d30e3fb7a.txt', 'txt', 3726, 'completed', 3, NULL, NULL, '2026-03-11 16:37:42.843748', 'f');
INSERT INTO "public"."kb_documents" VALUES ('16c330ba-b341-4fc4-9f18-ee6ecedfe702', '60b4d637-6acb-45e2-8217-07ddb5a79cf5', '林俊杰获奖记录.txt', 'E:\ai_code\github workplace\zzwzz_rag\backend\uploads\60b4d637-6acb-45e2-8217-07ddb5a79cf5\16c330ba-b341-4fc4-9f18-ee6ecedfe702.txt', 'txt', 18391, 'completed', 1, NULL, NULL, '2026-03-12 12:20:12.876993', 'f');
INSERT INTO "public"."kb_documents" VALUES ('6a68d4b9-6e37-4c70-bd93-0adac1b60505', '60b4d637-6acb-45e2-8217-07ddb5a79cf5', '王力宏获奖记录.txt', 'E:\ai_code\github workplace\zzwzz_rag\backend\uploads\60b4d637-6acb-45e2-8217-07ddb5a79cf5\6a68d4b9-6e37-4c70-bd93-0adac1b60505.txt', 'txt', 13008, 'completed', 1, NULL, NULL, '2026-03-12 12:20:23.01274', 'f');
INSERT INTO "public"."kb_documents" VALUES ('8d2ae925-aaa2-4362-bac0-09cb5470082a', '60b4d637-6acb-45e2-8217-07ddb5a79cf5', '1.txt', 'E:\ai_code\github workplace\zzwzz_rag\backend\uploads\60b4d637-6acb-45e2-8217-07ddb5a79cf5\8d2ae925-aaa2-4362-bac0-09cb5470082a.txt', 'txt', 38, 'completed', 1, NULL, NULL, '2026-03-13 15:40:09.199617', 't');
INSERT INTO "public"."kb_documents" VALUES ('9bd9a14f-11e8-4584-b9af-09ee6d2cc700', '60b4d637-6acb-45e2-8217-07ddb5a79cf5', '周杰伦获奖记录.txt', 'E:\ai_code\github workplace\zzwzz_rag\backend\uploads\60b4d637-6acb-45e2-8217-07ddb5a79cf5\9bd9a14f-11e8-4584-b9af-09ee6d2cc700.txt', 'txt', 30199, 'completed', 1, NULL, NULL, '2026-03-12 12:18:21.628413', 'f');
INSERT INTO "public"."kb_documents" VALUES ('e3ae5786-72d1-4ed5-b17f-b11074d60d17', '60b4d637-6acb-45e2-8217-07ddb5a79cf5', 'Hebe获奖记录.txt', 'E:\ai_code\github workplace\zzwzz_rag\backend\uploads\60b4d637-6acb-45e2-8217-07ddb5a79cf5\e3ae5786-72d1-4ed5-b17f-b11074d60d17.txt', 'txt', 6566, 'completed', 1, NULL, NULL, '2026-03-12 12:19:41.111515', 'f');
INSERT INTO "public"."kb_documents" VALUES ('b6949801-bb57-4cc3-a825-64d0055c54b6', '60b4d637-6acb-45e2-8217-07ddb5a79cf5', '蔡依林获奖记录.txt', 'E:\ai_code\github workplace\zzwzz_rag\backend\uploads\60b4d637-6acb-45e2-8217-07ddb5a79cf5\b6949801-bb57-4cc3-a825-64d0055c54b6.txt', 'txt', 15474, 'completed', 1, NULL, NULL, '2026-03-12 12:19:49.586408', 'f');
INSERT INTO "public"."kb_documents" VALUES ('5d8ff2e9-ba05-4a89-a47b-09d1e04c2a1e', '60b4d637-6acb-45e2-8217-07ddb5a79cf5', '孙燕姿获奖记录.txt', 'E:\ai_code\github workplace\zzwzz_rag\backend\uploads\60b4d637-6acb-45e2-8217-07ddb5a79cf5\5d8ff2e9-ba05-4a89-a47b-09d1e04c2a1e.txt', 'txt', 9794, 'completed', 1, NULL, NULL, '2026-03-12 12:20:03.127111', 'f');
INSERT INTO "public"."kb_documents" VALUES ('741e7288-9a3e-48fa-b808-8ecc62bc360f', '60b4d637-6acb-45e2-8217-07ddb5a79cf5', '1.txt', 'E:\ai_code\github workplace\zzwzz_rag\backend\uploads\60b4d637-6acb-45e2-8217-07ddb5a79cf5\741e7288-9a3e-48fa-b808-8ecc62bc360f.txt', 'txt', 38, 'completed', 1, NULL, NULL, '2026-03-13 15:43:37.546378', 't');

-- ----------------------------
-- Table structure for kb_domains
-- ----------------------------
DROP TABLE IF EXISTS "public"."kb_domains";
CREATE TABLE "public"."kb_domains" (
  "id" varchar COLLATE "pg_catalog"."default" NOT NULL DEFAULT gen_random_uuid(),
  "name" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "description" varchar(200) COLLATE "pg_catalog"."default",
  "created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "is_active" bool,
  "is_deleted" bool DEFAULT false
)
;
COMMENT ON COLUMN "public"."kb_domains"."id" IS 'ID';
COMMENT ON COLUMN "public"."kb_domains"."name" IS '标签名称';
COMMENT ON COLUMN "public"."kb_domains"."description" IS '角色描述';
COMMENT ON COLUMN "public"."kb_domains"."created_at" IS '创建时间';
COMMENT ON COLUMN "public"."kb_domains"."updated_at" IS '更新时间';
COMMENT ON COLUMN "public"."kb_domains"."is_active" IS '是否激活';
COMMENT ON COLUMN "public"."kb_domains"."is_deleted" IS '创建时间';

-- ----------------------------
-- Records of kb_domains
-- ----------------------------
INSERT INTO "public"."kb_domains" VALUES ('b9781b67-b491-42f4-b956-9d6452acb1be', '音乐', '音乐', '2026-03-11 14:49:12.72045', '2026-03-11 16:31:20.073402', 't', 'f');
INSERT INTO "public"."kb_domains" VALUES ('01b95fbc-e275-4c9c-b565-a3ec62a782b5', '项目管理', '项目管理', '2026-03-11 15:36:52.059418', '2026-03-11 16:31:30.642892', 't', 'f');
INSERT INTO "public"."kb_domains" VALUES ('c187d86f-b421-4477-beb4-48bf241e61b8', '编程', '编程', '2026-03-11 16:31:37.925177', '2026-03-11 16:31:37.925177', 't', 'f');
INSERT INTO "public"."kb_domains" VALUES ('fa5ecb70-80e6-4d87-81e7-7e133f7eb5fb', '产品', '产品', '2026-03-11 16:31:42.83318', '2026-03-11 16:31:42.83318', 't', 'f');
INSERT INTO "public"."kb_domains" VALUES ('ebf06a93-57d3-4b41-844b-2d3cd17984d7', '金融', '金融', '2026-03-11 16:31:47.850068', '2026-03-11 16:31:47.850068', 't', 'f');
INSERT INTO "public"."kb_domains" VALUES ('76252e1b-18d2-4c5c-acf2-3f87867a51b5', '花卉绿植', '花卉绿植', '2026-03-11 16:32:00.842814', '2026-03-11 16:32:00.842814', 't', 'f');
INSERT INTO "public"."kb_domains" VALUES ('00957cfd-2a6f-4df5-9ee0-86a1ecaefd86', '管理', '管理', '2026-03-11 16:32:19.158635', '2026-03-11 16:32:19.158635', 't', 'f');
INSERT INTO "public"."kb_domains" VALUES ('dd1a1251-7e27-4708-a1b3-ffb3603386b7', '测试', '', '2026-03-13 16:22:59.496469', '2026-03-13 16:23:08.219095', 't', 't');

-- ----------------------------
-- Table structure for kb_evaluations
-- ----------------------------
DROP TABLE IF EXISTS "public"."kb_evaluations";
CREATE TABLE "public"."kb_evaluations" (
  "id" int4 NOT NULL DEFAULT nextval('evaluations_id_seq'::regclass),
  "query" text COLLATE "pg_catalog"."default" NOT NULL,
  "reference_answer" text COLLATE "pg_catalog"."default",
  "rag_answer" text COLLATE "pg_catalog"."default",
  "score" numeric(5,2),
  "created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "kb_id" varchar(48) COLLATE "pg_catalog"."default",
  "model_id" varchar(48) COLLATE "pg_catalog"."default",
  "is_deleted" bool DEFAULT false
)
;
COMMENT ON COLUMN "public"."kb_evaluations"."id" IS 'ID';
COMMENT ON COLUMN "public"."kb_evaluations"."query" IS '查询内容';
COMMENT ON COLUMN "public"."kb_evaluations"."reference_answer" IS '参考回答';
COMMENT ON COLUMN "public"."kb_evaluations"."rag_answer" IS 'RAG回答';
COMMENT ON COLUMN "public"."kb_evaluations"."score" IS '评分';
COMMENT ON COLUMN "public"."kb_evaluations"."created_at" IS '创建时间';
COMMENT ON COLUMN "public"."kb_evaluations"."kb_id" IS '知识库ID';
COMMENT ON COLUMN "public"."kb_evaluations"."model_id" IS '模型ID';
COMMENT ON COLUMN "public"."kb_evaluations"."is_deleted" IS '创建时间';

-- ----------------------------
-- Records of kb_evaluations
-- ----------------------------
INSERT INTO "public"."kb_evaluations" VALUES (3, '林俊杰最近写歌了吗', '没有写歌', '是的，林俊杰最近写了一首新歌。（参考信息 4450447f-c11b-4de1-8a18-5b0bab74d3e0）', 0.20, '2026-02-20 10:47:33.501686', '69701332-85a5-431b-ab16-495b84b6f348', '28729906-00a9-4de7-9a97-b2b87454f154', 'f');
INSERT INTO "public"."kb_evaluations" VALUES (7, '周杰伦在文档中吗', '在', '根据提供的信息，未检索到相关内容。', 0.40, '2026-02-20 12:36:02.949205', '69701332-85a5-431b-ab16-495b84b6f348', '28729906-00a9-4de7-9a97-b2b87454f154', 'f');
INSERT INTO "public"."kb_evaluations" VALUES (6, '周杰伦在文档中吗', '没在', '根据提供的信息，未检索到相关内容。', 0.40, '2026-02-20 12:35:39.608308', '69701332-85a5-431b-ab16-495b84b6f348', '28729906-00a9-4de7-9a97-b2b87454f154', 'f');
INSERT INTO "public"."kb_evaluations" VALUES (5, '林俊杰最近写歌了吗', '写了1首歌', '是的，林俊杰最近写了一首新歌。（参考信息 4450447f-c11b-4de1-8a18-5b0bab74d3e0）', 0.79, '2026-02-20 12:17:16.808504', '69701332-85a5-431b-ab16-495b84b6f348', '28729906-00a9-4de7-9a97-b2b87454f154', 'f');
INSERT INTO "public"."kb_evaluations" VALUES (4, '林俊杰最近写歌了吗', '我不知道呢', '是的，根据参考信息 4450447f-c11b-4de1-8a18-5b0bab74d3e0，林俊杰最近写了一首新歌。', 0.20, '2026-02-20 11:00:42.679385', '69701332-85a5-431b-ab16-495b84b6f348', '28729906-00a9-4de7-9a97-b2b87454f154', 'f');
INSERT INTO "public"."kb_evaluations" VALUES (8, '周杰伦在文档中吗', '未检索到相关内容', '是的，周杰伦在文档中。参考信息 aeb16095-64fc-4264-acd1-d8a5c005ee96 中提到：“我是周杰伦”。', 0.20, '2026-02-20 12:37:17.457877', '69701332-85a5-431b-ab16-495b84b6f348', '28729906-00a9-4de7-9a97-b2b87454f154', 'f');

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
INSERT INTO "public"."kb_knowledge_base_authorization_association" VALUES ('84d68e67-fcf9-4a0b-a91c-13bcc7e9822a', '69701332-85a5-431b-ab16-495b84b6f348');

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
INSERT INTO "public"."kb_knowledge_base_domain_association" VALUES ('69701332-85a5-431b-ab16-495b84b6f348', 'b9781b67-b491-42f4-b956-9d6452acb1be');
INSERT INTO "public"."kb_knowledge_base_domain_association" VALUES ('76a18674-1a4a-4e33-a520-78f9ec509e56', '01b95fbc-e275-4c9c-b565-a3ec62a782b5');
INSERT INTO "public"."kb_knowledge_base_domain_association" VALUES ('60b4d637-6acb-45e2-8217-07ddb5a79cf5', 'b9781b67-b491-42f4-b956-9d6452acb1be');

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
INSERT INTO "public"."kb_knowledge_base_tag_association" VALUES ('69701332-85a5-431b-ab16-495b84b6f348', '997f5bf1-6819-4ca3-877e-7fe33ca6ac4e');
INSERT INTO "public"."kb_knowledge_base_tag_association" VALUES ('76a18674-1a4a-4e33-a520-78f9ec509e56', 'bacd9b5c-3a5c-4ba0-b82f-67a3dd0f5f32');
INSERT INTO "public"."kb_knowledge_base_tag_association" VALUES ('60b4d637-6acb-45e2-8217-07ddb5a79cf5', '0510a4b5-afc7-42fa-b24c-343cee8d7a11');
INSERT INTO "public"."kb_knowledge_base_tag_association" VALUES ('60b4d637-6acb-45e2-8217-07ddb5a79cf5', 'e0a6aedf-7495-41a2-bbb0-c72974fc03b5');
INSERT INTO "public"."kb_knowledge_base_tag_association" VALUES ('60b4d637-6acb-45e2-8217-07ddb5a79cf5', '65b6ed42-e9c5-451f-bd5d-a4777577f85f');
INSERT INTO "public"."kb_knowledge_base_tag_association" VALUES ('60b4d637-6acb-45e2-8217-07ddb5a79cf5', '997f5bf1-6819-4ca3-877e-7fe33ca6ac4e');
INSERT INTO "public"."kb_knowledge_base_tag_association" VALUES ('60b4d637-6acb-45e2-8217-07ddb5a79cf5', '551d161b-35aa-491a-8d64-4bde56ebe6aa');
INSERT INTO "public"."kb_knowledge_base_tag_association" VALUES ('60b4d637-6acb-45e2-8217-07ddb5a79cf5', '285ae395-2e2f-4dff-96a0-5afe4da5ffa6');
INSERT INTO "public"."kb_knowledge_base_tag_association" VALUES ('60b4d637-6acb-45e2-8217-07ddb5a79cf5', '9aca47c1-d928-4d2e-9fcd-eb4121ebc338');

-- ----------------------------
-- Table structure for kb_knowledge_bases
-- ----------------------------
DROP TABLE IF EXISTS "public"."kb_knowledge_bases";
CREATE TABLE "public"."kb_knowledge_bases" (
  "id" varchar(48) COLLATE "pg_catalog"."default" NOT NULL DEFAULT nextval('knowledge_bases_id_seq'::regclass),
  "name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default",
  "avatar" varchar(255) COLLATE "pg_catalog"."default",
  "embedding_model" varchar(100) COLLATE "pg_catalog"."default",
  "chunk_size" int4,
  "chunk_overlap" int4,
  "retrieval_mode" varchar(50) COLLATE "pg_catalog"."default",
  "doc_count" int4 DEFAULT 0,
  "chunk_count" int4 DEFAULT 0,
  "owner_id" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "rerank_model" varchar(100) COLLATE "pg_catalog"."default",
  "embedding_model_id" varchar(48) COLLATE "pg_catalog"."default",
  "rerank_model_id" varchar(48) COLLATE "pg_catalog"."aa_DJ",
  "chunk_method" varchar(48) COLLATE "pg_catalog"."default",
  "is_deleted" bool DEFAULT false
)
;
COMMENT ON COLUMN "public"."kb_knowledge_bases"."id" IS 'ID';
COMMENT ON COLUMN "public"."kb_knowledge_bases"."name" IS '标签名称';
COMMENT ON COLUMN "public"."kb_knowledge_bases"."description" IS '角色描述';
COMMENT ON COLUMN "public"."kb_knowledge_bases"."avatar" IS '知识库头像';
COMMENT ON COLUMN "public"."kb_knowledge_bases"."embedding_model" IS '嵌入模型';
COMMENT ON COLUMN "public"."kb_knowledge_bases"."chunk_size" IS '分块大小';
COMMENT ON COLUMN "public"."kb_knowledge_bases"."chunk_overlap" IS '分块重叠大小';
COMMENT ON COLUMN "public"."kb_knowledge_bases"."retrieval_mode" IS '检索模式';
COMMENT ON COLUMN "public"."kb_knowledge_bases"."doc_count" IS '文档数量';
COMMENT ON COLUMN "public"."kb_knowledge_bases"."chunk_count" IS '分块数量';
COMMENT ON COLUMN "public"."kb_knowledge_bases"."owner_id" IS '所有者ID';
COMMENT ON COLUMN "public"."kb_knowledge_bases"."created_at" IS '创建时间';
COMMENT ON COLUMN "public"."kb_knowledge_bases"."updated_at" IS '更新时间';
COMMENT ON COLUMN "public"."kb_knowledge_bases"."rerank_model" IS '重排序模型';
COMMENT ON COLUMN "public"."kb_knowledge_bases"."embedding_model_id" IS '嵌入模型ID';
COMMENT ON COLUMN "public"."kb_knowledge_bases"."rerank_model_id" IS '重排序模型ID';
COMMENT ON COLUMN "public"."kb_knowledge_bases"."chunk_method" IS '分块方法';
COMMENT ON COLUMN "public"."kb_knowledge_bases"."is_deleted" IS '创建时间';

-- ----------------------------
-- Records of kb_knowledge_bases
-- ----------------------------
INSERT INTO "public"."kb_knowledge_bases" VALUES ('69701332-85a5-431b-ab16-495b84b6f348', '周杰伦知识库', '周杰伦知识库', '📚', 'text-embedding-v1', 256, 64, 'hybrid', 2, 6, '70b550f3-f81b-45cb-a92e-1dd8bb8292fc', '2026-02-17 08:07:44.585152', '2026-03-11 16:30:59.926671', 'gte-rerank-v2', '279bf3cb-6571-4c94-b172-85020e711f66', '1ed2c59a-7dee-41fd-bdfe-905109b22086', 'line', 'f');
INSERT INTO "public"."kb_knowledge_bases" VALUES ('76a18674-1a4a-4e33-a520-78f9ec509e56', '项目管理知识库', '项目管理知识库', '📚', 'text-embedding-v1', 512, 64, 'hybrid', 2, 4, '70b550f3-f81b-45cb-a92e-1dd8bb8292fc', '2026-03-11 16:34:08.631589', '2026-03-11 16:37:46.030147', 'gte-rerank-v2', '279bf3cb-6571-4c94-b172-85020e711f66', '1ed2c59a-7dee-41fd-bdfe-905109b22086', 'smart', 'f');
INSERT INTO "public"."kb_knowledge_bases" VALUES ('76f37a32-f454-4ee9-baeb-fb2ca39b0ea4', '测试', '测试', '📚', 'text-embedding-3-small', 512, 64, 'hybrid', 0, 0, '70b550f3-f81b-45cb-a92e-1dd8bb8292fc', '2026-03-13 15:38:40.780476', '2026-03-13 15:39:03.54251', '', '', '', 'smart', 't');
INSERT INTO "public"."kb_knowledge_bases" VALUES ('d999309a-ef79-4ddb-80e3-be4f9739c8c4', '是', '是', '📚', 'text-embedding-3-small', 512, 64, 'hybrid', 0, 0, '53a69efd-4adb-4ff5-a72b-2c38369ab462', '2026-02-13 14:30:39.923542', '2026-02-13 14:30:39.923542', NULL, NULL, NULL, '\n', 't');
INSERT INTO "public"."kb_knowledge_bases" VALUES ('60b4d637-6acb-45e2-8217-07ddb5a79cf5', '获奖情况知识库', '明星获奖情况知识库', '📚', 'text-embedding-v1', 1024, 64, 'hybrid', 8, 8, '70b550f3-f81b-45cb-a92e-1dd8bb8292fc', '2026-03-12 01:18:25.769806', '2026-03-13 15:43:38.160674', 'gte-rerank-v2', '279bf3cb-6571-4c94-b172-85020e711f66', '1ed2c59a-7dee-41fd-bdfe-905109b22086', 'paragraph', 'f');

-- ----------------------------
-- Table structure for kb_tags
-- ----------------------------
DROP TABLE IF EXISTS "public"."kb_tags";
CREATE TABLE "public"."kb_tags" (
  "id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "name" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "color" varchar(20) COLLATE "pg_catalog"."default" DEFAULT '#4CAF50'::character varying,
  "created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "is_active" bool,
  "is_deleted" bool DEFAULT false
)
;
COMMENT ON COLUMN "public"."kb_tags"."id" IS 'ID';
COMMENT ON COLUMN "public"."kb_tags"."name" IS '标签名称';
COMMENT ON COLUMN "public"."kb_tags"."color" IS '标签颜色';
COMMENT ON COLUMN "public"."kb_tags"."created_at" IS '创建时间';
COMMENT ON COLUMN "public"."kb_tags"."updated_at" IS '更新时间';
COMMENT ON COLUMN "public"."kb_tags"."is_active" IS '是否激活';
COMMENT ON COLUMN "public"."kb_tags"."is_deleted" IS '创建时间';

-- ----------------------------
-- Records of kb_tags
-- ----------------------------
INSERT INTO "public"."kb_tags" VALUES ('997f5bf1-6819-4ca3-877e-7fe33ca6ac4e', '周杰伦', 'rgb(175, 76, 76)', '2026-03-11 15:37:16.76293', '2026-03-11 16:32:29.816134', 't', 'f');
INSERT INTO "public"."kb_tags" VALUES ('0510a4b5-afc7-42fa-b24c-343cee8d7a11', '林俊杰', '#4CAF50', '2026-03-11 14:41:50.154366', '2026-03-11 16:32:37.611727', 't', 'f');
INSERT INTO "public"."kb_tags" VALUES ('e0a6aedf-7495-41a2-bbb0-c72974fc03b5', 'Hebe', '#4CAF50', '2026-03-11 16:32:48.890692', '2026-03-11 16:32:48.890692', 't', 'f');
INSERT INTO "public"."kb_tags" VALUES ('aa45d484-2bd3-4294-a561-df349d37dffb', '项目管理', '#4CAF50', '2026-03-11 16:33:01.293063', '2026-03-11 16:33:01.293063', 't', 'f');
INSERT INTO "public"."kb_tags" VALUES ('bacd9b5c-3a5c-4ba0-b82f-67a3dd0f5f32', 'PMP', '#4CAF50', '2026-03-11 16:33:05.816712', '2026-03-11 16:33:05.816712', 't', 'f');
INSERT INTO "public"."kb_tags" VALUES ('01019102-1b23-4f92-a0a3-26f7ee5f73bb', '软考', '#4CAF50', '2026-03-11 16:33:10.989066', '2026-03-11 16:33:10.989066', 't', 'f');
INSERT INTO "public"."kb_tags" VALUES ('d98049cb-9b70-4fb4-bc08-17f2032ee7c5', '十大知识域', '#4CAF50', '2026-03-11 16:33:22.701696', '2026-03-11 16:33:22.701696', 't', 'f');
INSERT INTO "public"."kb_tags" VALUES ('65b6ed42-e9c5-451f-bd5d-a4777577f85f', '获奖', '#4CAF50', '2026-03-12 01:27:54.294895', '2026-03-12 01:27:54.294895', 't', 'f');
INSERT INTO "public"."kb_tags" VALUES ('860d8385-a89f-40cc-96e7-40ecd784e18a', '奖励', '#4CAF50', '2026-03-12 01:28:12.182934', '2026-03-12 01:28:12.182934', 't', 'f');
INSERT INTO "public"."kb_tags" VALUES ('551d161b-35aa-491a-8d64-4bde56ebe6aa', '蔡依林', '#4CAF50', '2026-03-12 02:07:45.586273', '2026-03-12 02:07:45.586273', 't', 'f');
INSERT INTO "public"."kb_tags" VALUES ('285ae395-2e2f-4dff-96a0-5afe4da5ffa6', '王力宏', '#4CAF50', '2026-03-12 02:07:53.172333', '2026-03-12 02:07:53.172333', 't', 'f');
INSERT INTO "public"."kb_tags" VALUES ('9aca47c1-d928-4d2e-9fcd-eb4121ebc338', '孙燕姿', '#4CAF50', '2026-03-12 02:07:58.65267', '2026-03-12 02:07:58.65267', 't', 'f');
INSERT INTO "public"."kb_tags" VALUES ('28958182-d5cf-476f-9297-bd951c66ae8d', '测试', '#4CAF50', '2026-03-13 16:22:04.095406', '2026-03-13 16:22:19.186233', 't', 't');

-- ----------------------------
-- Table structure for m_model_vendors
-- ----------------------------
DROP TABLE IF EXISTS "public"."m_model_vendors";
CREATE TABLE "public"."m_model_vendors" (
  "id" varchar COLLATE "pg_catalog"."default" NOT NULL,
  "name" varchar COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default",
  "created_at" timestamptz(6) DEFAULT now(),
  "updated_at" timestamptz(6) DEFAULT now(),
  "is_deleted" bool DEFAULT false
)
;

-- ----------------------------
-- Records of m_model_vendors
-- ----------------------------
INSERT INTO "public"."m_model_vendors" VALUES ('openai', 'OpenAI', 'OpenAI是人工智能研究实验室，开发了GPT系列模型', '2026-02-13 22:46:56.064067+08', '2026-02-13 22:46:56.064067+08', 'f');
INSERT INTO "public"."m_model_vendors" VALUES ('qwen', 'Qwen', 'Qwen是阿里云开发的开源大语言模型', '2026-02-13 22:46:56.064067+08', '2026-02-13 22:46:56.064067+08', 'f');
INSERT INTO "public"."m_model_vendors" VALUES ('deepseek', 'DeepSeek', 'DeepSeek是深度求索开发的大语言模型', '2026-02-13 22:46:56.064067+08', '2026-02-13 22:46:56.064067+08', 'f');
INSERT INTO "public"."m_model_vendors" VALUES ('ollama', 'Ollama', 'Ollama是一个本地运行大语言模型的工具', '2026-02-13 22:46:56.064067+08', '2026-02-13 22:46:56.064067+08', 'f');
INSERT INTO "public"."m_model_vendors" VALUES ('anthropic', 'Anthropic', 'Anthropic开发了Claude系列模型', '2026-02-13 22:46:56.064067+08', '2026-02-13 22:46:56.064067+08', 'f');
INSERT INTO "public"."m_model_vendors" VALUES ('google', 'Google', 'Google开发了Gemini系列模型', '2026-02-13 22:46:56.064067+08', '2026-02-13 22:46:56.064067+08', 'f');
INSERT INTO "public"."m_model_vendors" VALUES ('microsoft', 'Microsoft', 'Microsoft开发了Phi系列模型', '2026-02-13 22:46:56.064067+08', '2026-02-13 22:46:56.064067+08', 'f');
INSERT INTO "public"."m_model_vendors" VALUES ('meta', 'Meta', 'Meta开发了Llama系列开源模型', '2026-02-13 22:46:56.064067+08', '2026-02-13 22:46:56.064067+08', 'f');

-- ----------------------------
-- Table structure for m_models
-- ----------------------------
DROP TABLE IF EXISTS "public"."m_models";
CREATE TABLE "public"."m_models" (
  "id" varchar(48) COLLATE "pg_catalog"."default" NOT NULL,
  "name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "model" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "vendor_id" varchar(100) COLLATE "pg_catalog"."default",
  "type" varchar(10) COLLATE "pg_catalog"."default" NOT NULL,
  "api_key" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "base_url" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default",
  "created_at" timestamptz(6) DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamptz(6) DEFAULT CURRENT_TIMESTAMP,
  "is_active" bool NOT NULL,
  "is_default" bool NOT NULL,
  "top_k" int4 DEFAULT 5,
  "temperature" float8 DEFAULT 0.7,
  "top_p" float8 DEFAULT 0.9,
  "is_deleted" bool DEFAULT false
)
;

-- ----------------------------
-- Records of m_models
-- ----------------------------
INSERT INTO "public"."m_models" VALUES ('279bf3cb-6571-4c94-b172-85020e711f66', ' qwen-text-embedding-v1', 'text-embedding-v1', 'qwen', 'embedding', 'sk-b54299feefc6431f95014b4e3eb86bef', 'https://dashscope.aliyuncs.com/compatible-mode/v1', '', '2026-02-17 16:33:28.614913+08', '2026-02-19 15:45:18.210828+08', 't', 't', 5, 0.7, 0.9, 'f');
INSERT INTO "public"."m_models" VALUES ('28729906-00a9-4de7-9a97-b2b87454f154', 'qwen3-max', 'qwen3-max', 'qwen', 'chat', 'sk-b54299feefc6431f95014b4e3eb86bef', 'https://dashscope.aliyuncs.com/compatible-mode/v1', '', '2026-02-17 16:45:35.344614+08', '2026-02-20 14:49:14.675762+08', 't', 'f', 5, 0.7, 0.6, 'f');
INSERT INTO "public"."m_models" VALUES ('4ae30696-4bc7-4ccf-9edc-dd6bc58b2774', 'gte-rerank-v2-1', 'gte-rerank-v2', 'ollama', 'rerank', 'sk-b54299feefc6431f95014b4e3eb86bef', 'https://dashscope.aliyuncs.com/api/v1', '', '2026-02-18 21:27:32.235983+08', '2026-03-12 12:08:44.577825+08', 't', 'f', 5, 0.7, 0.9, 'f');
INSERT INTO "public"."m_models" VALUES ('1ed2c59a-7dee-41fd-bdfe-905109b22086', 'gte-rerank-v2', 'gte-rerank-v2', 'qwen', 'rerank', 'sk-b54299feefc6431f95014b4e3eb86bef', 'https://dashscope.aliyuncs.com/api/v1', '1', '2026-02-18 20:38:31.673748+08', '2026-03-12 12:08:44.577825+08', 't', 't', 5, 0.7, 0.9, 'f');

-- ----------------------------
-- Table structure for sys_dictionaries
-- ----------------------------
DROP TABLE IF EXISTS "public"."sys_dictionaries";
CREATE TABLE "public"."sys_dictionaries" (
  "id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "name" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "type" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default",
  "created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP
)
;
COMMENT ON COLUMN "public"."sys_dictionaries"."id" IS 'ID';
COMMENT ON COLUMN "public"."sys_dictionaries"."name" IS '标签名称';
COMMENT ON COLUMN "public"."sys_dictionaries"."type" IS '字典类型';
COMMENT ON COLUMN "public"."sys_dictionaries"."description" IS '角色描述';
COMMENT ON COLUMN "public"."sys_dictionaries"."created_at" IS '创建时间';
COMMENT ON COLUMN "public"."sys_dictionaries"."updated_at" IS '更新时间';

-- ----------------------------
-- Records of sys_dictionaries
-- ----------------------------
INSERT INTO "public"."sys_dictionaries" VALUES ('1', '模型厂商', 'model_vendor', 'AI模型厂商字典', '2026-02-13 23:26:40.668186', '2026-02-13 23:26:40.668186');
INSERT INTO "public"."sys_dictionaries" VALUES ('2', '用户状态', 'user_status', '用户状态字典', '2026-02-13 23:26:40.668186', '2026-02-13 23:26:40.668186');
INSERT INTO "public"."sys_dictionaries" VALUES ('3', '文档类型', 'document_type', '文档类型字典', '2026-02-13 23:26:40.668186', '2026-02-13 23:26:40.668186');

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
  "sort" int4 DEFAULT 0,
  "is_active" bool DEFAULT true,
  "created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP
)
;
COMMENT ON COLUMN "public"."sys_dictionary_items"."id" IS 'ID';
COMMENT ON COLUMN "public"."sys_dictionary_items"."dictionary_id" IS '字典ID';
COMMENT ON COLUMN "public"."sys_dictionary_items"."key" IS '字典项键';
COMMENT ON COLUMN "public"."sys_dictionary_items"."value" IS '字典项值';
COMMENT ON COLUMN "public"."sys_dictionary_items"."label" IS '字典项标签';
COMMENT ON COLUMN "public"."sys_dictionary_items"."sort" IS '排序';
COMMENT ON COLUMN "public"."sys_dictionary_items"."is_active" IS '是否激活';
COMMENT ON COLUMN "public"."sys_dictionary_items"."created_at" IS '创建时间';
COMMENT ON COLUMN "public"."sys_dictionary_items"."updated_at" IS '更新时间';

-- ----------------------------
-- Records of sys_dictionary_items
-- ----------------------------
INSERT INTO "public"."sys_dictionary_items" VALUES ('1', '1', 'openai', 'openai', 'OpenAI', 1, 't', '2026-02-13 23:32:03.195321', '2026-02-13 23:32:03.195321');
INSERT INTO "public"."sys_dictionary_items" VALUES ('2', '1', 'qwen', 'qwen', '通义千问', 2, 't', '2026-02-13 23:32:03.195321', '2026-02-13 23:32:03.195321');
INSERT INTO "public"."sys_dictionary_items" VALUES ('3', '1', 'deepseek', 'deepseek', '深度求索', 3, 't', '2026-02-13 23:32:03.195321', '2026-02-13 23:32:03.195321');
INSERT INTO "public"."sys_dictionary_items" VALUES ('4', '1', 'ollama', 'ollama', 'Ollama', 4, 't', '2026-02-13 23:32:03.195321', '2026-02-13 23:32:03.195321');
INSERT INTO "public"."sys_dictionary_items" VALUES ('5', '2', 'active', 'active', '活跃', 1, 't', '2026-02-13 23:32:03.195321', '2026-02-13 23:32:03.195321');
INSERT INTO "public"."sys_dictionary_items" VALUES ('6', '2', 'inactive', 'inactive', '未激活', 2, 't', '2026-02-13 23:32:03.195321', '2026-02-13 23:32:03.195321');
INSERT INTO "public"."sys_dictionary_items" VALUES ('7', '2', 'disabled', 'disabled', '禁用', 3, 't', '2026-02-13 23:32:03.195321', '2026-02-13 23:32:03.195321');
INSERT INTO "public"."sys_dictionary_items" VALUES ('8', '3', 'txt', 'txt', '文本文件', 1, 't', '2026-02-13 23:32:03.195321', '2026-02-13 23:32:03.195321');
INSERT INTO "public"."sys_dictionary_items" VALUES ('9', '3', 'pdf', 'pdf', 'PDF文件', 2, 't', '2026-02-13 23:32:03.195321', '2026-02-13 23:32:03.195321');
INSERT INTO "public"."sys_dictionary_items" VALUES ('10', '3', 'docx', 'docx', 'Word文件', 3, 't', '2026-02-13 23:32:03.195321', '2026-02-13 23:32:03.195321');
INSERT INTO "public"."sys_dictionary_items" VALUES ('11', '3', 'xlsx', 'xlsx', 'Excel文件', 4, 't', '2026-02-13 23:32:03.195321', '2026-02-13 23:32:03.195321');

-- ----------------------------
-- Table structure for sys_menus
-- ----------------------------
DROP TABLE IF EXISTS "public"."sys_menus";
CREATE TABLE "public"."sys_menus" (
  "id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL DEFAULT gen_random_uuid(),
  "name" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "code" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "path" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "icon" varchar(50) COLLATE "pg_catalog"."default",
  "parent_id" varchar(36) COLLATE "pg_catalog"."default",
  "sort" int4 DEFAULT 0,
  "is_active" bool DEFAULT true,
  "created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP
)
;
COMMENT ON COLUMN "public"."sys_menus"."id" IS 'ID';
COMMENT ON COLUMN "public"."sys_menus"."name" IS '标签名称';
COMMENT ON COLUMN "public"."sys_menus"."code" IS '权限编码';
COMMENT ON COLUMN "public"."sys_menus"."path" IS '菜单路径';
COMMENT ON COLUMN "public"."sys_menus"."icon" IS '菜单图标';
COMMENT ON COLUMN "public"."sys_menus"."parent_id" IS '父菜单ID';
COMMENT ON COLUMN "public"."sys_menus"."sort" IS '排序';
COMMENT ON COLUMN "public"."sys_menus"."is_active" IS '是否激活';
COMMENT ON COLUMN "public"."sys_menus"."created_at" IS '创建时间';
COMMENT ON COLUMN "public"."sys_menus"."updated_at" IS '更新时间';

-- ----------------------------
-- Records of sys_menus
-- ----------------------------
INSERT INTO "public"."sys_menus" VALUES ('1', '聊天', 'chat', '/chat', '💬', NULL, 1, 't', '2026-02-18 15:48:37.522499', '2026-02-18 15:48:37.522499');
INSERT INTO "public"."sys_menus" VALUES ('2', '知识库', 'knowledge', '/knowledge', '📚', NULL, 2, 't', '2026-02-18 15:48:37.522499', '2026-02-18 15:48:37.522499');
INSERT INTO "public"."sys_menus" VALUES ('3', '模型管理', 'model', '/model', '🤖', NULL, 3, 't', '2026-02-18 15:48:37.522499', '2026-02-18 15:48:37.522499');
INSERT INTO "public"."sys_menus" VALUES ('4', '系统设置', 'system', '/system', '🛠️', NULL, 4, 't', '2026-02-18 15:48:37.522499', '2026-02-18 15:48:37.522499');
INSERT INTO "public"."sys_menus" VALUES ('5', '知识库管理', 'knowledge_base', '/knowledge-base', '📚', '2', 1, 't', '2026-02-18 15:48:37.522499', '2026-02-18 15:48:37.522499');
INSERT INTO "public"."sys_menus" VALUES ('6', '文档管理', 'documents', '/documents', '📄', '2', 2, 't', '2026-02-18 15:48:37.522499', '2026-02-18 15:48:37.522499');
INSERT INTO "public"."sys_menus" VALUES ('7', '知识库评估', 'evaluation', '/evaluation', '📊', '2', 3, 't', '2026-02-18 15:48:37.522499', '2026-02-18 15:48:37.522499');
INSERT INTO "public"."sys_menus" VALUES ('8', 'Embedding模型', 'embedding_model', '/model-settings?type=embedding', '🤖', '3', 1, 't', '2026-02-18 15:48:37.522499', '2026-02-18 15:48:37.522499');
INSERT INTO "public"."sys_menus" VALUES ('9', '聊天模型', 'chat_model', '/model-settings?type=chat', '🤖', '3', 2, 't', '2026-02-18 15:48:37.522499', '2026-02-18 15:48:37.522499');
INSERT INTO "public"."sys_menus" VALUES ('10', 'Rerank模型', 'rerank_model', '/model-settings?type=rerank', '🤖', '3', 3, 't', '2026-02-18 15:48:37.522499', '2026-02-18 15:48:37.522499');
INSERT INTO "public"."sys_menus" VALUES ('11', '用户管理', 'system_users', '/system/users', '👤', '4', 1, 't', '2026-02-18 15:48:37.522499', '2026-02-18 15:48:37.522499');
INSERT INTO "public"."sys_menus" VALUES ('12', '角色管理', 'system_roles', '/system/roles', '🎭', '4', 2, 't', '2026-02-18 15:48:37.522499', '2026-02-18 15:48:37.522499');
INSERT INTO "public"."sys_menus" VALUES ('13', '菜单管理', 'system_menus', '/system/menus', '📋', '4', 3, 't', '2026-02-18 15:48:37.522499', '2026-02-18 15:48:37.522499');
INSERT INTO "public"."sys_menus" VALUES ('14', '权限设置', 'system_permissions', '/system/permissions', '🔒', '4', 4, 't', '2026-02-18 15:48:37.522499', '2026-02-18 15:48:37.522499');
INSERT INTO "public"."sys_menus" VALUES ('15', '字典管理', 'system_dictionaries', '/system/dictionaries', '📖', '4', 5, 't', '2026-02-18 15:48:37.522499', '2026-02-18 15:48:37.522499');
INSERT INTO "public"."sys_menus" VALUES ('16', 'API接口管理', 'api_management', '/api-auth-management', '🔑', '2', 4, 't', '2026-02-20 22:01:00.830894', '2026-02-21 14:35:09.4594');
INSERT INTO "public"."sys_menus" VALUES ('17', '领域管理', 'domain', '/domain', '🔑', '2', 5, 't', '2026-02-20 22:01:00.830894', '2026-03-11 22:24:37.573561');
INSERT INTO "public"."sys_menus" VALUES ('18', '标签管理', 'tag', '/tag', '🔑', '2', 6, 't', '2026-02-20 22:01:00.830894', '2026-03-11 22:24:40.636971');

-- ----------------------------
-- Table structure for sys_permissions
-- ----------------------------
DROP TABLE IF EXISTS "public"."sys_permissions";
CREATE TABLE "public"."sys_permissions" (
  "id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL DEFAULT gen_random_uuid(),
  "name" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "code" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default",
  "menu_id" varchar(36) COLLATE "pg_catalog"."default",
  "created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP
)
;
COMMENT ON COLUMN "public"."sys_permissions"."id" IS 'ID';
COMMENT ON COLUMN "public"."sys_permissions"."name" IS '标签名称';
COMMENT ON COLUMN "public"."sys_permissions"."code" IS '权限编码';
COMMENT ON COLUMN "public"."sys_permissions"."description" IS '角色描述';
COMMENT ON COLUMN "public"."sys_permissions"."menu_id" IS '菜单ID';
COMMENT ON COLUMN "public"."sys_permissions"."created_at" IS '创建时间';
COMMENT ON COLUMN "public"."sys_permissions"."updated_at" IS '更新时间';

-- ----------------------------
-- Records of sys_permissions
-- ----------------------------
INSERT INTO "public"."sys_permissions" VALUES ('1', '查看聊天', 'chat_view', '查看聊天页面', '1', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('2', '查看知识库', 'knowledge_view', '查看知识库页面', '2', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('3', '查看知识库管理', 'knowledge_base_view', '查看知识库管理页面', '5', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('4', '创建知识库', 'knowledge_base_create', '创建知识库', '5', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('5', '编辑知识库', 'knowledge_base_edit', '编辑知识库', '5', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('6', '删除知识库', 'knowledge_base_delete', '删除知识库', '5', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('7', '查看文档管理', 'documents_view', '查看文档管理页面', '6', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('8', '上传文档', 'documents_upload', '上传文档', '6', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('9', '删除文档', 'documents_delete', '删除文档', '6', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('10', '查看知识库评估', 'evaluation_view', '查看知识库评估页面', '7', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('11', '查看模型管理', 'model_view', '查看模型管理页面', '3', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('12', '查看Embedding模型', 'embedding_model_view', '查看Embedding模型页面', '8', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('13', '创建Embedding模型', 'embedding_model_create', '创建Embedding模型', '8', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('14', '编辑Embedding模型', 'embedding_model_edit', '编辑Embedding模型', '8', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('15', '删除Embedding模型', 'embedding_model_delete', '删除Embedding模型', '8', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('16', '查看聊天模型', 'chat_model_view', '查看聊天模型页面', '9', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('17', '创建聊天模型', 'chat_model_create', '创建聊天模型', '9', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('18', '编辑聊天模型', 'chat_model_edit', '编辑聊天模型', '9', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('19', '删除聊天模型', 'chat_model_delete', '删除聊天模型', '9', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('20', '查看Rerank模型', 'rerank_model_view', '查看Rerank模型页面', '10', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('21', '创建Rerank模型', 'rerank_model_create', '创建Rerank模型', '10', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('22', '编辑Rerank模型', 'rerank_model_edit', '编辑Rerank模型', '10', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('23', '删除Rerank模型', 'rerank_model_delete', '删除Rerank模型', '10', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('24', '查看系统设置', 'system_view', '查看系统设置页面', '4', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('25', '查看用户管理', 'system_users_view', '查看用户管理页面', '11', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('26', '创建用户', 'system_users_create', '创建用户', '11', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('27', '编辑用户', 'system_users_edit', '编辑用户', '11', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('28', '删除用户', 'system_users_delete', '删除用户', '11', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('29', '查看角色管理', 'system_roles_view', '查看角色管理页面', '12', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('30', '创建角色', 'system_roles_create', '创建角色', '12', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('31', '编辑角色', 'system_roles_edit', '编辑角色', '12', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('32', '删除角色', 'system_roles_delete', '删除角色', '12', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('33', '查看菜单管理', 'system_menus_view', '查看菜单管理页面', '13', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('34', '创建菜单', 'system_menus_create', '创建菜单', '13', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('35', '编辑菜单', 'system_menus_edit', '编辑菜单', '13', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('36', '删除菜单', 'system_menus_delete', '删除菜单', '13', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('37', '查看权限设置', 'system_permissions_view', '查看权限设置页面', '14', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('38', '创建权限', 'system_permissions_create', '创建权限', '14', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('39', '编辑权限', 'system_permissions_edit', '编辑权限', '14', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('40', '删除权限', 'system_permissions_delete', '删除权限', '14', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('41', '查看字典管理', 'system_dictionaries_view', '查看字典管理页面', '15', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('42', '创建字典', 'system_dictionaries_create', '创建字典', '15', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('43', '编辑字典', 'system_dictionaries_edit', '编辑字典', '15', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('44', '删除字典', 'system_dictionaries_delete', '删除字典', '15', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('45', '管理字典项', 'system_dictionary_items_manage', '管理字典项', '15', '2026-02-18 15:52:21.77299', '2026-02-18 15:52:21.77299');
INSERT INTO "public"."sys_permissions" VALUES ('46', 'API接口管理权限', 'api_management', 'API接口管理相关操作权限', '16', '2026-02-20 22:01:00.832859', '2026-02-20 22:01:00.832859');
INSERT INTO "public"."sys_permissions" VALUES ('47', '领域管理', 'domain', '领域管理', '17', '2026-02-20 22:01:00.832859', '2026-02-20 22:01:00.832859');
INSERT INTO "public"."sys_permissions" VALUES ('48', '标签管理', 'tag', '标签管理', '18', '2026-02-20 22:01:00.832859', '2026-02-20 22:01:00.832859');

-- ----------------------------
-- Table structure for sys_role_permissions
-- ----------------------------
DROP TABLE IF EXISTS "public"."sys_role_permissions";
CREATE TABLE "public"."sys_role_permissions" (
  "role_id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "permission_id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP
)
;
COMMENT ON COLUMN "public"."sys_role_permissions"."role_id" IS '角色ID';
COMMENT ON COLUMN "public"."sys_role_permissions"."permission_id" IS '权限 ID';
COMMENT ON COLUMN "public"."sys_role_permissions"."created_at" IS '创建时间';

-- ----------------------------
-- Records of sys_role_permissions
-- ----------------------------
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '46', '2026-02-20 22:01:00.83395');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '47', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '48', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '30', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '10', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '26', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '11', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '14', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '23', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '35', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '9', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '13', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '20', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '17', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '22', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '19', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '15', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '8', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '1', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '25', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '34', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '7', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '3', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '28', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '4', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '39', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '42', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '43', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '44', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '5', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '24', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '45', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '32', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '18', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '2', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '16', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '40', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '33', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '31', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '12', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '27', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '29', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '6', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '36', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '38', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '41', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '37', '2026-02-20 13:50:21.561566');
INSERT INTO "public"."sys_role_permissions" VALUES ('1', '21', '2026-02-20 13:50:21.561566');

-- ----------------------------
-- Table structure for sys_roles
-- ----------------------------
DROP TABLE IF EXISTS "public"."sys_roles";
CREATE TABLE "public"."sys_roles" (
  "id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL DEFAULT gen_random_uuid(),
  "name" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "code" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default",
  "created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP
)
;
COMMENT ON COLUMN "public"."sys_roles"."id" IS 'ID';
COMMENT ON COLUMN "public"."sys_roles"."name" IS '标签名称';
COMMENT ON COLUMN "public"."sys_roles"."code" IS '权限编码';
COMMENT ON COLUMN "public"."sys_roles"."description" IS '角色描述';
COMMENT ON COLUMN "public"."sys_roles"."created_at" IS '创建时间';
COMMENT ON COLUMN "public"."sys_roles"."updated_at" IS '更新时间';

-- ----------------------------
-- Records of sys_roles
-- ----------------------------
INSERT INTO "public"."sys_roles" VALUES ('1', '超级管理员', 'admin', '系统最高权限', '2026-02-13 23:32:03.186367', '2026-02-13 23:32:03.186367');
INSERT INTO "public"."sys_roles" VALUES ('2', '普通用户', 'user', '普通用户权限', '2026-02-13 23:32:03.186367', '2026-02-13 23:32:03.186367');

-- ----------------------------
-- Table structure for sys_users
-- ----------------------------
DROP TABLE IF EXISTS "public"."sys_users";
CREATE TABLE "public"."sys_users" (
  "id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL DEFAULT gen_random_uuid(),
  "username" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "email" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "hashed_password" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "is_active" bool DEFAULT true,
  "role" varchar(20) COLLATE "pg_catalog"."default" DEFAULT 'user'::character varying,
  "role_id" varchar(36) COLLATE "pg_catalog"."default",
  "created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "is_deleted" bool DEFAULT false
)
;
COMMENT ON COLUMN "public"."sys_users"."id" IS 'ID';
COMMENT ON COLUMN "public"."sys_users"."username" IS '用户名';
COMMENT ON COLUMN "public"."sys_users"."email" IS '邮箱';
COMMENT ON COLUMN "public"."sys_users"."hashed_password" IS '密码';
COMMENT ON COLUMN "public"."sys_users"."is_active" IS '是否激活';
COMMENT ON COLUMN "public"."sys_users"."role" IS '角色';
COMMENT ON COLUMN "public"."sys_users"."role_id" IS '角色ID';
COMMENT ON COLUMN "public"."sys_users"."created_at" IS '创建时间';
COMMENT ON COLUMN "public"."sys_users"."is_deleted" IS '创建时间';

-- ----------------------------
-- Records of sys_users
-- ----------------------------
INSERT INTO "public"."sys_users" VALUES ('70b550f3-f81b-45cb-a92e-1dd8bb8292fc', 'root', 'zzwzz2025@gmail.com', '63a9f0ea7bb98050796b649e85481845', 't', 'admin', '1', '2026-02-13 15:35:38.854422', '2026-03-14 01:28:02.576712', 'f');
INSERT INTO "public"."sys_users" VALUES ('80afe6ba-5f34-4548-ac88-aedd7e57a773', 'test', '84@qq.com', '123456', 't', 'user', '2', '2026-03-13 16:52:28.062077', '2026-03-14 01:34:01.578269', 'f');

-- ----------------------------
-- Function structure for update_timestamp
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."update_timestamp"();
CREATE FUNCTION "public"."update_timestamp"()
  RETURNS "pg_catalog"."trigger" AS $BODY$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

-- ----------------------------
-- Function structure for update_updated_at_column
-- ----------------------------
DROP FUNCTION IF EXISTS "public"."update_updated_at_column"();
CREATE FUNCTION "public"."update_updated_at_column"()
  RETURNS "pg_catalog"."trigger" AS $BODY$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."evaluations_id_seq"
OWNED BY "public"."kb_evaluations"."id";
SELECT setval('"public"."evaluations_id_seq"', 8, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "public"."knowledge_bases_id_seq"
OWNED BY "public"."kb_knowledge_bases"."id";
SELECT setval('"public"."knowledge_bases_id_seq"', 1, false);

-- ----------------------------
-- Indexes structure for table api_authorizations
-- ----------------------------
CREATE INDEX "idx_api_authorizations_auth_code" ON "public"."api_authorizations" USING btree (
  "auth_code" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "idx_api_authorizations_end_time" ON "public"."api_authorizations" USING btree (
  "end_time" "pg_catalog"."timestamptz_ops" ASC NULLS LAST
);
CREATE INDEX "idx_api_authorizations_is_active" ON "public"."api_authorizations" USING btree (
  "is_active" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "idx_api_authorizations_vendor_name" ON "public"."api_authorizations" USING btree (
  "vendor_name" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

-- ----------------------------
-- Triggers structure for table api_authorizations
-- ----------------------------
CREATE TRIGGER "update_api_authorizations_updated_at" BEFORE UPDATE ON "public"."api_authorizations"
FOR EACH ROW
EXECUTE PROCEDURE "public"."update_updated_at_column"();

-- ----------------------------
-- Uniques structure for table api_authorizations
-- ----------------------------
ALTER TABLE "public"."api_authorizations" ADD CONSTRAINT "api_authorizations_auth_code_key" UNIQUE ("auth_code");

-- ----------------------------
-- Primary Key structure for table api_authorizations
-- ----------------------------
ALTER TABLE "public"."api_authorizations" ADD CONSTRAINT "api_authorizations_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table api_logs
-- ----------------------------
CREATE INDEX "idx_api_logs_auth_code" ON "public"."api_logs" USING btree (
  "auth_code" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "idx_api_logs_created_at" ON "public"."api_logs" USING btree (
  "created_at" "pg_catalog"."timestamptz_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table api_logs
-- ----------------------------
ALTER TABLE "public"."api_logs" ADD CONSTRAINT "api_logs_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table chat_conversations
-- ----------------------------
CREATE INDEX "idx_conversations_is_deleted" ON "public"."chat_conversations" USING btree (
  "is_deleted" "pg_catalog"."bool_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table chat_conversations
-- ----------------------------
ALTER TABLE "public"."chat_conversations" ADD CONSTRAINT "conversations_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table chat_feedbacks
-- ----------------------------
CREATE INDEX "idx_feedbacks_is_deleted" ON "public"."chat_feedbacks" USING btree (
  "is_deleted" "pg_catalog"."bool_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table chat_feedbacks
-- ----------------------------
ALTER TABLE "public"."chat_feedbacks" ADD CONSTRAINT "feedbacks_message_id_key" UNIQUE ("message_id");

-- ----------------------------
-- Primary Key structure for table chat_feedbacks
-- ----------------------------
ALTER TABLE "public"."chat_feedbacks" ADD CONSTRAINT "feedbacks_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table chat_logs
-- ----------------------------
CREATE INDEX "idx_chat_logs_conversation_id" ON "public"."chat_logs" USING btree (
  "conversation_id" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "idx_chat_logs_created_at" ON "public"."chat_logs" USING btree (
  "created_at" "pg_catalog"."timestamptz_ops" ASC NULLS LAST
);
CREATE INDEX "idx_chat_logs_is_deleted" ON "public"."chat_logs" USING btree (
  "is_deleted" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "idx_chat_logs_user_id" ON "public"."chat_logs" USING btree (
  "user_id" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table chat_logs
-- ----------------------------
ALTER TABLE "public"."chat_logs" ADD CONSTRAINT "chat_logs_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table chat_messages
-- ----------------------------
CREATE INDEX "idx_messages_is_deleted" ON "public"."chat_messages" USING btree (
  "is_deleted" "pg_catalog"."bool_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table chat_messages
-- ----------------------------
ALTER TABLE "public"."chat_messages" ADD CONSTRAINT "messages_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table kb_document_chunks
-- ----------------------------
CREATE INDEX "idx_document_chunks_is_deleted" ON "public"."kb_document_chunks" USING btree (
  "is_deleted" "pg_catalog"."bool_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table kb_document_chunks
-- ----------------------------
ALTER TABLE "public"."kb_document_chunks" ADD CONSTRAINT "document_chunks_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table kb_documents
-- ----------------------------
CREATE INDEX "idx_documents_is_deleted" ON "public"."kb_documents" USING btree (
  "is_deleted" "pg_catalog"."bool_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table kb_documents
-- ----------------------------
ALTER TABLE "public"."kb_documents" ADD CONSTRAINT "documents_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table kb_domains
-- ----------------------------
CREATE INDEX "idx_domain_is_deleted" ON "public"."kb_domains" USING btree (
  "is_deleted" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "idx_domains_name" ON "public"."kb_domains" USING btree (
  "name" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table kb_domains
-- ----------------------------
ALTER TABLE "public"."kb_domains" ADD CONSTRAINT "domains_name_key" UNIQUE ("name");

-- ----------------------------
-- Primary Key structure for table kb_domains
-- ----------------------------
ALTER TABLE "public"."kb_domains" ADD CONSTRAINT "domains_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table kb_evaluations
-- ----------------------------
CREATE INDEX "idx_evaluations_is_deleted" ON "public"."kb_evaluations" USING btree (
  "is_deleted" "pg_catalog"."bool_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table kb_evaluations
-- ----------------------------
ALTER TABLE "public"."kb_evaluations" ADD CONSTRAINT "evaluations_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table kb_knowledge_base_authorization_association
-- ----------------------------
ALTER TABLE "public"."kb_knowledge_base_authorization_association" ADD CONSTRAINT "knowledge_base_authorization_association_pkey" PRIMARY KEY ("authorization_id", "knowledge_base_id");

-- ----------------------------
-- Primary Key structure for table kb_knowledge_base_domain_association
-- ----------------------------
ALTER TABLE "public"."kb_knowledge_base_domain_association" ADD CONSTRAINT "knowledge_base_domain_association_pkey" PRIMARY KEY ("knowledge_base_id", "domain_id");

-- ----------------------------
-- Primary Key structure for table kb_knowledge_base_tag_association
-- ----------------------------
ALTER TABLE "public"."kb_knowledge_base_tag_association" ADD CONSTRAINT "knowledge_base_tag_association_pkey" PRIMARY KEY ("knowledge_base_id", "tag_id");

-- ----------------------------
-- Indexes structure for table kb_knowledge_bases
-- ----------------------------
CREATE INDEX "idx_knowledge_bases_is_deleted" ON "public"."kb_knowledge_bases" USING btree (
  "is_deleted" "pg_catalog"."bool_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table kb_knowledge_bases
-- ----------------------------
ALTER TABLE "public"."kb_knowledge_bases" ADD CONSTRAINT "knowledge_bases_name_key" UNIQUE ("name");

-- ----------------------------
-- Primary Key structure for table kb_knowledge_bases
-- ----------------------------
ALTER TABLE "public"."kb_knowledge_bases" ADD CONSTRAINT "knowledge_bases_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table kb_tags
-- ----------------------------
CREATE INDEX "idx_tags_is_deleted" ON "public"."kb_tags" USING btree (
  "is_deleted" "pg_catalog"."bool_ops" ASC NULLS LAST
);

-- ----------------------------
-- Uniques structure for table kb_tags
-- ----------------------------
ALTER TABLE "public"."kb_tags" ADD CONSTRAINT "tags_name_key" UNIQUE ("name");

-- ----------------------------
-- Primary Key structure for table kb_tags
-- ----------------------------
ALTER TABLE "public"."kb_tags" ADD CONSTRAINT "tags_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table m_model_vendors
-- ----------------------------
CREATE INDEX "idx_model_vendors_is_deleted" ON "public"."m_model_vendors" USING btree (
  "is_deleted" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "idx_model_vendors_name" ON "public"."m_model_vendors" USING btree (
  "name" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

-- ----------------------------
-- Triggers structure for table m_model_vendors
-- ----------------------------
CREATE TRIGGER "update_model_vendors_timestamp" BEFORE UPDATE ON "public"."m_model_vendors"
FOR EACH ROW
EXECUTE PROCEDURE "public"."update_timestamp"();

-- ----------------------------
-- Uniques structure for table m_model_vendors
-- ----------------------------
ALTER TABLE "public"."m_model_vendors" ADD CONSTRAINT "model_vendors_name_key" UNIQUE ("name");

-- ----------------------------
-- Primary Key structure for table m_model_vendors
-- ----------------------------
ALTER TABLE "public"."m_model_vendors" ADD CONSTRAINT "model_vendors_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table m_models
-- ----------------------------
CREATE INDEX "idx_models_is_deleted" ON "public"."m_models" USING btree (
  "is_deleted" "pg_catalog"."bool_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table m_models
-- ----------------------------
ALTER TABLE "public"."m_models" ADD CONSTRAINT "models_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Triggers structure for table sys_dictionaries
-- ----------------------------
CREATE TRIGGER "update_dictionaries_updated_at" BEFORE UPDATE ON "public"."sys_dictionaries"
FOR EACH ROW
EXECUTE PROCEDURE "public"."update_updated_at_column"();

-- ----------------------------
-- Uniques structure for table sys_dictionaries
-- ----------------------------
ALTER TABLE "public"."sys_dictionaries" ADD CONSTRAINT "dictionaries_type_key" UNIQUE ("type");

-- ----------------------------
-- Primary Key structure for table sys_dictionaries
-- ----------------------------
ALTER TABLE "public"."sys_dictionaries" ADD CONSTRAINT "dictionaries_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Triggers structure for table sys_dictionary_items
-- ----------------------------
CREATE TRIGGER "update_dictionary_items_updated_at" BEFORE UPDATE ON "public"."sys_dictionary_items"
FOR EACH ROW
EXECUTE PROCEDURE "public"."update_updated_at_column"();

-- ----------------------------
-- Uniques structure for table sys_dictionary_items
-- ----------------------------
ALTER TABLE "public"."sys_dictionary_items" ADD CONSTRAINT "dictionary_items_dictionary_id_key_key" UNIQUE ("dictionary_id", "key");

-- ----------------------------
-- Primary Key structure for table sys_dictionary_items
-- ----------------------------
ALTER TABLE "public"."sys_dictionary_items" ADD CONSTRAINT "dictionary_items_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Triggers structure for table sys_menus
-- ----------------------------
CREATE TRIGGER "update_menus_updated_at" BEFORE UPDATE ON "public"."sys_menus"
FOR EACH ROW
EXECUTE PROCEDURE "public"."update_updated_at_column"();

-- ----------------------------
-- Uniques structure for table sys_menus
-- ----------------------------
ALTER TABLE "public"."sys_menus" ADD CONSTRAINT "menus_code_key" UNIQUE ("code");

-- ----------------------------
-- Primary Key structure for table sys_menus
-- ----------------------------
ALTER TABLE "public"."sys_menus" ADD CONSTRAINT "menus_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Triggers structure for table sys_permissions
-- ----------------------------
CREATE TRIGGER "update_permissions_updated_at" BEFORE UPDATE ON "public"."sys_permissions"
FOR EACH ROW
EXECUTE PROCEDURE "public"."update_updated_at_column"();

-- ----------------------------
-- Uniques structure for table sys_permissions
-- ----------------------------
ALTER TABLE "public"."sys_permissions" ADD CONSTRAINT "permissions_code_key" UNIQUE ("code");

-- ----------------------------
-- Primary Key structure for table sys_permissions
-- ----------------------------
ALTER TABLE "public"."sys_permissions" ADD CONSTRAINT "permissions_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table sys_role_permissions
-- ----------------------------
ALTER TABLE "public"."sys_role_permissions" ADD CONSTRAINT "role_permissions_pkey" PRIMARY KEY ("role_id", "permission_id");

-- ----------------------------
-- Triggers structure for table sys_roles
-- ----------------------------
CREATE TRIGGER "update_roles_updated_at" BEFORE UPDATE ON "public"."sys_roles"
FOR EACH ROW
EXECUTE PROCEDURE "public"."update_updated_at_column"();

-- ----------------------------
-- Uniques structure for table sys_roles
-- ----------------------------
ALTER TABLE "public"."sys_roles" ADD CONSTRAINT "roles_name_key" UNIQUE ("name");
ALTER TABLE "public"."sys_roles" ADD CONSTRAINT "roles_code_key" UNIQUE ("code");

-- ----------------------------
-- Primary Key structure for table sys_roles
-- ----------------------------
ALTER TABLE "public"."sys_roles" ADD CONSTRAINT "roles_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table sys_users
-- ----------------------------
CREATE INDEX "idx_users_email" ON "public"."sys_users" USING btree (
  "email" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "idx_users_is_deleted" ON "public"."sys_users" USING btree (
  "is_deleted" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "idx_users_username" ON "public"."sys_users" USING btree (
  "username" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

-- ----------------------------
-- Triggers structure for table sys_users
-- ----------------------------
CREATE TRIGGER "update_users_updated_at" BEFORE UPDATE ON "public"."sys_users"
FOR EACH ROW
EXECUTE PROCEDURE "public"."update_updated_at_column"();

-- ----------------------------
-- Uniques structure for table sys_users
-- ----------------------------
ALTER TABLE "public"."sys_users" ADD CONSTRAINT "users_username_key" UNIQUE ("username");
ALTER TABLE "public"."sys_users" ADD CONSTRAINT "users_email_key" UNIQUE ("email");

-- ----------------------------
-- Primary Key structure for table sys_users
-- ----------------------------
ALTER TABLE "public"."sys_users" ADD CONSTRAINT "users_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Foreign Keys structure for table chat_feedbacks
-- ----------------------------
ALTER TABLE "public"."chat_feedbacks" ADD CONSTRAINT "feedbacks_message_id_fkey" FOREIGN KEY ("message_id") REFERENCES "public"."chat_messages" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table chat_logs
-- ----------------------------
ALTER TABLE "public"."chat_logs" ADD CONSTRAINT "chat_logs_conversation_id_fkey" FOREIGN KEY ("conversation_id") REFERENCES "public"."chat_conversations" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "public"."chat_logs" ADD CONSTRAINT "chat_logs_message_id_fkey" FOREIGN KEY ("message_id") REFERENCES "public"."chat_messages" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "public"."chat_logs" ADD CONSTRAINT "chat_logs_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."sys_users" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table kb_knowledge_base_authorization_association
-- ----------------------------
ALTER TABLE "public"."kb_knowledge_base_authorization_association" ADD CONSTRAINT "knowledge_base_authorization_association_authorization_id_fkey" FOREIGN KEY ("authorization_id") REFERENCES "public"."api_authorizations" ("id") ON DELETE CASCADE ON UPDATE NO ACTION;
ALTER TABLE "public"."kb_knowledge_base_authorization_association" ADD CONSTRAINT "knowledge_base_authorization_association_knowledge_base_id_fkey" FOREIGN KEY ("knowledge_base_id") REFERENCES "public"."kb_knowledge_bases" ("id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table kb_knowledge_base_domain_association
-- ----------------------------
ALTER TABLE "public"."kb_knowledge_base_domain_association" ADD CONSTRAINT "knowledge_base_domain_association_domain_id_fkey" FOREIGN KEY ("domain_id") REFERENCES "public"."kb_domains" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "public"."kb_knowledge_base_domain_association" ADD CONSTRAINT "knowledge_base_domain_association_knowledge_base_id_fkey" FOREIGN KEY ("knowledge_base_id") REFERENCES "public"."kb_knowledge_bases" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table kb_knowledge_base_tag_association
-- ----------------------------
ALTER TABLE "public"."kb_knowledge_base_tag_association" ADD CONSTRAINT "knowledge_base_tag_association_knowledge_base_id_fkey" FOREIGN KEY ("knowledge_base_id") REFERENCES "public"."kb_knowledge_bases" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "public"."kb_knowledge_base_tag_association" ADD CONSTRAINT "knowledge_base_tag_association_tag_id_fkey" FOREIGN KEY ("tag_id") REFERENCES "public"."kb_tags" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table sys_dictionary_items
-- ----------------------------
ALTER TABLE "public"."sys_dictionary_items" ADD CONSTRAINT "dictionary_items_dictionary_id_fkey" FOREIGN KEY ("dictionary_id") REFERENCES "public"."sys_dictionaries" ("id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table sys_menus
-- ----------------------------
ALTER TABLE "public"."sys_menus" ADD CONSTRAINT "menus_parent_id_fkey" FOREIGN KEY ("parent_id") REFERENCES "public"."sys_menus" ("id") ON DELETE SET NULL ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table sys_permissions
-- ----------------------------
ALTER TABLE "public"."sys_permissions" ADD CONSTRAINT "permissions_menu_id_fkey" FOREIGN KEY ("menu_id") REFERENCES "public"."sys_menus" ("id") ON DELETE SET NULL ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table sys_role_permissions
-- ----------------------------
ALTER TABLE "public"."sys_role_permissions" ADD CONSTRAINT "role_permissions_permission_id_fkey" FOREIGN KEY ("permission_id") REFERENCES "public"."sys_permissions" ("id") ON DELETE CASCADE ON UPDATE NO ACTION;
ALTER TABLE "public"."sys_role_permissions" ADD CONSTRAINT "role_permissions_role_id_fkey" FOREIGN KEY ("role_id") REFERENCES "public"."sys_roles" ("id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table sys_users
-- ----------------------------
ALTER TABLE "public"."sys_users" ADD CONSTRAINT "users_role_id_fkey" FOREIGN KEY ("role_id") REFERENCES "public"."sys_roles" ("id") ON DELETE SET NULL ON UPDATE NO ACTION;
