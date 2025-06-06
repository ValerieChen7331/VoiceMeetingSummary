import whisper
import os
import subprocess
import tempfile
import streamlit as st


class AudioTranscriber:
    """
    音檔轉錄系統（只使用 Whisper 模型）
    - 支援多種音檔格式：mp3、wav、m4a、mp4 等
    - 不進行語者辨識（不使用 PaddleSpeech）
    """

    _whisper_model = None  # Whisper 模型快取，避免每次都重新載入模型

    def __init__(self):
        """初始化 Whisper 模型（僅載入一次）"""
        if AudioTranscriber._whisper_model is None:
            # 載入 Whisper base 模型（支援中文）
            AudioTranscriber._whisper_model = whisper.load_model("base")

    def transcribe(self, uploaded_audio):
        """
        將上傳的音檔轉為逐字稿，並輸出為 VTT 字幕格式

        參數:
        - uploaded_audio: Streamlit 的 UploadedFile 音檔物件

        回傳:
        - VTT 格式字串，內含時間戳記與轉錄內容
        """
        if uploaded_audio.size == 0:
            st.error("⚠️ 音檔為空，請重新上傳。")
            return ""

        file_extension = os.path.splitext(uploaded_audio.name)[-1].lower()  # 取得副檔名

        # 將音檔暫存至本地，避免直接讀取上傳物件造成錯誤
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_audio:
            temp_audio.write(uploaded_audio.getbuffer())  # 寫入暫存檔
            temp_audio_path = temp_audio.name  # 儲存暫存檔路徑

        wav_audio_path = None  # WAV 格式音檔路徑（Whisper 需要 16kHz 單聲道）
        try:
            # 將原始音檔轉為 Whisper 支援格式
            wav_audio_path = self.convert_audio_to_wav(temp_audio_path, file_extension)
            if not wav_audio_path:
                st.error("⚠️ 音檔轉換失敗，請上傳有效音檔。")
                return ""

            # 使用 Whisper 進行語音轉文字（支援中文）
            transcript_result = self._whisper_model.transcribe(
                wav_audio_path,
                language="zh",
                word_timestamps=True,  # 回傳每個詞的時間戳
                temperature=0.2         # 模型隨機性（0 為最穩定）
            )

            # 將 Whisper 結果轉為 VTT 字幕格式
            vtt_output = self.format_as_vtt(transcript_result)
            return vtt_output

        except Exception as error:
            st.error(f"⚠️ 音檔轉錄失敗: {error}")
            return ""

        finally:
            # 刪除暫存檔案，釋放磁碟空間
            os.remove(temp_audio_path)
            if wav_audio_path and os.path.exists(wav_audio_path):
                os.remove(wav_audio_path)

    @staticmethod
    def convert_audio_to_wav(input_path, file_extension):
        """
        將輸入音檔轉換為 Whisper 支援的 16kHz 單聲道 WAV 格式

        參數:
        - input_path: 原始音檔路徑
        - file_extension: 音檔副檔名（用於命名）

        回傳:
        - 轉換後的 WAV 檔案路徑，失敗則回傳 None
        """
        output_path = input_path.rsplit(".", 1)[0] + ".wav"  # 轉換後的檔名

        try:
            # 使用 ffmpeg 進行格式轉換
            cmd = ["ffmpeg", "-y", "-i", input_path, "-ar", "16000", "-ac", "1", output_path]
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

            return output_path if os.path.exists(output_path) else None
        except Exception as error:
            st.error(f"⚠️ 音檔轉換失敗: {error}")
            return None

    @staticmethod
    def format_as_vtt(transcript_result):
        """
        將 Whisper 的轉錄結果格式化為 VTT 字幕格式

        參數:
        - transcript_result: Whisper 回傳的轉錄字典，內含 segments（每段內容）

        回傳:
        - 字串形式的 VTT 字幕內容（含時間與文字）
        """
        vtt_output = ["WEBVTT\n"]  # 開頭加上 VTT 標記

        for segment in transcript_result["segments"]:
            start_time = segment["start"]
            end_time = segment["end"]

            # 避免出現 end < start 的錯誤，強制最小長度 0.5 秒
            if start_time >= end_time:
                end_time = start_time + 0.5

            text = segment["text"].strip()  # 去除多餘空白
            start_vtt_time = AudioTranscriber.format_timestamp(start_time)
            end_vtt_time = AudioTranscriber.format_timestamp(end_time)

            # 加入時間戳與內容（每段結尾要換行）
            vtt_output.append(f"{start_vtt_time} --> {end_vtt_time}")
            vtt_output.append(f"{text}\n")

        return "\n".join(vtt_output)

    @staticmethod
    def format_timestamp(seconds):
        """
        將秒數轉換為 VTT 格式時間（00:00:00）

        參數:
        - seconds: 時間（以秒為單位）

        回傳:
        - 時間字串，格式為 HH:MM:SS
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02}:{minutes:02}:{secs:02}"
