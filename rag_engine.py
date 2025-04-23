import streamlit as st
import requests
import json
# from app import MeetingSummaryApp  # 導入主應用
from controllers.meeting_controller import MeetingSummaryApp
from config import Config

# 🔹 **Streamlit 應用類**
class StreamlitLoginApp:
    """管理 Streamlit 登入與主應用的邏輯"""

    LOGIN_API_URL = "http://10.5.61.129:6666/auth/login"
    HEADERS = {'Content-Type': 'application/json'}

    def __init__(self):
        """初始化 session_state"""
        self._initialize_session_state()

        # 設定 Streamlit 頁面配置
        st.set_page_config(
            page_title="Meeting Summary Assistant",
            page_icon="🔗",
            layout="wide",
            initial_sidebar_state="expanded"
        )

    def _initialize_session_state(self):
        """初始化 session_state"""
        st.session_state.setdefault("authenticated", True)
        st.session_state.setdefault("user_id", Config.DEFAULT_USER_ID)

    def login_api_request(self, user_id, password):
        """向 API 發送登入請求，回傳結果"""
        try:
            response = requests.post(
                self.LOGIN_API_URL,
                headers=self.HEADERS,
                data=json.dumps({"user_id": user_id, "password": password})
            )
            response.raise_for_status()  # 確保 API 回應正常
            return response.json()
        except requests.exceptions.RequestException as error:
            st.error(f"⚠️ 伺服器錯誤，請稍後再試: {error}")
            return None

    def handle_login(self, user_id, password):
        """處理登入邏輯"""
        if not user_id or not password:
            st.warning("⚠️ 請輸入工號與密碼！")
            return

        if st.session_state["authenticated"]:
            return  # 已登入，不重複請求

        response_data = self.login_api_request(user_id, password)
        if response_data and response_data.get("login", False):
            st.session_state["authenticated"] = True
            st.session_state["user_id"] = user_id
            st.rerun()  # 切換到主應用
        else:
            st.error("❌ 工號或密碼輸入錯誤！")

    def logout(self):
        """登出並重置 session"""
        st.session_state["authenticated"] = False
        st.session_state["user_id"] = None
        st.rerun()

    def display_login_page(self):
        """顯示登入畫面"""
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

        with col2:  # 左側放置圖標
            st.image("assets/summary_icon.png", use_column_width=True)

        with col3:  # 右側放置登入表單
            st.title("南亞會議摘要")
            with st.form("login_form"):
                user_id = st.text_input("ID", key="user_id_input")
                password = st.text_input("Password", type="password", key="password_input")
                submitted = st.form_submit_button("登入")

            if submitted:
                self.handle_login(user_id, password)

    def display_main_app(self):
        """顯示主應用"""
        st.sidebar.button("登出", on_click=self.logout)
        MeetingSummaryApp().run()

    def run(self):
        """執行應用程式"""
        if st.session_state["authenticated"]:
            self.display_main_app()
        else:
            self.display_login_page()


# 🔹 **執行應用**
if __name__ == "__main__":
    app = StreamlitLoginApp()
    app.run()
