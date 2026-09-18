"""
Chuyển văn bản tiếng Việt thành giọng nói bằng edge-tts
(dùng giọng đọc neural miễn phí của Microsoft Edge).

Danh sách giọng tiếng Việt có sẵn:
    vi-VN-HoaiMyNeural   (nữ)
    vi-VN-NamMinhNeural  (nam)
"""
import asyncio
from pathlib import Path

import edge_tts

from config import CFG


async def _synthesize_async(text: str, out_path: Path) -> None:
    communicate = edge_tts.Communicate(text, voice=CFG.tts_voice, rate=CFG.tts_rate)
    await communicate.save(str(out_path))


def synthesize(text: str, out_path: Path) -> None:
    """Tạo file .mp3 từ text. Hàm đồng bộ, gọi trực tiếp trong pipeline."""
    if not text.strip():
        raise ValueError("Text rỗng, không thể tạo giọng đọc.")
    asyncio.run(_synthesize_async(text, out_path))
