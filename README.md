# meeting_summary_app
## 專案目錄結構

```plaintext
meeting_summary_app/
│── app.py  # 主程式
│── config.py  # 配置文件
│── controllers/
│   ├── meeting_controller.py  # 控制邏輯
│── models/
│   ├── audio_transcriber.py  # Whisper 音檔處理
│   ├── llm_summarizer.py  # LLM 文字摘要
│── views/
│   ├── ui.py  # UI 組件

├── requirements.txt       # 依賴套件列表
├── Dockerfile             # Docker 部署設定
├── template.docx          # Word 模板
├── assets/
│   └── summary_icon.png   # 側邊欄 icon 圖示
├── bg.jpg                 # 背景圖片
└── summaries/             # 產出檔案儲存資料夾


```
## 詳細說明

### 啟動程式
- Model (數據處理) → audio_transcriber.py, llm_summarizer.py
View (界面) → ui.py
Controller (邏輯) → meeting_controller.py