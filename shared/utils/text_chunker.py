"""
文本分块工具 - 将大文档按段落/句子边界切分为适合 LLM 处理的块

Usage:
    from shared.utils.text_chunker import split_text_into_chunks

    chunks = split_text_into_chunks(long_text, max_chars=6000)
"""
import re
from typing import List


def estimate_token_count(text: str) -> int:
    """
    粗略估算 token 数量。
    中文约 1 字 ≈ 1.5 token，英文约 1 词 ≈ 1.3 token。
    此处采用保守估算: 每 2 个字符 ≈ 1 token。
    """
    return len(text) // 2


def split_text_into_chunks(
    text: str,
    max_chars: int = 6000,
    overlap_chars: int = 200,
) -> List[str]:
    """
    将文本按自然段落边界分块。

    Args:
        text: 原始文本
        max_chars: 每块最大字符数（默认 6000 ≈ 3000 tokens）
        overlap_chars: 相邻块重叠字符数（保持上下文连续性）

    Returns:
        文本块列表
    """
    text = text.strip()
    if not text:
        return []

    if len(text) <= max_chars:
        return [text]

    paragraphs = re.split(r'\n{2,}', text)
    
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if len(para) > max_chars:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""
            sub_chunks = _split_long_paragraph(para, max_chars, overlap_chars)
            chunks.extend(sub_chunks)
            continue

        if len(current_chunk) + len(para) + 2 > max_chars:
            chunks.append(current_chunk.strip())
            if overlap_chars > 0 and current_chunk:
                current_chunk = current_chunk[-overlap_chars:].strip() + "\n\n" + para
            else:
                current_chunk = para
        else:
            if current_chunk:
                current_chunk += "\n\n" + para
            else:
                current_chunk = para

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def _split_long_paragraph(
    text: str,
    max_chars: int,
    overlap_chars: int,
) -> List[str]:
    """将超长段落按句子边界分割"""
    sentences = re.split(r'(?<=[。！？.!?\n])\s*', text)

    chunks = []
    current = ""

    for sent in sentences:
        sent = sent.strip()
        if not sent:
            continue

        if len(current) + len(sent) + 1 > max_chars:
            if current:
                chunks.append(current.strip())
                if overlap_chars > 0:
                    current = current[-overlap_chars:].strip() + " " + sent
                else:
                    current = sent
            else:
                chunks.append(sent[:max_chars])
                current = sent[max_chars:]
        else:
            current = current + " " + sent if current else sent

    if current.strip():
        chunks.append(current.strip())

    return chunks
