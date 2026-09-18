from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple


@dataclass
class Config:
    # ==========================================
    # ĐẦU VÀO
    # ==========================================
    images_dir: Path = Path("assets")              # nơi để ảnh topic + comment
    topic_filename: str = "topic.png"               # tên file ảnh chủ đề
    comment_prefix: str = "comment_"                 # comment_1.png, comment_2.png, ...
    image_extensions: tuple = (".png", ".jpg", ".jpeg", ".webp")

    backgrounds_dir: Path = Path("backgrounds")      # thư mục chứa video parkour nền

    # ==========================================
    # OCR (đọc chữ trong ảnh chụp màn hình)
    # ==========================================
    ocr_lang: str = "vie"                            # gói ngôn ngữ tesseract (cần cài: tesseract-ocr-vie)

    # ==========================================
    # TTS (đọc thành giọng nói tiếng Việt qua edge-tts)
    # ==========================================
    # Giọng nữ: vi-VN-HoaiMyNeural | Giọng nam: vi-VN-NamMinhNeural
    tts_voice: str = "vi-VN-HoaiMyNeural"
    tts_rate: str = "+0%"                            # vd "+15%" để đọc nhanh hơn

    # ==========================================
    # VIDEO OUTPUT
    # ==========================================
    output_dir: Path = Path("output")
    output_filename: str = "final_video.mp4"
    resolution: Tuple[int, int] = (1080, 1920)       # dọc, chuẩn Shorts/Reels
    fps: int = 30

    # Khoảng lặng ngắn giữa các đoạn (topic -> comment 1 -> comment 2 ...)
    gap_between_segments: float = 0.35

    # Ảnh overlay chiếm bao nhiêu % chiều rộng khung hình
    image_max_width_ratio: float = 0.85

    # Nếu tất cả video nền đều ngắn hơn tổng thời lượng thoại, sẽ lặp video nền
    # (không có "cắt cứng 60s" — nếu thoại dài hơn, nền sẽ được nối dài tương ứng)


CFG = Config()
