import cv2
import numpy as np
from PIL import Image
import io
from skimage.feature import graycomatrix, graycoprops, local_binary_pattern
from typing import Tuple, Dict, Any

class ImageProcessor:
    """
    Production-grade Computer Vision pipeline for field soil photography.
    Implements Laplacian blur gating, CLAHE normalization, and dual-stream
    (color moments + GLCM + LBP) feature extraction.
    """

    @staticmethod
    def bytes_to_cv2(image_bytes: bytes) -> np.ndarray:
        """Decodes raw byte stream into an OpenCV BGR matrix."""
        image_array = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Failed to decode image from bytes. File may be corrupted.")
        return img

    @staticmethod
    def compute_blur_score(img_bgr: np.ndarray) -> float:
        """
        Computes the variance of the Laplacian: Var(∇²I).
        Empirical threshold: >= 100 indicates sufficient optical clarity for soil analysis.
        """
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        score = float(laplacian.var())
        return score

    @classmethod
    def apply_clahe(cls, img_bgr: np.ndarray) -> np.ndarray:
        """
        Applies Contrast-Limited Adaptive Histogram Equalization (CLAHE)
        strictly to the L* (lightness) channel in CIELAB color space.
        Normalizes varying ambient sunlight without distorting chromatic ratios.
        """
        lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab)
        
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl = clahe.apply(l_channel)
        
        merged_lab = cv2.merge((cl, a_channel, b_channel))
        result_bgr = cv2.cvtColor(merged_lab, cv2.COLOR_LAB2BGR)
        return result_bgr

    @classmethod
    def segment_soil_surface(cls, img_bgr: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Isolates soil surface from incidental foliage and sky.
        Uses HSV color thresholding (filtering green leaves ~35°-85°),
        followed by morphological opening.
        Returns (masked_bgr, binary_mask).
        """
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        # Foliage green mask in HSV
        lower_green = np.array([35, 40, 40])
        upper_green = np.array([85, 255, 255])
        foliage_mask = cv2.inRange(hsv, lower_green, upper_green)
        
        # Soil is the inverse of green foliage
        soil_mask = cv2.bitwise_not(foliage_mask)
        
        # Clean small noise artifacts
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        clean_mask = cv2.morphologyEx(soil_mask, cv2.MORPH_OPEN, kernel)
        
        segmented_bgr = cv2.bitwise_and(img_bgr, img_bgr, mask=clean_mask)
        return segmented_bgr, clean_mask

    @classmethod
    def extract_physical_descriptors(cls, img_bgr: np.ndarray) -> Dict[str, float]:
        """
        Extracts scientific radiometric and textural descriptors:
        - Mean & Std of LAB and HSV components
        - Dark Channel Prior (DCP)
        - Gray-Level Co-occurrence Matrix (GLCM) Contrast, Energy, Homogeneity
        - Local Binary Pattern (LBP) entropy
        """
        # 1. Color Metrics in LAB & HSV
        lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        
        l_mean, l_std = float(np.mean(lab[:, :, 0])), float(np.std(lab[:, :, 0]))
        a_mean, a_std = float(np.mean(lab[:, :, 1])), float(np.std(lab[:, :, 1]))
        b_mean, b_std = float(np.mean(lab[:, :, 2])), float(np.std(lab[:, :, 2]))
        
        v_mean, v_std = float(np.mean(hsv[:, :, 2])), float(np.std(hsv[:, :, 2]))

        # 2. Dark Channel Prior (Soil darkening proxy)
        min_channel = np.min(img_bgr, axis=2)
        dcp_mean = float(np.mean(min_channel))

        # 3. GLCM Textural Descriptors
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        # Subsample to 128x128 for rapid texture computation
        small_gray = cv2.resize(gray, (128, 128))
        glcm = graycomatrix(small_gray, distances=[1], angles=[0], levels=256, symmetric=True, normed=True)
        
        contrast = float(graycoprops(glcm, 'contrast')[0, 0])
        dissimilarity = float(graycoprops(glcm, 'dissimilarity')[0, 0])
        homogeneity = float(graycoprops(glcm, 'homogeneity')[0, 0])
        energy = float(graycoprops(glcm, 'energy')[0, 0])

        # 4. Local Binary Patterns (LBP) for micro-granularity
        radius = 1
        n_points = 8 * radius
        lbp = local_binary_pattern(small_gray, n_points, radius, method='uniform')
        lbp_mean = float(np.mean(lbp))
        lbp_std = float(np.std(lbp))

        return {
            "l_mean": l_mean, "l_std": l_std,
            "a_mean": a_mean, "a_std": a_std,
            "b_mean": b_mean, "b_std": b_std,
            "v_mean": v_mean, "v_std": v_std,
            "dark_channel": dcp_mean,
            "glcm_contrast": contrast,
            "glcm_dissimilarity": dissimilarity,
            "glcm_homogeneity": homogeneity,
            "glcm_energy": energy,
            "lbp_mean": lbp_mean,
            "lbp_std": lbp_std
        }

    @classmethod
    def prepare_onnx_input(cls, img_bgr: np.ndarray, target_size=(224, 224)) -> np.ndarray:
        """
        Prepares a standardized NCHW float32 tensor matching ImageNet normalization:
        mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225].
        """
        rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        resized = cv2.resize(rgb, target_size, interpolation=cv2.INTER_AREA)
        
        # Convert to float and scale to [0, 1]
        normalized = resized.astype(np.float32) / 255.0
        
        # ImageNet normalization
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        normalized = (normalized - mean) / std
        
        # Transpose HWC -> CHW, add Batch dimension: (1, 3, 224, 224)
        tensor = np.transpose(normalized, (2, 0, 1))
        tensor = np.expand_dims(tensor, axis=0)
        return tensor
