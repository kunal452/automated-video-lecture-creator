import re
from pathlib import Path
from typing import List, Optional
from PIL import Image, ImageDraw, ImageFont
from app.config import SLIDE_THEMES

def hex_to_rgb(hex_code: str):
    hex_code = hex_code.lstrip("#")
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

def get_font(size: int, bold: bool = False):
    font_candidates = [
        "segoeui.ttf", "arial.ttf", "calibri.ttf", "tahoma.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    ]
    if bold:
        font_candidates = ["segoeuib.ttf", "arialbd.ttf", "calibrib.ttf"] + font_candidates

    for font_name in font_candidates:
        try:
            return ImageFont.truetype(font_name, size)
        except IOError:
            continue
    return ImageFont.load_default()

def wrap_text(text: str, max_chars: int = 58) -> List[str]:
    words = text.split()
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        if current_length + len(word) + 1 <= max_chars:
            current_line.append(word)
            current_length += len(word) + 1
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
            current_length = len(word)

    if current_line:
        lines.append(" ".join(current_line))
    return lines

def render_slide_image(
    slide_title: str,
    bullet_points: List[str],
    slide_number: int,
    total_slides: int,
    output_path: Path,
    lecture_title: str = "Automated Video Lecture",
    theme_key: str = "dark_modern",
    code_snippet: Optional[str] = None
) -> Path:
    """
    Renders a crisp 1920x1080 slide image with rich visuals,
    proper typography, bullet points, and optional code snippets.
    """
    theme = SLIDE_THEMES.get(theme_key, SLIDE_THEMES["dark_modern"])
    width, height = 1920, 1080

    bg_rgb = hex_to_rgb(theme["bg_color"])
    card_rgb = hex_to_rgb(theme["card_bg"])
    accent_rgb = hex_to_rgb(theme["accent_color"])
    title_rgb = hex_to_rgb(theme["title_color"])
    text_rgb = hex_to_rgb(theme["text_color"])
    code_bg_rgb = hex_to_rgb(theme["code_bg"])
    code_text_rgb = hex_to_rgb(theme["code_text"])
    footer_rgb = hex_to_rgb(theme["footer_color"])

    img = Image.new("RGB", (width, height), color=bg_rgb)
    draw = ImageDraw.Draw(img)

    # 1. Accent Header Bar
    draw.rectangle([(0, 0), (width, 10)], fill=accent_rgb)

    # 2. Main Presentation Content Container (Glassmorphic Card Effect)
    card_padding = 80
    draw.rounded_rectangle(
        [(card_padding, 60), (width - card_padding, height - 70)],
        radius=20,
        fill=card_rgb,
        outline=accent_rgb,
        width=1
    )

    # 3. Slide Title & Category Badge
    title_font = get_font(56, bold=True)
    draw.text((card_padding + 60, 110), slide_title, font=title_font, fill=title_rgb)

    # Decorative underline
    draw.rectangle(
        [(card_padding + 60, 195), (card_padding + 280, 200)],
        fill=accent_rgb
    )

    # 4. Content Area: Bullet Points and Code
    has_code = bool(code_snippet and code_snippet.strip())
    content_width_chars = 42 if has_code else 62

    bullet_font = get_font(34, bold=False)
    y_pos = 260

    for bullet in bullet_points[:5]:
        wrapped = wrap_text(bullet, max_chars=content_width_chars)
        # Draw modern bullet dot
        draw.ellipse(
            [(card_padding + 60, y_pos + 12), (card_padding + 76, y_pos + 28)],
            fill=accent_rgb
        )
        for line_idx, line in enumerate(wrapped):
            draw.text((card_padding + 100, y_pos), line, font=bullet_font, fill=text_rgb)
            y_pos += 46
        y_pos += 24

    # 5. Code Block Container (if present)
    if has_code:
        code_box_x = width // 2 + 30
        code_box_y = 250
        code_box_w = width - card_padding - 60
        code_box_h = height - 180

        # Background box
        draw.rounded_rectangle(
            [(code_box_x, code_box_y), (code_box_w, code_box_h)],
            radius=12,
            fill=code_bg_rgb,
            outline=accent_rgb,
            width=1
        )
        # Header for code box
        draw.rectangle([(code_box_x, code_box_y), (code_box_w, code_box_y + 40)], fill=card_rgb)
        code_header_font = get_font(20, bold=True)
        draw.text((code_box_x + 20, code_box_y + 10), "Code Demonstration", font=code_header_font, fill=accent_rgb)

        code_font = get_font(22, bold=False)
        code_lines = code_snippet.strip().split("\n")[:14]
        code_y = code_box_y + 60
        for cline in code_lines:
            draw.text((code_box_x + 25, code_y), cline[:48], font=code_font, fill=code_text_rgb)
            code_y += 32

    # 6. Footer Metadata
    footer_font = get_font(22, bold=False)
    footer_label = f"{lecture_title}  |  Slide {slide_number} of {total_slides}"
    draw.text((card_padding + 60, height - 120), footer_label, font=footer_font, fill=footer_rgb)

    brand_label = "AI Automated Lecture Pipeline"
    draw.text((width - card_padding - 340, height - 120), brand_label, font=footer_font, fill=accent_rgb)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(output_path), "PNG", quality=95)
    return output_path
