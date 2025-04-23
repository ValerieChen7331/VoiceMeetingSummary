import streamlit as st

# 🔹 **會議記錄助理應用**
class MainPage():
    """會議記錄助理應用程式"""

    OPTIONS = {
        "audio_transcription": ("🎙️ 音檔轉逐字稿", ["m4a", "wav", "mp3", "mp4"]),
        "vtt_summary": ("📝 逐字稿 (VTT) 生成摘要", ["vtt"]),
        "audio_summary": ("🎙️+📝 音檔生成摘要", ["m4a", "wav", "mp3", "mp4"]),
    }

    # def run(self):
    #     """啟動應用程式"""
    #     self.show_app_header()
    #     selected_mode, uploaded_file, summary_prompt, is_submitted = self.show_sidebar()
    #
    #     if not (uploaded_file and is_submitted):
    #         return
    #
    #     if selected_mode == "audio_transcription":
    #         self.process_audio_transcription(uploaded_file)
    #     elif selected_mode == "vtt_summary":
    #         extracted_text = VTTProcessor.extract(uploaded_file.getvalue())
    #         if extracted_text:
    #             self.generate_summary(extracted_text, summary_prompt, uploaded_file)
    #     elif selected_mode == "audio_summary":
    #         transcript_text = self.process_audio_transcription(uploaded_file)
    #         if transcript_text:
    #             self.generate_summary(transcript_text.strip(), summary_prompt, uploaded_file)

    def show_app_header(self):
        """顯示標題與登出按鈕"""
        st.markdown('<div style="position:fixed; top:20px; right:20px;">', unsafe_allow_html=True)
        if st.button("LogOut"):
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