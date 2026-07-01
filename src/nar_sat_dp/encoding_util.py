"""輸入編碼偵測。"""

from __future__ import annotations


def decode_bytes(data: bytes, encodings: list[str]) -> tuple[str, str]:
    """依序嘗試編碼，回傳 (文字, 使用的編碼名稱)。"""
    last_error: Exception | None = None
    for encoding in encodings:
        try:
            return data.decode(encoding), encoding
        except (UnicodeDecodeError, LookupError) as exc:
            last_error = exc
    raise UnicodeDecodeError(
        "unknown",
        data,
        0,
        min(len(data), 1),
        f"無法以 {encodings!r} 解碼: {last_error}",
    )
