# Threads Video Builder

Pipeline: ảnh chụp màn hình (topic + comment) → OCR → TTS tiếng Việt → ghép với video nền parkour → xuất video dọc (1080x1920).

## 1. Cài đặt hệ thống (bắt buộc trước khi pip install)

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg tesseract-ocr tesseract-ocr-vie

# macOS (brew)
brew install ffmpeg tesseract tesseract-lang
```

## 2. Cài thư viện Python

```bash
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Chuẩn bị dữ liệu

```
threads_video_builder/
├── assets/
│   ├── topic.png          # ảnh chủ đề (screenshot bài gốc)
│   ├── comment_1.png       # top comment 1
│   ├── comment_2.png       # top comment 2
│   └── ...                 # tới comment_5.png / comment_6.png
└── backgrounds/
    ├── parkour_01.mp4
    ├── parkour_02.mp4
    └── ...
```

Tên file comment chỉ cần chứa số thứ tự (ví dụ `comment_1.png`, `comment_2.jpg`...), hệ thống tự sort đúng thứ tự.

## 4. Chỉnh cấu hình (tùy chọn)

Mở `config.py` để đổi:
- Giọng đọc: `tts_voice = "vi-VN-HoaiMyNeural"` (nữ) hoặc `"vi-VN-NamMinhNeural"` (nam)
- Tốc độ đọc: `tts_rate = "+15%"` để đọc nhanh hơn
- Độ phân giải, khoảng lặng giữa các đoạn, tỉ lệ ảnh overlay...

## 5. Chạy

```bash
python main.py
```

Video xuất ra tại `output/final_video.mp4`.

## Cách hoạt động

1. OCR đọc chữ trong từng ảnh (topic trước, rồi lần lượt từng comment).
2. Mỗi đoạn text được chuyển thành 1 file audio riêng bằng edge-tts.
3. Tổng thời lượng video = tổng thời lượng tất cả đoạn audio (+ khoảng lặng nhỏ giữa các đoạn).
4. Hệ thống chọn ngẫu nhiên 1 video trong `backgrounds/`, cắt 1 đoạn ngẫu nhiên đúng bằng
   tổng thời lượng đó (nếu không video nào đủ dài, sẽ tự lặp lại cho đủ).
5. Video nền được resize/crop cho vừa khung dọc, sau đó từng ảnh được overlay lên đúng
   thời điểm audio tương ứng bắt đầu phát.
6. Ghép tất cả bằng moviepy, xuất file .mp4 cuối cùng.

## Lưu ý

- OCR có thể đọc sai vài chữ nếu ảnh chụp bị mờ/độ tương phản thấp — nên kiểm tra
  console log (in ra text đã đọc được cho từng đoạn) trước khi để chạy hàng loạt.
- edge-tts cần kết nối internet (gọi dịch vụ giọng đọc của Microsoft Edge, miễn phí,
  không cần API key).
- Nếu muốn tự động hoá thành hàng loạt video (nhiều bộ topic+comment), có thể viết thêm
  một vòng lặp gọi `run_pipeline()` cho từng thư mục con trong `assets/`.
