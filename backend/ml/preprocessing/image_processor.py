import io
import numpy as np
from PIL import Image, ImageStat
from backend.config import settings

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

class ImageQualityResult:
    def __init__(self, is_valid: bool, error_message: str = None, warnings: list = None, image_np: np.ndarray = None, pil_image: Image.Image = None):
        self.is_valid = is_valid
        self.error_message = error_message
        self.warnings = warnings or []
        self.image_np = image_np
        self.pil_image = pil_image

def validate_and_preprocess_image(file_bytes: bytes, filename: str = "") -> ImageQualityResult:
    # 1. Size Check
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > settings.MAX_IMAGE_SIZE_MB:
        return ImageQualityResult(
            is_valid=False,
            error_message=f"File size ({size_mb:.1f} MB) exceeds maximum allowed limit of {settings.MAX_IMAGE_SIZE_MB} MB."
        )

    # 2. Decode Image with Pillow (robust format detection by content, not just extension)
    try:
        pil_img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
        img_np = np.array(pil_img)
    except Exception as e:
        return ImageQualityResult(
            is_valid=False,
            error_message="Corrupted or unreadable image file. Please re-capture or upload a valid photo."
        )

    height, width, _ = img_np.shape

    # 3. Dimension Resolution Check
    if width < 50 or height < 50:
        return ImageQualityResult(
            is_valid=False,
            error_message="Image resolution is too low (<50x50 px) for accurate AI computer vision diagnosis. Please upload a clearer photo."
        )
    elif width < 150 or height < 150:
        # Gracefully upscale small previews to 224x224 for MobileNetV2
        pil_img = pil_img.resize((224, 224), Image.Resampling.BILINEAR)
        img_np = np.array(pil_img)

    warnings = []

    # 5. Darkness & Blur Check (OpenCV or Pillow fallback)
    if HAS_CV2:
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        mean_brightness = float(np.mean(gray))
        laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    else:
        gray_pil = pil_img.convert("L")
        stat = ImageStat.Stat(gray_pil)
        mean_brightness = float(stat.mean[0])
        # Approximate variance
        laplacian_var = float(stat.stddev[0] ** 2)

    if mean_brightness < 40.0:
        warnings.append("Image is extremely dark. Capture under clear natural sunlight for better accuracy.")

    if laplacian_var < 80.0:
        warnings.append("Image appears blurry. Ensure the crop leaf is sharply in focus.")

    return ImageQualityResult(
        is_valid=True,
        warnings=warnings,
        image_np=img_np,
        pil_image=pil_img
    )
