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

    # 3. Dimension Resolution Check (<150x150 px strictly rejected)
    if width < 150 or height < 150:
        return ImageQualityResult(
            is_valid=False,
            error_message=f"Image resolution ({width}x{height} px) is too low (<150x150 px) for reliable crop diagnosis. Please take a closer, higher-resolution photo."
        )

    # 4. Darkness, Brightness & Blur Gate (OpenCV or Pillow fallback)
    if HAS_CV2:
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        mean_brightness = float(np.mean(gray))
        laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    else:
        gray_pil = pil_img.convert("L")
        stat = ImageStat.Stat(gray_pil)
        mean_brightness = float(stat.mean[0])
        laplacian_var = float(stat.stddev[0] ** 2)

    # Strict Quality Rejections
    if mean_brightness < 35.0:
        return ImageQualityResult(
            is_valid=False,
            error_message="Image is too dark for diagnostic evaluation (mean brightness < 35). Please retake in clear, natural daytime lighting."
        )

    if mean_brightness > 225.0:
        return ImageQualityResult(
            is_valid=False,
            error_message="Image is washed out or overexposed (mean brightness > 225). Please avoid direct camera flash or glare and retake."
        )

    if laplacian_var < 70.0:
        return ImageQualityResult(
            is_valid=False,
            error_message="Image is too blurry for reliable computer vision pathology (focus score < 70). Hold your camera steady and ensure the leaf lamina is in sharp focus."
        )

    warnings = []
    if mean_brightness < 50.0:
        warnings.append("Lighting is somewhat dim. Better daylight improves diagnostic confidence.")
    if laplacian_var < 100.0:
        warnings.append("Leaf focus is marginal. For critical decisions, take a sharper close-up.")

    return ImageQualityResult(
        is_valid=True,
        warnings=warnings,
        image_np=img_np,
        pil_image=pil_img
    )
