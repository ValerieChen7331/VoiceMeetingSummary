# 🔹 **應用程式設定**
class Config:
    LLM_MODEL_NAME = "gemma3:27b"
    LLM_API_BASE_URL = "http://10.5.61.81:11437"
    BACKGROUND_IMAGE_PATH = "bg.png"
    OUTPUT_FOLDER = "summaries"
    DEFAULT_USER_ID = "guest"
    DOCX_MIME_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    AUDIO_MODEL_TYPE = "medium"
    # MODEL: tiny, base, small,medium, (large, turbo)