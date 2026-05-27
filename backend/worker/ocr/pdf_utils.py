import fitz  # PyMuPDF
from PIL import Image
import io

def pdf_to_images(pdf_bytes: bytes, zoom: float = 2.0) -> list[Image.Image]:
    """
    Convert each page of a PDF to a PIL Image.
    zoom=2.0 doubles resolution (better OCR quality).
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    images = []

    for page in doc:
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        img_bytes = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        images.append(img)

    doc.close()
    return images