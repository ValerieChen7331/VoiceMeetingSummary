# 匯入必要套件
import streamlit as st
import os
import random
import re
from config import Config
from io import BytesIO
from docxtpl import DocxTemplate

# 🔹 **Word 檔案產生**
class DocumentGenerator:
    """產生 Word 文件"""

    @staticmethod
    def create_word_document(summary_text):
        """建立 Word 文件"""
        # 載入 Word 模板檔案 (template.docx 必須存在於程式目錄中)
        doc = DocxTemplate("template.docx")

        # 清理摘要內容，移除 Markdown 標記符號避免干擾 Word 顯示
        clean_summary = re.sub(
            r'(#+|\*\*|__|\*|_|\[.*?\]\(.*?\)|[-*])',
            '',
            summary_text
        )

        # 將清理後的摘要填入模板中的 {{ summary }} 占位符
        doc.render({'summary': clean_summary})

        # 將 Word 文件寫入記憶體緩衝區
        buffer = BytesIO()
        doc.save(buffer)

        # 回傳 Word 檔案的二進位內容
        return buffer.getvalue()


# 🔹 **VTT 逐字稿處理**
    @staticmethod
    def extract_VTT(vtt_bytes):
        """從 VTT 檔案提取純文字內容"""
        try:
            # 將 VTT 位元組資料用 UTF-8 編碼解碼成文字
            lines = vtt_bytes.decode('utf-8').splitlines()

            # 過濾掉時間軸標記、標頭與空行，只保留字幕文本
            return " ".join(
                line.strip()
                for line in lines
                if line and "-->" not in line and not line.startswith("WEBVTT")
            )
        except Exception as e:
            # 如果解析過程中出現錯誤，顯示錯誤提示並回傳空字串
            st.error(f"⚠️ VTT 解析失敗: {e}")
            return ""

    @staticmethod
    def save_files(summary, prompt, file, user_id):
        user_folder = os.path.join(Config.OUTPUT_FOLDER, user_id)
        os.makedirs(user_folder, exist_ok=True)
        suffix = random.randint(1000, 9999)
        with open(f"{user_folder}/summary_{suffix}.txt", "w", encoding="utf-8") as f:
            f.write(summary)
        with open(f"{user_folder}/prompt_{suffix}.txt", "w", encoding="utf-8") as f:
            f.write(prompt)
        with open(f"{user_folder}/{file.name}_{suffix}", "wb") as f:
            f.write(file.getbuffer())



    @staticmethod
    def clean_text(text):
        text = re.sub(r'\S+-\S+/\d+-\d+\s+', '', text)
        return "\n\n".join(line.strip() for line in text.split('\n') if line.strip())

    @staticmethod
    def split_text(text, max_tokens=7000):
        words, chunks, chunk, length = text.split(), [], [], 0
        for word in words:
            length += len(word) + 1
            chunk.append(word)
            if length >= max_tokens:
                chunks.append(" ".join(chunk))
                chunk, length = [], 0
        if chunk:
            chunks.append(" ".join(chunk))
        return chunks