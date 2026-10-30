"""Keep the declared U2-Net isolation workflow stable across rembg upgrades."""

from io import BytesIO

from PIL import Image
import pytest

from app.processing import image_isolation


def test_isolation_keeps_u2net_and_crops_the_subject_without_model_download(monkeypatch):
    rembg = pytest.importorskip("rembg")
    image_isolation._u2net_session.cache_clear()
    created = []

    class SyntheticSession:
        def predict(self, image, *_args, **_kwargs):
            mask = Image.new("L", image.size, 0)
            mask.paste(255, (8, 6, 24, 18))
            return [mask]

    def session_for(model_name, *_args, **_kwargs):
        # An unexpected default must fail closed in this fixture. No real model
        # is instantiated or downloaded, even if the selected library changes.
        if model_name != "u2net":
            raise ValueError("Unexpected isolation model")
        created.append(model_name)
        return SyntheticSession()

    monkeypatch.setattr(rembg.bg, "new_session", session_for)
    monkeypatch.setattr(rembg, "new_session", session_for)
    source = BytesIO()
    Image.new("RGB", (32, 24), (180, 60, 30)).save(source, format="PNG")
    try:
        for _ in range(2):
            result = image_isolation.isolate_building(source.getvalue())
            with Image.open(BytesIO(result)) as image:
                assert image.format == "PNG"
                assert image.size == (16, 12)
                assert image.getpixel((8, 6)) == (180, 60, 30)
        assert created == ["u2net"]
    finally:
        image_isolation._u2net_session.cache_clear()
