from __future__ import annotations

import base64
import io
import os
import re
import sys
from pathlib import Path

from flask import Flask, render_template, request, send_file
from PIL import Image, UnidentifiedImageError
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import SolidFillColorMask, VerticalGradiantColorMask
from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer, SquareModuleDrawer

DEFAULT_DATA = ""
DEFAULT_TOP_HEX = "#185A99"
DEFAULT_BOTTOM_HEX = "#92A73F"
DEFAULT_COLOR_MODE = "solid"
ICON_PADDING_RATIO = 0.03
DEFAULT_ICON_FILENAME = "icon.png"
FALLBACK_ICON_RELATIVE_PATHS = (
    Path(DEFAULT_ICON_FILENAME),
    Path("images") / DEFAULT_ICON_FILENAME,
    Path("images") / "favicon.ico",
    Path("favicon.ico"),
)
HEX_COLOR_RE = re.compile(r"^#?[0-9a-fA-F]{6}$")


def is_frozen_bundle() -> bool:
    return bool(getattr(sys, "frozen", False))


def bundle_root_dir() -> Path:
    if is_frozen_bundle():
        return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return Path(__file__).resolve().parent


def runtime_root_dir() -> Path:
    if is_frozen_bundle():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def default_icon_candidates() -> list[Path]:
    roots = (Path.cwd(), runtime_root_dir(), bundle_root_dir())
    candidates: list[Path] = []
    seen: set[str] = set()
    for root in roots:
        for rel_path in FALLBACK_ICON_RELATIVE_PATHS:
            candidate = root / rel_path
            key = str(candidate)
            if key not in seen:
                seen.add(key)
                candidates.append(candidate)
    return candidates


def find_default_icon_path() -> Path | None:
    for candidate in default_icon_candidates():
        if candidate.exists():
            return candidate
    return None


app = Flask(__name__, template_folder=str(bundle_root_dir() / "templates"))


def normalize_hex_or_empty(value: str) -> str:
    clean = value.strip()
    if not clean:
        return ""
    if not HEX_COLOR_RE.fullmatch(clean):
        raise ValueError(f"Invalid hex color: {value!r}. Use 6-digit HEX like #185A99.")
    if not clean.startswith("#"):
        clean = f"#{clean}"
    return clean.upper()


def hex_to_rgb(hex_code: str) -> tuple[int, int, int]:
    value = hex_code.strip().lstrip("#")
    if len(value) != 6:
        raise ValueError(f"Invalid hex color: {hex_code!r}.")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def load_icon_as_rgba(file_obj) -> Image.Image:
    file_obj.stream.seek(0)
    return Image.open(file_obj.stream).convert("RGBA")


def load_icon_from_path(path: Path) -> Image.Image:
    return Image.open(path).convert("RGBA")


def add_icon_margin(
    icon_rgba: Image.Image,
    padding_ratio: float = ICON_PADDING_RATIO,
    margin_color: tuple[int, int, int, int] = (255, 255, 255, 255),
) -> Image.Image:
    w, h = icon_rgba.size
    base = max(w, h)
    pad = max(1, int(base * padding_ratio))
    out_size = base + (pad * 2)
    out = Image.new("RGBA", (out_size, out_size), margin_color)
    x = (out_size - w) // 2
    y = (out_size - h) // 2
    out.alpha_composite(icon_rgba, (x, y))
    return out


def build_color_mask(one_color: str, top_hex: str, bottom_hex: str):
    if top_hex and bottom_hex:
        return VerticalGradiantColorMask(
            back_color=(255, 255, 255),
            top_color=hex_to_rgb(top_hex),
            bottom_color=hex_to_rgb(bottom_hex),
        )

    solid_color = one_color if one_color else "#000000"
    return SolidFillColorMask(
        back_color=(255, 255, 255),
        front_color=hex_to_rgb(solid_color),
    )


def generate_qr_png_base64(
    data: str,
    one_color: str,
    top_hex: str,
    bottom_hex: str,
    icon_rgba: Image.Image | None,
) -> str:
    color_mask = build_color_mask(one_color, top_hex, bottom_hex)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    make_image_kwargs = {
        "image_factory": StyledPilImage,
        "module_drawer": SquareModuleDrawer(),
        "eye_drawer": RoundedModuleDrawer(radius_ratio=0.95),
        "color_mask": color_mask,
    }

    if icon_rgba is not None:
        icon_with_margin = add_icon_margin(icon_rgba)
        make_image_kwargs["embedded_image"] = icon_with_margin
        make_image_kwargs["embedded_image_ratio"] = 0.18

    img = qr.make_image(**make_image_kwargs)
    pil_image = img.get_image() if hasattr(img, "get_image") else img

    buffer = io.BytesIO()
    pil_image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("ascii")


@app.route("/", methods=["GET", "POST"])
def index():
    form_data = {
        "url": DEFAULT_DATA,
        "color_mode": DEFAULT_COLOR_MODE,
        "one_color": "",
        "top_hex": "",
        "bottom_hex": "",
        "use_icon": False,
    }
    qr_image_data = None
    error_message = None

    if request.method == "POST":
        form_data["url"] = request.form.get("url", "").strip()
        form_data["color_mode"] = request.form.get("color_mode", DEFAULT_COLOR_MODE).strip().lower()
        form_data["one_color"] = request.form.get("one_color", "").strip()
        form_data["top_hex"] = request.form.get("top_hex", "").strip()
        form_data["bottom_hex"] = request.form.get("bottom_hex", "").strip()
        form_data["use_icon"] = request.form.get("use_icon") == "on"
        icon_file = request.files.get("icon_file")
        icon_rgba = None

        try:
            if form_data["color_mode"] not in {"solid", "gradient"}:
                form_data["color_mode"] = DEFAULT_COLOR_MODE

            if form_data["color_mode"] == "gradient":
                top_hex = normalize_hex_or_empty(form_data["top_hex"])
                bottom_hex = normalize_hex_or_empty(form_data["bottom_hex"])
                if not top_hex or not bottom_hex:
                    raise ValueError("Gradient mode requires both top-hex and bottom-hex.")
                one_color = ""
            else:
                one_color = normalize_hex_or_empty(form_data["one_color"])
                top_hex = ""
                bottom_hex = ""

            if icon_file and icon_file.filename and not icon_file.filename.lower().endswith(".png"):
                raise ValueError("Icon file must be a PNG image. Any PNG filename is supported.")

            if form_data["use_icon"]:
                if icon_file and icon_file.filename:
                    icon_rgba = load_icon_as_rgba(icon_file)
                elif (default_icon_path := find_default_icon_path()) is not None:
                    icon_rgba = load_icon_from_path(default_icon_path)
                else:
                    searched_paths = ", ".join(str(p) for p in default_icon_candidates())
                    raise ValueError(
                        "Icon mode is enabled, but no PNG was uploaded and icon.png was not found. "
                        f"Searched: {searched_paths}"
                    )

            qr_image_data = generate_qr_png_base64(
                data=form_data["url"],
                one_color=one_color,
                top_hex=top_hex,
                bottom_hex=bottom_hex,
                icon_rgba=icon_rgba,
            )

            form_data["one_color"] = one_color
            form_data["top_hex"] = top_hex
            form_data["bottom_hex"] = bottom_hex

        except (ValueError, UnidentifiedImageError, OSError) as exc:
            error_message = str(exc)

    return render_template(
        "index.html",
        form_data=form_data,
        qr_image_data=qr_image_data,
        error_message=error_message,
    )


@app.get("/health")
def health():
    return {"status": "ok"}, 200


@app.get("/favicon.ico")
def favicon():
    candidates = [
        Path.cwd() / "images" / "favicon.ico",
        runtime_root_dir() / "images" / "favicon.ico",
        bundle_root_dir() / "images" / "favicon.ico",
        Path.cwd() / "favicon.ico",
        runtime_root_dir() / "favicon.ico",
        bundle_root_dir() / "favicon.ico",
    ]
    for candidate in candidates:
        if candidate.exists():
            response = send_file(candidate, mimetype="image/x-icon")
            response.headers["Cache-Control"] = "no-store, no-cache, max-age=0"
            return response
    return "", 404


if __name__ == "__main__":
    host = os.environ.get("ICON_QR_HOST", "127.0.0.1")
    port = int(os.environ.get("ICON_QR_PORT", os.environ.get("PORT", "5000")))
    debug = os.environ.get("ICON_QR_DEBUG", "0") == "1"
    app.run(host=host, port=port, debug=debug, use_reloader=False)
