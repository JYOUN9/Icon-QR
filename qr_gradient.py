import qrcode
from pathlib import Path

from PIL import Image
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import VerticalGradiantColorMask
from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer, SquareModuleDrawer

# URL to encode
data = "https://jyoun9.github.io/"

# PNG icon path
icon_path = Path("icon.png")


def hex_to_rgb(hex_code: str) -> tuple[int, int, int]:
    hex_code = hex_code.strip().lstrip("#")
    if len(hex_code) != 6:
        raise ValueError(f"Invalid hex color: {hex_code!r}. Use format RRGGBB.")
    return tuple(int(hex_code[i : i + 2], 16) for i in (0, 2, 4))


# CVPR-like 2-color gradient (blue -> olive) using hex codes
top_hex_color = "#185A99"
bottom_hex_color = "#92A73F"
top_color = hex_to_rgb(top_hex_color)
bottom_color = hex_to_rgb(bottom_hex_color)
icon_padding_ratio = 0.03


def load_icon_as_rgba(path: Path) -> Image.Image:
    """Load PNG/JPG icon to RGBA."""
    return Image.open(path).convert("RGBA")


def add_icon_margin(
    icon_rgba: Image.Image,
    padding_ratio: float = 0.12,
    margin_color: tuple[int, int, int, int] = (255, 255, 255, 255),
) -> Image.Image:
    """Center icon on a square background with a small outer margin."""
    w, h = icon_rgba.size
    base = max(w, h)
    pad = max(1, int(base * padding_ratio))
    out_size = base + (pad * 2)
    out = Image.new("RGBA", (out_size, out_size), margin_color)
    x = (out_size - w) // 2
    y = (out_size - h) // 2
    out.alpha_composite(icon_rgba, (x, y))
    return out


# QR base settings
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=10,
    border=4,
)
qr.add_data(data)
qr.make(fit=True)

# Basic QR (black/white)
img_basic = qr.make_image(fill_color="black", back_color="white")
img_basic.save("permanent_qr_basic.png")
print("Saved: permanent_qr_basic.png")

gradient_mask = VerticalGradiantColorMask(
    back_color=(255, 255, 255),
    top_color=top_color,
    bottom_color=bottom_color,
)

# Gradient QR with square modules + rounded eyes
img_gradient = qr.make_image(
    image_factory=StyledPilImage,
    module_drawer=SquareModuleDrawer(),
    eye_drawer=RoundedModuleDrawer(radius_ratio=0.95),
    color_mask=gradient_mask,
)
img_gradient.save("permanent_qr_gradient.png")
print("Saved: permanent_qr_gradient.png")

# Gradient QR + centered PNG icon
if icon_path.exists():
    icon_rgba = load_icon_as_rgba(icon_path)
    icon_with_margin = add_icon_margin(icon_rgba, padding_ratio=icon_padding_ratio)

    img_gradient_with_icon = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=SquareModuleDrawer(),
        eye_drawer=RoundedModuleDrawer(radius_ratio=0.95),
        color_mask=gradient_mask,
        embedded_image=icon_with_margin,
        embedded_image_ratio=0.18,
    )
    img_gradient_with_icon.save("permanent_qr_gradient_icon.png")
    print("Saved: permanent_qr_gradient_icon.png (icon: icon.png)")
else:
    print("Skip icon QR: icon.png not found")
