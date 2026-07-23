"""Pipeline suy luận cho Dashboard — nối DRRE (Module 3′) + Risk Scoring
(Module 5) + Explainability (Module 6) thành một luồng forward pass duy
nhất, chạy trên dữ liệu đã tiền xử lý trong data/processed/.

=== ⚠ CHẾ ĐỘ DEMO — ĐỌC TRƯỚC KHI DIỄN GIẢI KẾT QUẢ ===

Nếu không tìm thấy checkpoint đã huấn luyện tại models/drre_checkpoint.pt,
pipeline sẽ khởi tạo DRRE với TRỌNG SỐ NGẪU NHIÊN (chưa huấn luyện) chỉ để
minh họa luồng dữ liệu kiến trúc chạy được đầu-cuối. Trong trường hợp này:

  - risk_score KHÔNG phản ánh rủi ro thực — chỉ là output của một mạng
    chưa học gì.
  - alpha_k, beta, delta_t vẫn có cấu trúc toán học đúng (softmax hợp lệ,
    tổng = 1) nhưng KHÔNG mang ý nghĩa "khớp lịch sử hành vi" thật.

Việc huấn luyện DRRE thật là công việc của Tuần 1-2 trong roadmap
(README.md §7) — không nằm trong phạm vi hoàn thiện Dashboard. Dashboard
này được thiết kế để CHẠY ĐƯỢC NGAY với model chưa train, và tự động
chuyển sang dùng checkpoint thật ngay khi bạn huấn luyện xong và lưu vào
models/drre_checkpoint.pt (xem save_checkpoint() bên dưới).
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Cột đặc trưng dùng làm x_t / node_features — PHẢI khớp giữa toàn bộ
# pipeline (input_dim của DRRE được suy ra từ độ dài danh sách này).
# Mở rộng danh sách này khi Behavior Analytics (Module 2) cung cấp thêm
# đặc trưng — nhớ huấn luyện lại từ đầu vì input_dim sẽ thay đổi.
FEATURE_COLUMNS = ["amount_norm", "channel_encoded"]

DEFAULT_CHECKPOINT_PATH = "models/drre_checkpoint.pt"


class DashboardInferenceEngine:
    """Bọc DRRE + RiskScoringEngine thành một pipeline suy luận (forward-only)
    cho Dashboard. KHÔNG phải training loop — chỉ dùng để hiển thị.
    """

    def __init__(
        self,
        hidden_dim: int = 64,
        num_slots: int = 4,
        graph_hidden_dim: int = 64,
        embedding_dim: int = 128,
        checkpoint_path: str | Path = DEFAULT_CHECKPOINT_PATH,
    ) -> None:
        try:
            import torch
        except ImportError as e:
            raise ImportError(
                "torch chưa được cài. Chạy: pip install torch torch-geometric"
            ) from e
        self._torch = torch

        from src.drre.model import DRRE
        from src.scoring.risk_scoring import RiskScoringEngine

        self.input_dim = len(FEATURE_COLUMNS)
        self.drre = DRRE(
            input_dim=self.input_dim,
            hidden_dim=hidden_dim,
            num_slots=num_slots,
            graph_hidden_dim=graph_hidden_dim,
            graph_num_layers=2,
            embedding_dim=embedding_dim,
        )
        self.risk_engine = RiskScoringEngine(embedding_dim=embedding_dim)

        self.is_trained = False
        checkpoint_path = Path(checkpoint_path)
        if checkpoint_path.exists():
            state = torch.load(checkpoint_path, map_location="cpu")
            self.drre.load_state_dict(state["drre"])
            self.risk_engine.load_state_dict(state["risk_engine"])
            self.is_trained = True
            logger.info("Đã tải checkpoint đã huấn luyện: %s", checkpoint_path)
        else:
            logger.warning(
                "Không tìm thấy checkpoint tại %s — dùng trọng số NGẪU NHIÊN "
                "(CHẾ ĐỘ DEMO, xem cảnh báo đầu module).", checkpoint_path,
            )

        self.drre.eval()
        self.risk_engine.eval()

    def score_batch(self, df: pd.DataFrame, max_rows: int = 500) -> pd.DataFrame:
        """Chạy forward pass DRRE + Risk Scoring cho một batch giao dịch.

        Args:
            df: DataFrame đã tiền xử lý (từ src/data/preprocessing.py),
                cần có account_id, counterparty_id + các cột FEATURE_COLUMNS.
            max_rows: giới hạn kích thước batch cho Dashboard — dựng đồ thị
                O(n) node/edge, không nên đẩy nguyên tập triệu dòng vào đây.
                Dùng cửa sổ theo thời gian (vd. 15 phút gần nhất) khi tích
                hợp dữ liệu streaming thật.

        Returns:
            df gốc (đã cắt max_rows) + cột risk_score, tier, delta_t,
            max_attention_weight, beta_transaction/beta_behavior/beta_graph.
        """
        from src.dashboard.graph_utils import build_account_graph
        from src.scoring.risk_scoring import classify_tier

        torch = self._torch
        missing = set(FEATURE_COLUMNS) - set(df.columns)
        if missing:
            raise ValueError(
                f"DataFrame thiếu cột đặc trưng: {missing}. "
                f"Chạy src/data/preprocessing.py trước (sinh amount_norm/channel_encoded)."
            )

        if len(df) > max_rows:
            logger.info("Batch %d dòng > max_rows=%d, lấy %d dòng gần nhất.",
                        len(df), max_rows, max_rows)
            df = df.sort_values("step") if "step" in df.columns else df
            df = df.tail(max_rows).reset_index(drop=True)
        else:
            df = df.reset_index(drop=True)

        node_features, edge_index, account_to_idx = build_account_graph(df, FEATURE_COLUMNS)

        x_t = torch.tensor(df[FEATURE_COLUMNS].to_numpy(dtype=np.float32))
        batch_size = len(df)

        # Cold-start tuyệt đối cho mỗi lần load Dashboard (chưa có Behavior
        # Memory tích lũy liên phiên). Hệ thống sản xuất thật cần lưu/khôi
        # phục (h_prev, m_prev) theo account_id giữa các batch — ngoài
        # phạm vi Dashboard scaffold này (ghi rõ để không hiểu nhầm là bug).
        h_prev, m_prev = self.drre.behavior_memory.init_state(batch_size, device=x_t.device)
        node_index = torch.tensor(
            [account_to_idx[a] for a in df["account_id"]], dtype=torch.long
        )

        with torch.no_grad():
            out = self.drre(x_t, h_prev, m_prev, node_features, edge_index, node_index)
            scores = self.risk_engine(out["e_t"])

        result = df.copy()
        result["risk_score"] = scores.numpy()
        result["tier"] = result["risk_score"].apply(lambda s: classify_tier(s).value)
        result["max_attention_weight"] = out["alpha_k"].max(dim=-1).values.numpy()
        beta = out["beta"].numpy()
        result["beta_transaction"] = beta[:, 0]
        result["beta_behavior"] = beta[:, 1]
        result["beta_graph"] = beta[:, 2]
        result["delta_t"] = out["delta_t"].numpy()
        # Giữ lại alpha_k đầy đủ (không chỉ max) để panel giải thích dùng lại
        result.attrs["alpha_k_full"] = out["alpha_k"].numpy()
        return result

    def save_checkpoint(self, path: str | Path = DEFAULT_CHECKPOINT_PATH) -> None:
        """Lưu checkpoint sau khi huấn luyện — gọi từ training loop
        (src/drre/model.py::main(), khi đã implement), KHÔNG gọi từ Dashboard.
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self._torch.save(
            {"drre": self.drre.state_dict(), "risk_engine": self.risk_engine.state_dict()},
            path,
        )
        logger.info("Đã lưu checkpoint: %s", path)


def load_latest_processed_data(processed_dir: str | Path = "data/processed") -> dict[str, Path]:
    """Liệt kê các file *_test.parquet có sẵn trong data/processed/ để
    Dashboard cho người dùng chọn nguồn dữ liệu.

    Dùng *_test.parquet (không phải train) vì Dashboard mô phỏng giám sát
    giao dịch MỚI — dùng tập train sẽ là dữ liệu model "đã thấy" trong
    huấn luyện (một khi có huấn luyện thật), gây hiểu lầm về hiệu năng.
    """
    processed_dir = Path(processed_dir)
    if not processed_dir.exists():
        return {}
    return {
        f.stem.replace("_test", ""): f
        for f in processed_dir.glob("*_test.parquet")
    }
