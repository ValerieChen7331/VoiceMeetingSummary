# 🔗 Meeting Summary Assistant 會議記錄助理

本專案為一款基於 **Streamlit** 的 AI 工具，結合語音轉文字與摘要生成模型，可自動將會議錄音或逐字稿轉換為條列式會議記錄，大幅減少人工紀錄時間，提升效率與準確度。

---

## 🚀 功能特色

### 🔐 使用者認證系統
- 整合 API 登入驗證
- 支援工號與密碼認證
- 安全的 Session 管理
- 個人化檔案儲存空間

### 🎙️ 音檔轉逐字稿
- 上傳錄音檔（支援 `.m4a`、`.wav`、`.mp3`、`.mp4`）
- 使用 Whisper 模型進行中文語音辨識
- 自動轉換為 16kHz 單聲道 WAV 格式
- 輸出 VTT 格式逐字稿（含時間戳記）
- 可編輯與下載轉錄結果

### 📝 逐字稿摘要生成
- 上傳 `.vtt` 格式逐字稿
- 自訂提示語引導摘要風格
- 智能文本分段處理（避免超出 Token 限制）
- 自動生成重點摘要
- 支援 `.txt` 與 `.docx` 格式下載

### 🎙️+📝 音檔直接生成摘要
- 僅需上傳錄音檔
- 自動完成語音轉文字與摘要生成兩步驟
- 快速取得會議重點
- 一鍵下載完整會議記錄

---

## 🧩 架構與模組

```
VoiceMeetingSummary_GIT/
├── assets/                     # 靜態資源
│   ├── bg_2.png               # 背景圖片
│   └── summary_icon.png       # 應用程式圖示
├── controllers/                # 控制層
│   └── meeting_controller.py  # 主視覺頁面與功能流程控制
├── models/                    # 模型層
│   ├── audio_transcriber.py   # 語音辨識模組（Whisper）
│   ├── document_generator.py  # 檔案處理、儲存與分段
│   └── llm_summarizer.py     # 摘要生成模組（LLM）
├── uploads/                   # 上傳檔案暫存
├── outputs/                   # 輸出檔案儲存
├── config.py                  # 設定檔
├── rag_engine.py             # 主程式入口點（含登入系統）
├── README.md                 # 專案說明文件
├── requirements.txt          # Python 依賴套件
├── template.docx            # Word 文件範本
└── Dockerfile               # Docker 容器設定
```

### 核心模組說明
- **rag_engine.py**：主程式入口點，包含登入系統與主應用程式邏輯
- **meeting_controller.py**：會議記錄助理核心功能控制
- **audio_transcriber.py**：語音辨識模組（使用 Whisper 模型，支援中文轉錄）
- **llm_summarizer.py**：摘要生成模組（整合大型語言模型）
- **document_generator.py**：文件處理模組（VTT解析、Word生成、檔案儲存）
- **config.py**：應用程式設定（背景圖路徑、使用者ID預設值、API設定等）

---

## 🖥️ 使用方式

### 1. 環境需求
- **Python**: 3.10
- **作業系統**: Windows / macOS / Linux
- **瀏覽器**: Chrome / Firefox / Safari（建議）

### 2. 快速開始

```bash
# 安裝依賴套件
pip install -r requirements.txt

# 啟動應用程式
streamlit run rag_engine.py
```

> 🌐 **存取網址**: `http://10.5.61.81:18511/`

### 3. 操作流程

#### 步驟 1：使用者登入
- 輸入工號與密碼
- 系統驗證身份（連接內部 API）
- 登入成功後進入主功能界面

#### 步驟 2：選擇功能模式
- **🎙️ 音檔轉逐字稿**：僅轉錄音檔為文字
- **📝 逐字稿生成摘要**：上傳現有 VTT 檔案生成摘要
- **🎙️+📝 音檔生成摘要**：一步完成轉錄與摘要

#### 步驟 3：上傳檔案
- **音檔格式**：`.m4a`、`.wav`、`.mp3`、`.mp4`
- **逐字稿格式**：`.vtt`
- **檔案大小**：建議小於 100MB

#### 步驟 4：自訂設定（可選）
- 修改預設提示語以引導摘要風格
- 系統會記住您的提示語偏好
- 支援繁體中文輸出

#### 步驟 5：執行處理
- 點擊「開始執行」按鈕
- 系統顯示即時處理進度
- 耐心等待處理完成

#### 步驟 6：檢視與下載結果
- **逐字稿**：`.vtt` 格式（含時間戳記）
- **摘要檔案**：`.txt`、`.docx` 格式
- 所有檔案自動儲存至個人資料夾

---

## 📋 技術架構

### 主要依賴套件
- **Streamlit**: Web 應用程式框架
- **OpenAI Whisper**: 語音轉文字（支援中文）
- **ffmpeg**: 音檔格式轉換（需系統安裝）
- **requests**: API 請求處理
- **python-docx / docxtpl**: Word 文件生成與模板處理
- **Transformers**: 自然語言處理

### 系統需求
- **Python**: 3.10+
- **記憶體**: 建議 8GB 以上
- **硬碟空間**: 2GB（含 Whisper 模型）
- **網路**: 需連接內部 API 服務

### 模型資訊
- **語音模型**: Whisper (base/small/medium 可配置)
- **自動下載**: 首次使用會自動下載模型檔案
- **語言支援**: 主要針對繁體中文優化

---

## 🔧 設定檔說明

### config.py 主要參數
```python
# API 設定
LOGIN_API_URL = "http://10.5.61.129:6666/auth/login"

# 路徑設定
BACKGROUND_IMAGE_PATH = "assets/bg_2.png"
UPLOAD_PATH = "uploads/"
OUTPUT_FOLDER = "outputs/"

# Whisper 模型設定
AUDIO_MODEL_TYPE = "base"  # 可選: tiny, base, small, medium, large

# 預設值
DEFAULT_USER_ID = "user_001"
```

### 環境變數（可選）
```bash
# 設定 API 端點
export MEETING_API_URL="http://your-api-server:port"

# 設定模型類型
export WHISPER_MODEL="medium"
```
---

## 🛠️ 開發指南
### 程式碼結構
- **MVC 架構**: 控制層、模型層分離
- **模組化設計**: 各功能獨立模組
- **錯誤處理**: 完整的異常捕獲機制
- **日誌記錄**: 詳細的操作日誌

---

## 🔍 疑難排解

### 常見問題
1. **音檔轉錄失敗**
   - 檢查 ffmpeg 是否正確安裝
   - 確認音檔格式是否支援
   - 檢查檔案大小是否過大

2. **登入無法成功**
   - 確認 API 端點連線狀態
   - 檢查工號密碼是否正確
   - 查看網路連線是否正常

3. **摘要生成失敗**
   - 檢查逐字稿內容是否完整
   - 確認 LLM 服務是否正常
   - 檢查提示語格式是否正確

### 效能優化建議
- 使用較小的 Whisper 模型（tiny/base）提升速度
- 定期清理 uploads 和 outputs 資料夾
- 建議音檔長度控制在 60 分鐘內

---

## 📞 技術支援

### 聯繫方式
- **問題回報**: 請建立 GitHub Issue
- **功能建議**: 提交 Feature Request
- **程式貢獻**: 歡迎 Pull Request

### 更新維護
- **版本發布**: 遵循語意化版本號
- **安全更新**: 定期更新依賴套件
- **功能迭代**: 根據使用者回饋持續改進

---

## 📄 授權資訊

本專案為內部開發使用，採用內部授權條款。如需商業應用或對外授權，請聯繫開發團隊。

---

## 🎯 開始使用

1. **環境準備**: 確保 Python 3.10+ 已安裝
2. **套件安裝**: `pip install -r requirements.txt`
3. **服務啟動**: `streamlit run rag_engine.py`
4. **開啟瀏覽器**: 前往 `http://10.5.61.81:18511/`
5. **登入系統**: 使用您的工號與密碼
6. **開始使用**: 上傳音檔，享受 AI 助理服務！

---

*最後更新：2025年6月*