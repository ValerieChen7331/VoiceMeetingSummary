import streamlit as st
from models.audio_transcriber import AudioTranscriber
from models.llm_summarizer import LLMTextSummarizer
from models.document_generator import DocumentGenerator
from config import Config
import base64


class MeetingSummaryApp:
    """會議記錄助理應用程式"""
    OPTIONS = {
        "audio_transcription": ("🎙️ 音檔轉逐字稿", ["m4a", "wav", "mp3", "mp4"]),
        "vtt_summary": ("📝 逐字稿 (VTT) 生成摘要", ["vtt"]),
        "audio_summary": ("🎙️+📝 音檔生成摘要", ["m4a", "wav", "mp3", "mp4"]),
    }

    def run(self):
        """啟動應用程式"""
        # 設定背景圖片
        # # 設定背景圖片
        # page_bg_img = '''
        # <style>
        # .stApp {
        #     background-color: #ebf2f3;
        #     background-image: url("data:image/svg+xml,%3Csvg width='44' height='12' viewBox='0 0 44 12' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M20 12v-2L0 0v10l4 2h16zm18 0l4-2V0L22 10v2h16zM20 0v8L4 0h16zm18 0L22 8V0h16z' fill='%23c1d0dc' fill-opacity='0.45' fill-rule='evenodd'/%3E%3C/svg%3E");
        #     background-size: cover;
        #     background-position: center;
        # }
        # </style>
        # '''
        #
        # # 注入 CSS
        # st.markdown(page_bg_img, unsafe_allow_html=True)

        self.set_background(self.load_base64_image(Config.BACKGROUND_IMAGE_PATH))
        # 顯示標題
        self.show_app_header()
        # 取得使用者選擇的模式、上傳的檔案和輸入的提示語
        selected_mode, uploaded_file, summary_prompt, is_submitted = self.show_sidebar()

        # 如果未上傳檔案或未點擊執行按鈕，就不執行任何操作
        if not (uploaded_file and is_submitted):
            return

        if selected_mode == "audio_transcription":
            self._handle_transcription(uploaded_file)
        elif selected_mode == "vtt_summary":
            extracted_text = DocumentGenerator.extract_VTT(uploaded_file.getvalue())
            if extracted_text:  # 確保 VTT 內容不為空
                self._handle_summary(extracted_text, summary_prompt, uploaded_file)
            else:
                st.error("⚠️ VTT 解析失敗，請上傳有效的逐字稿檔案")
        elif selected_mode == "audio_summary":
            transcript_text = self._handle_transcription(uploaded_file) or ""  # 確保轉錄內容不為 None
            clean_text = DocumentGenerator.clean_text(transcript_text)
            if clean_text.strip():  # 避免處理空白內容
                self._handle_summary(transcript_text.strip(), summary_prompt, uploaded_file)
            else:
                st.error("⚠️ 轉錄內容為空，無法生成摘要")

    @staticmethod
    def load_base64_image(path):
        with open(path, "rb") as img:
            return base64.b64encode(img.read()).decode()

    @staticmethod
    def set_background(image_base64):
        st.markdown(f"""
                <style>
                    #MainMenu, footer, header, [data-testid="stSidebarNav"] {{ display: none; }}
                    .stApp {{
                        background: url(data:image/jpg;base64,{image_base64}) no-repeat center center fixed;
                        background-size: cover;
                    }}
                </style>
            """, unsafe_allow_html=True)

    def show_app_header_1(self):
        """顯示標題與登出按鈕"""
        st.markdown('<div style="position:fixed; top:20px; right:20px;">', unsafe_allow_html=True)

        # if st.button("LogOut"):
        #     st.session_state.clear()

        st.markdown('</div>', unsafe_allow_html=True)
        st.title("🔗 會議記錄助理 - Meeting Summary Assistant 🔗")

    # def show_app_header(self):
    #     """顯示標題與右上角 LOGO"""
    #     # 右上角顯示 LOGO
    #     col1, col2 = st.columns([6, 1])
    #     with col2:
    #         st.image("assets/summary_icon.png", width=150)  # 載入圖片
    #
    #     st.title("🔗 會議記錄助理 - Meeting Summary Assistant 🔗")



    @staticmethod
    def load_image(self, image_path):
        """讀取圖片並轉換為 Base64"""
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()

    def show_app_header(self):
        """顯示標題與右上角 LOGO (標題可覆蓋圖片)"""
        """讀取圖片並轉換為 Base64"""
        with open("assets/summary_icon.png", "rb") as img_file:
            image_base64 = base64.b64encode(img_file.read()).decode()

        st.markdown(
            f"""
            <style>
                .header-container {{
                    position: relative;
                    width: 100%;
                    text-align: left; 
                    padding: 20px 0;
                }}
                .header-container img {{
                    position: absolute;
                    top: 0;
                    right: 0;
                    width: 20%;
                    opacity: 0.9;  /* 調整透明度，讓標題更清晰 */
                }}
                .header-container h1 {{
                    position: relative;
                    z-index: 10;  /* 確保標題在圖片上方 */
                    font-size: 2.5em;
                    font-weight: bold;
                }}
            </style>
            <div class="header-container">
                <img src="data:image/png;base64,{image_base64}">
                <h1>🔗會議記錄助理 - Meeting Summary Assistant🔗</h1>
            </div>
            """,
            unsafe_allow_html=True
        )

    def show_sidebar(self):
        """顯示側邊欄選擇功能"""
        # st.sidebar.image("assets/summary_icon.png", width=300)  # 側邊欄 LOGO
        st.sidebar.title("操作選擇")
        # 顯示選項按鈕
        options_display = [opt[0] for opt in self.OPTIONS.values()]
        action = st.sidebar.radio("請選擇操作模式：", options_display)
        selected_key = next(key for key, value in self.OPTIONS.items() if value[0] == action)
        file_types = self.OPTIONS[selected_key][1]
        # 上傳檔案欄位
        uploaded_file = st.sidebar.file_uploader("請上傳檔案：", type=file_types)
        # 自訂摘要提示語
        prompt = st.sidebar.text_area("自訂摘要提示語：", "根據以下對話內容生成摘要，並加上標題：{context}")
        # 執行按鈕
        submitted = st.sidebar.button("開始執行")
        return selected_key, uploaded_file, prompt, submitted

    # 音檔轉逐字稿處理
    def _handle_transcription_1(self, uploaded_file):
        """處理音檔轉逐字稿"""
        if uploaded_file is None:
            st.warning("⚠️ 請上傳音檔")
            return ""

        with st.spinner("音訊轉錄中..."):  # 顯示等待提示
            audio_transcriber = AudioTranscriber()
            transcription = audio_transcriber.transcribe(uploaded_file)

        if transcription:
            st.subheader("📝 逐字稿結果")
            # st.write(transcription)  # 顯示逐字稿內容
            # 🔹 使用 CSS 設定固定高度 + 捲動條
            st.markdown(
                f"""
                       <style>
                           .transcription-box {{
                               width: 50%;
                               height: 300px;  /* 設定固定高度 */
                               overflow-y: scroll;  /* 啟用垂直滾動 */
                               padding: 10px;
                               border: 2px solid #ccc;
                               border-radius: 10px;
                               background-color: #f9f9f9;
                               font-family: Arial, sans-serif;
                               white-space: pre-wrap;
                           }}
                       </style>
                       <div class="transcription-box">{transcription}</div>
                       """,
                unsafe_allow_html=True
            )

            # 允許下載逐字稿檔案
            st.download_button(
                "📥 下載逐字稿 (.txt)",
                transcription,
                f"{uploaded_file.name}_transcription.txt",
                mime="text/plain"
            )
            return transcription  # **確保回傳非 None 的內容**
        else:
            st.error("⚠️ 音檔轉錄失敗")
            return ""

    def _handle_transcription(self, uploaded_file):
        """處理音檔轉逐字稿"""
        if uploaded_file is None:
            st.warning("⚠️ 請上傳音檔")
            return ""

        with st.spinner("音訊轉錄中..."):  # 顯示等待提示
            audio_transcriber = AudioTranscriber()
            transcription = audio_transcriber.transcribe(uploaded_file)

        if transcription:
            st.subheader("📝 逐字稿")
            # 🔹 顯示滾動視窗
            st.text_area("內容編輯", transcription, height=400)

            # 允許下載逐字稿檔案
            st.download_button(
                "📥 下載逐字稿 (.vtt)",
                transcription,
                f"{uploaded_file.name}_transcription.txt",
                mime="text/plain"
            )
            return transcription  # **確保回傳非 None 的內容**
        else:
            st.error("⚠️ 音檔轉錄失敗")
            return ""

    # 摘要生成處理
    def _handle_summary(self, text, prompt, uploaded_file):
        with st.spinner("摘要生成中..."):  # 顯示等待提示
            chunks = DocumentGenerator.split_text(text)  # 將文本切塊
            summary = LLMTextSummarizer.summary_generator(chunks, prompt)  # 生成摘要
        if summary:
            st.subheader("📄 摘要結果")
            st.write(summary)  # 顯示摘要內容
            user_id = st.session_state.get("user_id", Config.DEFAULT_USER_ID)
            # 儲存摘要、提示語與原始檔案
            DocumentGenerator.save_files(summary, prompt, uploaded_file, user_id)
            # 提供 txt 下載
            st.download_button(
                "📥 下載摘要 (.txt)",
                summary,
                f"{uploaded_file.name}_summary.txt",
                mime="text/plain"
            )
            # 提供 docx 下載
            st.download_button(
                "📥 下載摘要 (.docx)",
                DocumentGenerator.create_word_document(summary),
                f"{uploaded_file.name}_summary.docx",
                mime=Config.DOCX_MIME_TYPE
            )
        else:
            st.error("⚠️ 摘要生成失敗")  # 若摘要失敗顯示錯誤
