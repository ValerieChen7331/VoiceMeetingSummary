import whisper
import os
import subprocess
import tempfile
from config import Config
import streamlit as st


class AudioTranscriber:
    """Whisper 音檔轉錄器 (支援 m4a、wav、mp3、mp4)"""

    # 類別變數，避免重複載入 Whisper 模型，提高效能
    _whisper_model = None

    # def  voiceprint_recognition():
    #     # PaddleSpeech


    @classmethod
    def load_whisper_model(cls):
        """
        延遲載入 Whisper 模型 (Lazy Load)

        這樣可以避免在應用程式啟動時就加載模型，而是等到真正需要時才載入，
        以提高程式啟動速度。
        """
        if cls._whisper_model is None:
            try:
                # 載入 Whisper 語音轉錄模型 (使用 `Config.AUDIO_MODEL_TYPE` 指定模型類型)
                cls._whisper_model = whisper.load_model(Config.AUDIO_MODEL_TYPE)
            except Exception as error:
                st.error(f"❌ Whisper 模型載入失敗: {error}")
                return None
        return cls._whisper_model

    @classmethod
    def transcribe(cls, uploaded_audio):
        """
        **將上傳的音檔轉錄為逐字稿 (Speech-to-Text)**

        參數:
        - `uploaded_audio` (UploadedFile): 使用者上傳的音訊檔案 (m4a、wav、mp3、mp4)

        回傳:
        - `str`: 轉錄後的逐字稿文字 (若失敗則回傳 "")
        """

        # **步驟 1：嘗試載入 Whisper 模型**
        model = cls.load_whisper_model()
        if model is None:
            return ""

        # **步驟 2：檢查音檔是否為空**
        if uploaded_audio.size == 0:
            st.error("⚠️ 音檔為空，請重新上傳。")
            return ""

        # **步驟 3：取得音檔副檔名**
        file_extension = os.path.splitext(uploaded_audio.name)[-1].lower()

        # **步驟 4：將上傳的音檔儲存到暫存檔案**
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_audio:
            temp_audio.write(uploaded_audio.getbuffer())  # 將音檔內容寫入暫存檔案
            temp_audio_path = temp_audio.name  # 取得暫存檔案的完整路徑

        wav_audio_path = None  # 預先定義變數，以防止未賦值錯誤
        try:
            # **步驟 5：轉換音檔為 16kHz WAV**
            wav_audio_path = cls.convert_audio_to_wav(temp_audio_path, file_extension)
            if not wav_audio_path:
                st.error("⚠️ 音檔轉換失敗，請上傳有效音檔。")
                return ""

            # **步驟 6：使用 Whisper 進行語音轉文字**
            transcript_result = model.transcribe(wav_audio_path, language="zh", word_timestamps=True)  # 指定語言為繁體中文

            # 7️ 轉換 Whisper 結果為 **VTT 格式**
            vtt_output = cls.format_as_vtt(transcript_result)
            # st.write(type(vtt_output),vtt_output)
            return vtt_output  # 返回 VTT 格式的逐字稿

            # # **步驟 7：回傳轉錄結果**
            # return transcript_result.get("text", "")

        except Exception as error:
            # **步驟 8：錯誤處理**
            st.error(f"⚠️ 音檔轉錄失敗: {error}")
            return ""

        finally:
            # **步驟 9：確保刪除所有暫存檔案**
            os.remove(temp_audio_path)
            if wav_audio_path and os.path.exists(wav_audio_path):
                os.remove(wav_audio_path)

    @staticmethod
    def convert_audio_to_wav(input_path, file_extension):
        """
        **轉換音檔為 16kHz 單聲道 WAV 格式 (Whisper 最佳格式)**

        參數:
        - `input_path` (str): 原始音檔路徑
        - `file_extension` (str): 檔案副檔名 (用於判斷是否為 MP4)

        回傳:
        - `str`: 轉換後的 WAV 檔案路徑 (若失敗則回傳 None)
        """
        output_path = input_path.rsplit(".", 1)[0] + ".wav"  # 生成 WAV 輸出路徑

        try:
            # **步驟 1：決定 ffmpeg 指令**
            cmd = ["ffmpeg", "-y", "-i", input_path, "-q:a", "0", "-map", "a", output_path] \
                if file_extension == ".mp4" else \
                ["ffmpeg", "-y", "-i", input_path, "-ar", "16000", "-ac", "1", output_path]

            # **步驟 2：執行音訊轉換**
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

            # **步驟 3：確認輸出檔案是否成功生成**
            return output_path if os.path.exists(output_path) and os.path.getsize(output_path) > 0 else None

        except Exception as error:
            st.error(f"⚠️ 音檔轉換失敗 (ffmpeg): {error}")
            return None


    @staticmethod
    def format_as_vtt(transcript_result):
        """
        **將 Whisper 轉錄結果轉換為 VTT (WebVTT) 格式**

        參數:
        - `transcript_result` (dict): Whisper 轉錄結果

        回傳:
        - `str`: VTT 格式的字幕內容
        """
        vtt_output = ["WEBVTT\n"]  # VTT 標頭
        for segment in transcript_result["segments"]:
            start_time = segment["start"]
            end_time = segment["end"]
            text = segment["text"]

            # 轉換時間戳記格式 `00:00:01.500 --> 00:00:04.000`
            start_vtt_time = AudioTranscriber.format_timestamp(start_time)
            end_vtt_time = AudioTranscriber.format_timestamp(end_time)

            vtt_output.append(f"{start_vtt_time} --> {end_vtt_time}\n{text}\n")

        return "\n".join(vtt_output)

    @staticmethod
    def format_timestamp(seconds):
        """
        **將秒數轉換為 VTT 時間格式 (00:00:01.500)**
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds - int(seconds)) * 1000)

        return f"{hours:02}:{minutes:02}:{secs:02}.{milliseconds:03}"
