import qrcode

from io import BytesIO
from qrcode.image.pil import PilImage


def QRcode_generation(text) -> bytes:
    qr = qrcode.QRCode()
    qr.add_data(text)
    image = qr.make_image(PilImage)
    bg_bio = BytesIO()
    image.save(bg_bio, format="jpeg")
    return bg_bio.getvalue()
