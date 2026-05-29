import io
import unittest

from app import app
from PIL import Image


class AppSmokeTest(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.client = app.test_client()

    def test_get_home(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Preview Box", response.data)

    def test_generate_with_solid_color(self):
        response = self.client.post(
            "/",
            data={
                "url": "https://example.com",
                "one_color": "#112233",
                "top_hex": "",
                "bottom_hex": "",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'download="Icon_QR.png"', response.data)

    def test_solid_mode_ignores_gradient_partial_input(self):
        response = self.client.post(
            "/",
            data={
                "color_mode": "solid",
                "url": "https://example.com",
                "one_color": "#224466",
                "top_hex": "#185A99",
                "bottom_hex": "",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'download="Icon_QR.png"', response.data)

    def test_generate_with_gradient(self):
        response = self.client.post(
            "/",
            data={
                "color_mode": "gradient",
                "url": "https://example.com",
                "one_color": "",
                "top_hex": "#185A99",
                "bottom_hex": "#92A73F",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'download="Icon_QR.png"', response.data)

    def test_gradient_requires_top_and_bottom(self):
        response = self.client.post(
            "/",
            data={
                "color_mode": "gradient",
                "url": "https://example.com",
                "one_color": "#112233",
                "top_hex": "#185A99",
                "bottom_hex": "",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Gradient mode requires both".encode("utf-8"), response.data)

    def test_icon_upload_accepts_any_png_filename(self):
        buffer = io.BytesIO()
        Image.new("RGBA", (20, 20), (255, 0, 0, 255)).save(buffer, format="PNG")
        buffer.seek(0)

        response = self.client.post(
            "/",
            data={
                "color_mode": "solid",
                "url": "https://example.com",
                "one_color": "#112233",
                "top_hex": "",
                "bottom_hex": "",
                "use_icon": "on",
                "icon_file": (buffer, "my-custom-name.png"),
            },
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'download="Icon_QR.png"', response.data)

    def test_healthcheck(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"status": "ok"})


if __name__ == "__main__":
    unittest.main()
