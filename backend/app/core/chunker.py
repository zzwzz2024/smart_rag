"""
SmartRAG 自适应智能分块器
- 根据文档类型自动选择策略
- 保证语义完整性
- 生成元数据
"""
import re
import uuid
from typing import List, Optional
from dataclasses import dataclass, field
from loguru import logger
import tiktoken

from backend.app.core.document_parser import ParsedDocument


@dataclass
class Chunk:
    """分块对象"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    chunk_index: int = 0
    token_count: int = 0
    metadata: dict = field(default_factory=dict)


class SmartChunker:
    """自适应智能分块器"""

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 64,
        min_chunk_size: int = 1,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        try:
            self.tokenizer = tiktoken.encoding_for_model("gpt-4o")
        except Exception:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        return len(self.tokenizer.encode(text))

    def chunk_document(
        self,
        parsed_doc: ParsedDocument,
        doc_id: str,
        kb_id: str,
        chunk_method: str = "smart",
    ) -> List[Chunk]:
        """根据文档类型和分块方式选择分块策略"""
        content = parsed_doc.content
        file_type = parsed_doc.metadata.get("file_type", "")
        file_name = parsed_doc.metadata.get("file_name", "")

        if not content.strip():
            logger.warning(f"Empty document: {file_name}")
            return []

        # 策略路由
        if chunk_method == "line":
            chunks = self._chunk_by_line(content)
        elif chunk_method == "paragraph":
            chunks = self._chunk_by_paragraph(content)
        elif self._is_markdown_structured(content):
            chunks = self._chunk_by_headers(content)
        elif self._is_qa_format(content):
            chunks = self._chunk_by_qa(content)
        elif file_type in (".xlsx", ".csv"):
            chunks = self._chunk_table(content)
        else:
            chunks = self._chunk_by_semantic_paragraph(content)

        # 过滤太短的块
        chunks = [c for c in chunks if len(c.content.strip()) >= self.min_chunk_size]

        # 添加元数据
        for i, chunk in enumerate(chunks):
            chunk.chunk_index = i
            chunk.token_count = self.count_tokens(chunk.content)
            chunk.metadata.update({
                "doc_id": doc_id,
                "kb_id": kb_id,
                "filename": file_name,
                "chunk_total": len(chunks),
            })

            # 页码映射 (PDF)
            if parsed_doc.pages:
                chunk.metadata["page"] = self._find_page(
                    chunk.content, parsed_doc.pages
                )

        logger.info(
            f"Document '{file_name}' chunked into {len(chunks)} chunks"
        )
        return chunks

    # ───────── 策略 1: 按标题层级分块 (Markdown / 结构化文档) ─────────
    def _chunk_by_headers(self, content: str) -> List[Chunk]:
        """基于 Markdown 标题层级的分块"""
        header_pattern = re.compile(r'^(#{1,4})\s+(.+)$', re.MULTILINE)

        sections = []
        last_pos = 0
        current_headers = {}

        for match in header_pattern.finditer(content):
            level = len(match.group(1))
            title = match.group(2).strip()

            if last_pos < match.start():
                section_text = content[last_pos:match.start()].strip()
                if section_text:
                    sections.append({
                        "content": section_text,
                        "headers": dict(current_headers),
                    })

            current_headers[f"h{level}"] = title
            # 清除更低层级标题
            for l in range(level + 1, 5):
                current_headers.pop(f"h{l}", None)

            last_pos = match.start()

        # 最后一段
        remaining = content[last_pos:].strip()
        if remaining:
            sections.append({
                "content": remaining,
                "headers": dict(current_headers),
            })

        # 对过长的 section 进一步拆分
        chunks = []
        for section in sections:
            text = section["content"]
            if self.count_tokens(text) > self.chunk_size:
                sub_chunks = self._split_text_with_overlap(text)
                for sc in sub_chunks:
                    chunks.append(Chunk(
                        content=sc,
                        metadata={"headers": section["headers"]},
                    ))
            else:
                chunks.append(Chunk(
                    content=text,
                    metadata={"headers": section["headers"]},
                ))

        return chunks

    # ───────── 策略 2: 语义段落分块 (通用) ─────────
    def _chunk_by_semantic_paragraph(self, content: str) -> List[Chunk]:
        """基于段落的语义分块，确保不在句子中间断开"""
        paragraphs = self._split_paragraphs(content)
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            test_chunk = (current_chunk + "\n\n" + para).strip() if current_chunk else para

            if self.count_tokens(test_chunk) <= self.chunk_size:
                current_chunk = test_chunk
            else:
                if current_chunk:
                    chunks.append(Chunk(content=current_chunk))

                # 如果单个段落就超长，需要进一步拆分
                if self.count_tokens(para) > self.chunk_size:
                    sub_chunks = self._split_text_with_overlap(para)
                    for sc in sub_chunks:
                        chunks.append(Chunk(content=sc))
                    current_chunk = ""
                else:
                    current_chunk = para

        if current_chunk:
            chunks.append(Chunk(content=current_chunk))

        return chunks

    # ───────── 策略 3: QA 分块 ─────────
    def _chunk_by_qa(self, content: str) -> List[Chunk]:
        """识别 Q&A 格式并按对分块"""
        qa_pattern = re.compile(
            r'(?:Q|问|问题)[：:\s]*(.+?)\n+(?:A|答|回答)[：:\s]*(.+?)(?=\n+(?:Q|问|问题)[：:\s]|\Z)',
            re.DOTALL | re.IGNORECASE,
        )
        matches = qa_pattern.findall(content)

        if not matches:
            return self._chunk_by_semantic_paragraph(content)

        chunks = []
        for q, a in matches:
            chunk_text = f"问：{q.strip()}\n答：{a.strip()}"
            chunks.append(Chunk(content=chunk_text, metadata={"type": "qa"}))

        return chunks

    # ───────── 策略 4: 表格分块 ─────────
    def _chunk_table(self, content: str) -> List[Chunk]:
        """表格类文档按行组分块"""
        lines = content.strip().split("\n")
        if not lines:
            return []

        # 假设第1-2行是表头
        header_lines = []
        data_lines = []
        for i, line in enumerate(lines):
            if i < 2 or line.startswith("|--"):
                header_lines.append(line)
            else:
                data_lines.append(line)

        header = "\n".join(header_lines)
        chunks = []
        current_rows = []

        for row in data_lines:
            current_rows.append(row)
            test_text = header + "\n" + "\n".join(current_rows)
            if self.count_tokens(test_text) > self.chunk_size:
                # 保存当前块
                if len(current_rows) > 1:
                    chunk_text = header + "\n" + "\n".join(current_rows[:-1])
                    chunks.append(Chunk(content=chunk_text, metadata={"type": "table"}))
                    current_rows = [row]
                else:
                    chunks.append(Chunk(content=test_text, metadata={"type": "table"}))
                    current_rows = []

        if current_rows:
            chunk_text = header + "\n" + "\n".join(current_rows)
            chunks.append(Chunk(content=chunk_text, metadata={"type": "table"}))

        return chunks

    # ───────── 辅助方法 ─────────
    def _split_text_with_overlap(self, text: str) -> List[str]:
        """按 token 数滑窗分割，保证有重叠"""
        sentences = self._split_sentences(text)
        chunks = []
        current = []
        current_tokens = 0

        for sent in sentences:
            sent_tokens = self.count_tokens(sent)
            if current_tokens + sent_tokens > self.chunk_size and current:
                chunks.append(" ".join(current))
                # 重叠: 保留最后几句
                overlap_tokens = 0
                overlap_start = len(current)
                for j in range(len(current) - 1, -1, -1):
                    overlap_tokens += self.count_tokens(current[j])
                    if overlap_tokens >= self.chunk_overlap:
                        overlap_start = j
                        break
                current = current[overlap_start:]
                current_tokens = sum(self.count_tokens(s) for s in current)

            current.append(sent)
            current_tokens += sent_tokens

        if current:
            chunks.append(" ".join(current))

        return chunks

    def _split_paragraphs(self, text: str) -> List[str]:
        """按段落分割"""
        return re.split(r'\n\s*\n', text)

    def _split_sentences(self, text: str) -> List[str]:
        """按句子分割 (中英文兼容)"""
        sentences = re.split(r'(?<=[。！？.!?])\s*', text)
        return [s.strip() for s in sentences if s.strip()]

    def _is_markdown_structured(self, content: str) -> bool:
        """检测是否有 Markdown 标题结构"""
        headers = re.findall(r'^#{1,4}\s+.+$', content, re.MULTILINE)
        return len(headers) >= 3

    def _is_qa_format(self, content: str) -> bool:
        """检测是否是 QA 格式"""
        qa_markers = re.findall(
            r'(?:^|\n)(?:Q|问|问题)[：:\s]', content, re.IGNORECASE
        )
        return len(qa_markers) >= 3

    def _find_page(self, chunk_text: str, pages: List[dict]) -> Optional[int]:
        """将 chunk 映射到 PDF 页码"""
        chunk_start = chunk_text[:100]
        for page in pages:
            if chunk_start in page.get("content", ""):
                return page["page"]
        return None

    # ───────── 策略 6: 按行分块 ─────────
    def _chunk_by_line(self, content: str) -> List[Chunk]:
        """按行分块，每行作为一个块"""
        lines = content.strip().split('\n')
        chunks = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 每行作为一个单独的块
            chunks.append(Chunk(content=line))
        
        return chunks

    # ───────── 策略 7: 按段落分块 ─────────
    def _chunk_by_paragraph(self, content: str) -> List[Chunk]:
        """按段落分块，每个段落作为一个块"""
        paragraphs = content.strip().split('\n\n')
        chunks = []
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # 每个段落作为一个单独的块
            chunks.append(Chunk(content=paragraph))
        
        return chunks