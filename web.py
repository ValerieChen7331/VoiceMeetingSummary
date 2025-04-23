import React, { useState, useRef, useEffect } from "react";

const transcript = [
  { start: 2.68, end: 9.279, speaker: "說話人 1", text: "差勤的角度,你要教人力,要先講。" },
  { start: 11.5, end: 17.0, speaker: "說話人 1", text: "以我,對於這個我自己來差勤,一定會," },
  { start: 17.0, end: 24.96, speaker: "說話人 1", text: "你說,差勤要被復速了。多選這樣的差勤。" },
  { start: 30.759, end: 36.74, speaker: "說話人 1", text: "我現在要看產品斷線,安娜學士在研究開發階段," },
  { start: 37.06, end: 39.859, speaker: "說話人 1", text: "我查,我希望可以考慮我,先簡單。" },
];

export default function TranscriptPlayer() {
  const audioRef = useRef(null);
  const [currentTime, setCurrentTime] = useState(0);

  // 更新當前播放時間
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const updateTime = () => setCurrentTime(audio.currentTime);
    audio.addEventListener("timeupdate", updateTime);

    return () => {
      audio.removeEventListener("timeupdate", updateTime);
    };
  }, []);

  // 點擊逐字稿跳轉音訊
  const jumpToTime = (time) => {
    if (audioRef.current) {
      audioRef.current.currentTime = time;
      audioRef.current.play();
    }
  };

  // 音訊快進/倒退 10 秒
  const adjustTime = (offset) => {
    if (audioRef.current) {
      audioRef.current.currentTime += offset;
    }
  };

  return (
    <div className="p-4 max-w-2xl mx-auto">
      {/* 音訊播放器 */}
      <audio ref={audioRef} controls className="w-full mt-4">
        <source src="/audio/sample.mp3" type="audio/mp3" />
        Your browser does not support the audio element.
      </audio>

      {/* 控制按鈕 */}
      <div className="flex justify-center space-x-4 mt-4">
        <button className="px-4 py-2 bg-gray-200 rounded" onClick={() => adjustTime(-10)}>
          ⏪ -10s
        </button>
        <button className="px-4 py-2 bg-gray-200 rounded" onClick={() => adjustTime(10)}>
          ⏩ +10s
        </button>
      </div>

      {/* 逐字稿顯示 */}
      <div className="mt-6 space-y-2">
        {transcript.map((entry, index) => (
          <p
            key={index}
            className={`p-2 rounded cursor-pointer ${
              currentTime >= entry.start && currentTime <= entry.end
                ? "bg-yellow-200 font-bold"
                : "hover:bg-gray-100"
            }`}
            onClick={() => jumpToTime(entry.start)}
          >
            <span className="font-semibold text-blue-600">{entry.speaker}</span> {" "}
            <span className="text-gray-500">[{formatTime(entry.start)}]</span>: {" "}
            {entry.text}
          </p>
        ))}
      </div>
    </div>
  );
}

// 時間格式轉換 (秒 → MM:SS)
function formatTime(seconds) {
  const minutes = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${String(minutes).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
}
