import whisper
import os
import subprocess
import tempfile
import numpy as np
from scipy.spatial.distance import cdist
from paddlespeech.cli.vector import VectorExecutor
import streamlit as st


class AudioTranscriber:
    """音檔轉錄與聲紋辨識系統，支援 mp3、wav、mp4、m4a"""

    _whisper_model = None  # Whisper 語音轉錄模型（避免重複載入）
    _vector_executor = None  # PaddleSpeech 聲紋辨識模型（避免重複載入）

    def __init__(self):
        """初始化 Whisper 與 PaddleSpeech"""
        if AudioTranscriber._whisper_model is None:
            AudioTranscriber._whisper_model = whisper.load_model("base")  # 載入 Whisper 模型
        if AudioTranscriber._vector_executor is None:
            AudioTranscriber._vector_executor = VectorExecutor()  # 載入 PaddleSpeech 模型

    def transcribe(self, uploaded_audio):
        """
        轉錄音檔，並自動識別不同語者，輸出 VTT 格式逐字稿

        參數:
        - uploaded_audio (UploadedFile): 使用者上傳的音檔

        回傳:
        - str: 包含時間戳記、語者標籤和文字的 VTT 格式內容
        """
        if uploaded_audio.size == 0:
            st.error("⚠️ 音檔為空，請重新上傳。")
            return ""

        file_extension = os.path.splitext(uploaded_audio.name)[-1].lower()

        # 儲存上傳的音檔到暫存檔案
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_audio:
            temp_audio.write(uploaded_audio.getbuffer())
            temp_audio_path = temp_audio.name

        wav_audio_path = None
        try:
            # **步驟 1：將音檔轉換為 16kHz WAV**
            wav_audio_path = self.convert_audio_to_wav(temp_audio_path, file_extension)
            if not wav_audio_path:
                st.error("⚠️ 音檔轉換失敗，請上傳有效音檔。")
                return ""

            # **步驟 2：Whisper 進行語音轉文字**
            transcript_result = self._whisper_model.transcribe(wav_audio_path,
                                                               language="zh",
                                                               word_timestamps=True,
                                                               temperature=0.2)

            # # **步驟 2.5：合併短片段**
            # merged_segments = self.merge_short_segments(transcript_result["segments"])
            # # **步驟 3：使用 PaddleSpeech 進行聲紋辨識**
            # speaker_labels = self.assign_speaker_labels(wav_audio_path, merged_segments)

            # **步驟 3：使用 PaddleSpeech 進行聲紋辨識**
            speaker_labels = self.assign_speaker_labels(wav_audio_path, transcript_result["segments"])

            # **步驟 4：將結果格式化為 VTT**
            vtt_output = self.format_as_vtt(transcript_result, speaker_labels)
            return vtt_output

        except Exception as error:
            st.error(f"⚠️ 音檔轉錄失敗: {error}")
            return ""

        finally:
            # **清理暫存檔案**
            os.remove(temp_audio_path)
            if wav_audio_path and os.path.exists(wav_audio_path):
                os.remove(wav_audio_path)

    def merge_short_segments(self, segments, min_duration=1.5, max_gap=1.0):
        """
        合併較短的片段，避免過多切割導致語者辨識錯誤。

        參數：
        - segments (list): Whisper 轉錄的語音片段
        - min_duration (float): 最小片段長度（秒）
        - max_gap (float): 允許的最大間隔時間（秒），若小於此值則合併

        回傳：
        - list: 合併後的片段
        """
        merged_segments = []
        current_segment = None

        for segment in segments:
            start, end = segment["start"], segment["end"]
            text = segment["text"]

            # 初始化當前片段
            if current_segment is None:
                current_segment = {"start": start, "end": end, "text": text}
                continue

            # 計算當前片段與新片段的間隔時間
            gap = start - current_segment["end"]
            segment_duration = end - start

            # **合併條件**：
            # 1. 間隔小於 max_gap
            # 2. 片段過短（小於 min_duration）
            if gap < max_gap or (current_segment["end"] - current_segment["start"] < min_duration):
                current_segment["end"] = end
                current_segment["text"] += " " + text  # 合併文字
            else:
                merged_segments.append(current_segment)
                current_segment = {"start": start, "end": end, "text": text}

        # **加上最後一個片段**
        if current_segment:
            merged_segments.append(current_segment)

        return merged_segments

    @staticmethod
    def convert_audio_to_wav(input_path, file_extension):
        """將音檔轉換為 16kHz 單聲道 WAV 格式"""
        output_path = input_path.rsplit(".", 1)[0] + ".wav"

        try:
            cmd = ["ffmpeg", "-y", "-i", input_path, "-ar", "16000", "-ac", "1", output_path]
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return output_path if os.path.exists(output_path) else None
        except Exception as error:
            st.error(f"⚠️ 音檔轉換失敗: {error}")
            return None


    def assign_speaker_labels(self, audio_path, segments):
        """
        **自動為音檔片段分配語者標籤**
        - 透過 PaddleSpeech 取得每個片段的 **聲紋特徵 (Speaker Embedding)**
        - 計算與現有語者的 **餘弦距離 (Cosine Distance)** 來辨識是否為同一人
        - 若為新語者，則分配新的標籤 (例如：「語者 1」、「語者 2」)
        參數：
        - audio_path (str): 音檔的路徑
        - segments (list): 每個片段的時間區間
        回傳：
        - list: 每個片段對應的語者標籤 (["語者 1", "語者 2", ...])
        """
        speaker_embeddings = []  # 儲存每位語者的聲紋特徵
        speaker_labels = []  # 每個片段對應的語者標籤
        speaker_count = 0  # 語者計數器 (從 1 開始)

        for segment in segments:
            start_time = segment["start"]  # 片段起始時間 (秒)
            end_time = segment["end"]  # 片段結束時間 (秒)
            if start_time >= end_time:  # 避免無效時間戳
                end_time = start_time + 0.5  # 增加 0.5 秒

            # **建立臨時檔案來存放擷取的音訊片段**
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_segment:
                temp_segment_path = temp_segment.name.replace("\\", "/")  # 取得臨時檔案的路徑

            # **使用 FFmpeg 擷取音檔中的片段**
            cmd = [
                "ffmpeg", "-y", "-i", audio_path, "-ss", str(start_time), "-to", str(end_time),
                "-ar", "16000", "-ac", "1", temp_segment_path  # 轉換為 16kHz 單聲道
            ]
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

            try:
                # **取得當前片段的聲紋特徵 (Embedding)**
                embedding = self._vector_executor(audio_file=temp_segment_path)

                # **比對是否為已知語者**
                if len(speaker_embeddings) == 0:
                    speaker_count += 1  # 第一位語者
                    speaker_labels.append(f"語者 {speaker_count}")  # 標記為「語者 1」
                    speaker_embeddings.append(embedding)  # 儲存這位語者的聲紋特徵
                else:
                    # **計算與已知語者的相似度 (Cosine Distance)**
                    distances = cdist([embedding], speaker_embeddings, metric='cosine')[0]
                    min_distance = np.min(distances)  # 取得最小距離 (最接近的語者)

                    # **如果距離小於 0.6，視為同一個語者**
                    if min_distance < 0.9:  # 0.6 為相似度閾值，可根據實際需求調整
                        speaker_index = np.argmin(distances)  # 找出最相近的語者索引
                        speaker_labels.append(f"語者 {speaker_index + 1}")  # 分配現有語者標籤
                    else:
                        # **如果是新語者，則分配新標籤**
                        speaker_count += 1
                        speaker_labels.append(f"語者 {speaker_count}")
                        speaker_embeddings.append(embedding)  # 存入新語者的聲紋特徵
                        # st.write(speaker_labels[-1])

            except Exception as error:
                st.error(f"⚠️ 聲紋辨識失敗: {error}")  # 如果辨識失敗，顯示錯誤訊息
                speaker_labels.append("未知語者")  # 若發生錯誤，標記為「未知語者」

            # **清除臨時音檔**
            os.remove(temp_segment_path)

        return speaker_labels  # 回傳所有片段的語者標籤

    @staticmethod
    def format_as_vtt(transcript_result, speaker_labels):
        """
        **將 Whisper 轉錄結果格式化為 VTT（含語者資訊）**

        - **時間戳記**
        - **語者標籤**
        - **逐字稿內容**

        回傳:
        - str: VTT 格式內容
        """
        vtt_output = ["WEBVTT\n"]  # VTT 文件開頭

        for i, segment in enumerate(transcript_result["segments"]):
            start_time = segment["start"]
            end_time = segment["end"]

            if start_time >= end_time:  # 避免無效時間戳
                end_time = start_time + 0.5  # 增加 0.5 秒

            text = segment["text"].strip()  # 確保文字沒有前後空格
            speaker = speaker_labels[i]

            start_vtt_time = AudioTranscriber.format_timestamp(start_time)
            end_vtt_time = AudioTranscriber.format_timestamp(end_time)

            # **加入時間戳記 + 語者資訊 + 內容**
            vtt_output.append(f"{start_vtt_time} --> {end_vtt_time}")
            vtt_output.append(f"{speaker}: {text}\n")  # 確保每個片段後面都有換行

        return "\n".join(vtt_output)

    @staticmethod
    def format_timestamp(seconds):
        """將秒數轉換為 VTT 格式 (00:00:01)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        return f"{hours:02}:{minutes:02}:{secs:02}"
