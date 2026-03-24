import os
import qrcode
from flask import current_app


def generate_qr(book, base_url='http://localhost:5001'):
    url = f'{base_url}/books/{book.id}'
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color='black', back_color='white')
    filename = f'book_{book.id}.png'
    filepath = os.path.join(current_app.config['QR_CODE_DIR'], filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    img.save(filepath)

    return f'qrcodes/{filename}'
