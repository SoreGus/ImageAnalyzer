from __future__ import annotations

import hashlib

PALETTE = (
    "#E53935",
    "#1E88E5",
    "#43A047",
    "#FB8C00",
    "#8E24AA",
    "#00ACC1",
    "#6D4C41",
    "#3949AB",
    "#7CB342",
    "#F4511E",
    "#00897B",
    "#C0CA33",
)


def color_for(label: str, index: int = 0) -> str:
    """Return a stable high-contrast color for an element label."""
    digest = hashlib.sha256(f"{label}:{index}".encode("utf-8")).digest()
    return PALETTE[int.from_bytes(digest[:2], "big") % len(PALETTE)]
