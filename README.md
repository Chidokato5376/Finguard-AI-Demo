# FinGuard AI — Dashboard Demo

> **Bản demo công khai của nền tảng Quản trị Rủi ro Giao dịch FinGuard AI**

[![Streamlit](https://img.shields.io/badge/Streamlit-Live%20Demo-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://finguard-ai-demo-cfjsgsbg3qxf4zkv7j2xde.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](Finguard-Demo/README.md)

**🔗 Live Demo:** [finguard-ai-demo.streamlit.app](https://finguard-ai-demo-cfjsgsbg3qxf4zkv7j2xde.streamlit.app/)
**📦 Repository chính (mã nguồn đầy đủ):** [FinGuard-AI-Platform](https://github.com/Chidokato5376/FinGuard-AI-Platform)

> Submission — **AI-Quantum Challenge 2026**
> Tác giả: Phạm Tiến Dũng — Khoa Toán Kinh tế, Đại học Kinh tế Quốc dân (NEU)

---

## Nội dung repository

| Đường dẫn | Mô tả |
|---|---|
| [**`Finguard-Demo/`**](Finguard-Demo/) | **Toàn bộ mã nguồn và dữ liệu của bản demo** — xem [README chi tiết](Finguard-Demo/README.md) |
| `requirements.txt` | Dependencies (đặt ở gốc theo yêu cầu của Streamlit Community Cloud) |
| `.streamlit/config.toml` | Theme giao diện (đặt ở gốc theo yêu cầu của Streamlit Cloud) |

## Dashboard có gì

Bốn khối mô phỏng quy trình làm việc của một chuyên viên quản trị rủi ro:

1. **Hàng đợi cảnh báo ưu tiên** — chấm điểm rủi ro liên tục 0–100, phân tier Low / Medium / Critical
2. **Giải thích quyết định** — chỉ rõ yếu tố nào đẩy điểm rủi ro lên cao, kèm công thức minh bạch
3. **Sơ đồ mạng lưới tài khoản** — phát hiện Money Mule / Fraud Ring qua cấu trúc quan hệ
4. **Phân bổ ca trực (QAPE)** — chọn tập cảnh báo xử lý dưới ràng buộc ngân sách nguồn lực

## Chạy nhanh trên máy

```bash
git clone https://github.com/Chidokato5376/Finguard-AI-Demo.git
```
```bash
cd Finguard-AI-Demo
```
```bash
pip install -r requirements.txt
```
```bash
streamlit run Finguard-Demo/src/dashboard/app.py
```

Dữ liệu mô phỏng đã được commit kèm nên dashboard hiển thị ngay, không cần bước tiền xử lý.

> ⚠️ **Dữ liệu trong demo là dữ liệu mô phỏng**, không phải giao dịch ngân hàng thật và không chứa dữ liệu khách hàng. Chi tiết về nguồn gốc, cách hiệu chỉnh và các giả định: xem [`Finguard-Demo/README.md`](Finguard-Demo/README.md).

---

*Đại học Kinh tế Quốc dân, Hà Nội*
