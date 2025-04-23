# 🔹 **匯入必要套件**
import streamlit as st
import os
import re
import base64
import tempfile
from io import BytesIO
from docxtpl import DocxTemplate
from langchain_openai import ChatOpenAI
import whisper
import subprocess

# 🔹 **頁面基本設定**
st.set_page_config(page_title="Meeting Summary Assistant", layout="wide")


# 🔹 **應用程式設定**
class Config:
    LLM_MODEL_NAME = "cwchang/llama-3-taiwan-8b-instruct-dpo:f16"
    LLM_API_BASE_URL = "http://10.5.61.81:11436/v1"
    BACKGROUND_IMAGE_PATH = "bg.jpg"
    OUTPUT_FOLDER = "summaries"
    DEFAULT_USER_ID = "guest"
    DOCX_MIME_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    AUDIO_MODEL_TYPE = "base"


# 🔹 **Whisper 音檔轉錄**
class AudioTranscriber:
    """Whisper 音檔轉錄器 (支援 m4a、wav、mp3、mp4)"""

    _whisper_model = None

    @classmethod
    def load_whisper_model(cls):
        """載入 Whisper 模型 (Lazy Load)"""
        if cls._whisper_model is None:
            try:
                cls._whisper_model = whisper.load_model(Config.AUDIO_MODEL_TYPE)
            except Exception as error:
                st.error(f"❌ Whisper 模型載入失敗: {error}")
                return None
        return cls._whisper_model

    @classmethod
    def transcribe(cls, uploaded_audio_file):
        """將音檔轉錄為逐字稿"""
        whisper_model = cls.load_whisper_model()
        if whisper_model is None:
            return ""

        if uploaded_audio_file.size == 0:
            st.error("⚠️ 音檔為空，請重新上傳。")
            return ""

        file_extension = os.path.splitext(uploaded_audio_file.name)[-1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_audio:
            temp_audio.write(uploaded_audio_file.getbuffer())
            temp_audio_path = temp_audio.name

        try:
            wav_audio_path = cls.convert_to_wav(temp_audio_path, file_extension)
            if not wav_audio_path:
                st.error("⚠️ 音檔轉換失敗，請上傳有效音檔。")
                return ""

            transcript_result = whisper_model.transcribe(wav_audio_path, language="zh")
            return transcript_result.get("text", "")

        except Exception as error:
            st.error(f"⚠️ 音檔轉錄失敗: {error}")
            return ""

        finally:
            os.remove(temp_audio_path)
            if wav_audio_path and os.path.exists(wav_audio_path):
                os.remove(wav_audio_path)

    @staticmethod
    def convert_to_wav(input_audio_path, file_extension):
        """轉換音檔為 16kHz 單聲道 WAV"""
        output_wav_path = input_audio_path.rsplit(".", 1)[0] + ".wav"

        try:
            conversion_cmd = ["ffmpeg", "-y", "-i", input_audio_path, "-ar", "16000", "-ac", "1", output_wav_path]
            subprocess.run(conversion_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return output_wav_path if os.path.exists(output_wav_path) and os.path.getsize(output_wav_path) > 0 else None
        except Exception as error:
            st.error(f"⚠️ 音檔轉換失敗: {error}")
            return None


# 🔹 **LLM 摘要生成**
class LLMTextSummarizer:
    """使用 LLM 生成文本摘要"""

    @staticmethod
    def generate(text_segments, prompt_template):
        """使用 LLM 生成摘要"""
        model = ChatOpenAI(api_key="ollama", model=Config.LLM_MODEL_NAME, base_url=Config.LLM_API_BASE_URL)
        summaries = []

        for segment in text_segments:
            prompt = prompt_template.format(context=segment)
            response = model.invoke(prompt)
            if response and response.content:
                summaries.append(response.content)

        return "\n".join(summaries)


# 🔹 **Word 檔案產生**
class WordDocumentGenerator:
    """產生 Word 文件"""

    @staticmethod
    def create(summary_text):
        """建立 Word 文件"""
        doc = DocxTemplate("template.docx")
        cleaned_text = re.sub(r'(#+|\*\*|__|\*|_|\[.*?\]\(.*?\)|[-*])', '', summary_text)
        doc.render({'summary': cleaned_text})

        buffer = BytesIO()
        doc.save(buffer)
        return buffer.getvalue()


# 🔹 **VTT 逐字稿處理**
class VTTProcessor:
    """處理 VTT 檔案，提取純文字"""

    @staticmethod
    def extract(vtt_data):
        """從 VTT 檔案提取純文字內容"""
        try:
            lines = vtt_data.decode('utf-8').splitlines()
            return " ".join(
                line.strip() for line in lines if line and "-->" not in line and not line.startswith("WEBVTT"))
        except Exception as error:
            st.error(f"⚠️ VTT 解析失敗: {error}")
            return ""


# 🔹 **會議記錄助理應用**
class MeetingSummaryApp:
    """會議記錄助理應用程式"""

    OPTIONS = {
        "audio_transcription": ("🎙️ 音檔轉逐字稿", ["m4a", "wav", "mp3", "mp4"]),
        "vtt_summary": ("📝 逐字稿 (VTT) 生成摘要", ["vtt"]),
        "audio_summary": ("🎙️+📝 音檔生成摘要", ["m4a", "wav", "mp3", "mp4"]),
    }

    def run(self):
        """啟動應用程式"""
        self.show_app_header()
        selected_mode, uploaded_file, summary_prompt, is_submitted = self.show_sidebar()

        if not (uploaded_file and is_submitted):
            return

        if selected_mode == "audio_transcription":
            self.process_audio_transcription(uploaded_file)
        elif selected_mode == "vtt_summary":
            extracted_text = VTTProcessor.extract(uploaded_file.getvalue())
            if extracted_text:
                self.generate_summary(extracted_text, summary_prompt, uploaded_file)
        elif selected_mode == "audio_summary":
            transcript_text = self.process_audio_transcription(uploaded_file)
            if transcript_text:
                self.generate_summary(transcript_text.strip(), summary_prompt, uploaded_file)

    def show_app_header(self):
        """顯示標題與登出按鈕"""
        st.markdown('<div style="position:fixed; top:20px; right:20px;">', unsafe_allow_html=True)
        if st.button("Log Out"):
            st.session_state.clear()
        st.markdown('</div>', unsafe_allow_html=True)
        st.title("🔗 會議記錄助理 - Meeting Summary Assistant 🔗")

    def show_sidebar(self):
        """顯示側邊欄選擇功能"""
        st.sidebar.title("操作選擇")
        options = [opt[0] for opt in self.OPTIONS.values()]
        selected_mode = next(
            key for key, value in self.OPTIONS.items() if value[0] == st.sidebar.radio("請選擇操作模式：", options, key="mode_selection"))
        uploaded_file = st.sidebar.file_uploader("請上傳檔案：", type=self.OPTIONS[selected_mode][1])
        summary_prompt = st.sidebar.text_area("自訂摘要提示語：", "根據以下對話內容生成摘要，並加上標題：{context}")
        is_submitted = st.sidebar.button("開始執行")
        return selected_mode, uploaded_file, summary_prompt, is_submitted


if __name__ == "__main__":
    MeetingSummaryApp().run()
