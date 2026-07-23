# FinGuard AI — Dashboard Demo (public)

Bản demo công khai của **FinGuard AI** — nền tảng quản trị rủi ro giao dịch
dựa trên Biểu diễn Rủi ro Động (DRRE), Explainable AI và tối ưu hóa lượng tử.

Đây là **bản chụp gọn để deploy** (chạy ở chế độ *Heuristic Scorer* — không cần
GPU/torch/qiskit), kèm sẵn dữ liệu mô phỏng `synthetic_vn` để dashboard hiển thị
ngay. Mã nguồn đầy đủ (DRRE, QAPE/QAOA, training) nằm ở repository chính.

## Chạy cục bộ

```bash
pip install -r requirements.txt
streamlit run src/dashboard/app.py
```

## Về dữ liệu

Dashboard demo dùng dữ liệu **tổng hợp** (`synthetic_vn`), hiệu chỉnh theo thống kê
công khai của NHNN/Napas — **không phải dữ liệu khách hàng thật**. Điểm rủi ro do
Heuristic Scorer (z-score biên độ giao dịch theo lịch sử từng tài khoản) tính,
minh bạch, không phải hộp đen. Chi tiết: `src/dashboard/scoring_service.py`.

## Triển khai (Streamlit Community Cloud)

- Main file path: `src/dashboard/app.py`
- Python: 3.10+
- Dependencies: `requirements.txt` (bản gọn)
