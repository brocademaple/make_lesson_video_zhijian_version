"""16:9 课程向视觉常量（深蓝 / 洋葱紫 / 警示红）。"""

from pptx.dml.color import RGBColor
from pptx.util import Inches

# 默认宽幅 16:9（python-pptx 默认）
SLIDE_WIDTH = Inches(13.333)
SLIDE_HEIGHT = Inches(7.5)

MARGIN = Inches(0.45)

FONT_CN = "Microsoft YaHei"
FONT_FALLBACK = "PingFang SC"

COLORS = {
    "primary": RGBColor(0x2E, 0x3A, 0x8E),  # 深蓝
    "accent_purple": RGBColor(0x6B, 0x4F, 0x9E),  # 洋葱紫
    "alert_red": RGBColor(0xC9, 0x2A, 0x2A),  # 警示红
    "text": RGBColor(0x22, 0x22, 0x22),
    "muted": RGBColor(0x66, 0x66, 0x66),
    "card_bg": RGBColor(0xF5, 0xF7, 0xFB),
    "white": RGBColor(0xFF, 0xFF, 0xFF),
}
