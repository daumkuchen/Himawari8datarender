"""
画像補正モジュール
ImageMagickの補正処理をPythonで実装
GPU対応（CuPy）による高速化をサポート
"""
import os
import numpy as np
from PIL import Image, ImageEnhance

# 環境変数の読み込み
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenvがインストールされていない場合はスキップ

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

# 環境変数 USE_GPU でGPU使用を制御
USE_GPU_ENV = os.getenv('USE_GPU', 'true').lower() in ('true', '1', 'yes')

try:
    import cupy as cp
    HAS_CUPY = True
    if USE_GPU_ENV:
        print("CuPy検出: GPU高速化が有効です")
    else:
        print("CuPy検出: 環境変数 USE_GPU=false のため CPU処理で実行します")
        HAS_CUPY = False  # 環境変数で無効化
except ImportError:
    HAS_CUPY = False
    if USE_GPU_ENV:
        print("CuPy未検出: CPU処理で実行します")
    else:
        print("環境変数 USE_GPU=false: CPU処理で実行します")


def apply_level(img_array: np.ndarray, black_point: float = 0.0, white_point: float = 100.0, gamma: float = 1.0) -> np.ndarray:
    """
    レベル補正を適用（ImageMagickの-levelに相当）

    Args:
        img_array: 入力画像配列 (H, W, 3)
        black_point: 黒点 (0-100%)
        white_point: 白点 (0-100%)
        gamma: ガンマ値

    Returns:
        補正後の画像配列
    """
    # パーセンテージを0-1の範囲に変換
    black_point = black_point / 100.0
    white_point = white_point / 100.0

    # GPU高速化版（CuPy利用可能な場合）
    if HAS_CUPY and gamma != 1.0:
        # GPU上で処理
        result_gpu = cp.asarray(img_array, dtype=cp.float32) / 255.0

        # レベル補正
        result_gpu = (result_gpu - black_point) / (white_point - black_point)
        result_gpu = cp.clip(result_gpu, 0.0, 1.0)

        # ガンマ補正（GPU上でべき乗計算）
        result_gpu = cp.power(result_gpu, 1.0 / gamma)

        # 0-255に戻してCPUに転送
        result = (result_gpu * 255).clip(0, 255).astype(cp.uint8)
        result = cp.asnumpy(result)

        return result

    # CPU版（従来の処理）
    # 浮動小数点数に変換
    result = img_array.astype(np.float32) / 255.0

    # レベル補正の適用
    # (value - black_point) / (white_point - black_point)
    result = (result - black_point) / (white_point - black_point)
    result = np.clip(result, 0.0, 1.0)

    # ガンマ補正（ImageMagick -level 0%,100%,1.5）
    if gamma != 1.0:
        result = np.power(result, 1.0 / gamma)

    # 0-255に戻す
    result = (result * 255).clip(0, 255).astype(np.uint8)

    return result


def apply_modulate(img_array: np.ndarray, brightness: float = 100.0, saturation: float = 100.0, hue: float = 100.0) -> np.ndarray:
    """
    色調補正を適用（ImageMagickの-modulateに相当）

    Args:
        img_array: 入力画像配列 (H, W, 3)
        brightness: 明度 (100が基準)
        saturation: 彩度 (100が基準)
        hue: 色相 (100が基準)

    Returns:
        補正後の画像配列
    """
    # PIL Imageを使用して高速化
    from PIL import Image, ImageEnhance

    img = Image.fromarray(img_array)

    # 20251128_色調補正: 1. 明度（Brightness）の調整
    # 20251128_色調補正: if brightness != 100.0:
    # 20251128_色調補正:     brightness_factor = brightness / 100.0
    # 20251128_色調補正:     enhancer = ImageEnhance.Brightness(img)
    # 20251128_色調補正:     img = enhancer.enhance(brightness_factor)

    # 20251128_色調補正: 2. 彩度（Saturation）の調整
    # 20251128_色調補正: if saturation != 100.0:
    # 20251128_色調補正:     saturation_factor = saturation / 100.0
    # 20251128_色調補正:     enhancer = ImageEnhance.Color(img)
    # 20251128_色調補正:     img = enhancer.enhance(saturation_factor)

    # 彩度（Saturation）の調整（ImageMagick -modulate 100,250,102）
    if saturation != 100.0:
        saturation_factor = saturation / 100.0

        # GPU高速化版（CuPy利用可能な場合）
        if HAS_CUPY:
            img_array_temp = np.array(img, dtype=np.float32) / 255.0
            img_gpu = cp.asarray(img_array_temp)

            # RGB to grayscale (luminance)
            gray = 0.299 * img_gpu[:, :, 0] + 0.587 * img_gpu[:, :, 1] + 0.114 * img_gpu[:, :, 2]
            gray_3ch = cp.stack([gray, gray, gray], axis=2)

            # Blend original with grayscale
            result_gpu = gray_3ch + saturation_factor * (img_gpu - gray_3ch)
            result_gpu = cp.clip(result_gpu * 255, 0, 255).astype(cp.uint8)

            img = Image.fromarray(cp.asnumpy(result_gpu))
        else:
            # CPU版（PIL ImageEnhance使用）
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(saturation_factor)

    # 20251128_色調補正: 3. 色相（Hue）の調整
    # 20251128_色調補正: # PILには直接的な色相調整がないため、HSVで処理
    # 20251128_色調補正: if hue != 100.0 and HAS_CV2:
    # 20251128_色調補正:     img_array_temp = np.array(img)
    # 20251128_色調補正:     # RGBからHSVに変換
    # 20251128_色調補正:     hsv = cv2.cvtColor(img_array_temp, cv2.COLOR_RGB2HSV).astype(np.float32)
    # 20251128_色調補正:     # 色相をシフト（ImageMagickの-modulateの色相は0-200の範囲）
    # 20251128_色調補正:     hue_shift = ((hue - 100.0) / 100.0) * 180.0  # OpenCVのHueは0-180
    # 20251128_色調補正:     hsv[:, :, 0] = (hsv[:, :, 0] + hue_shift) % 180
    # 20251128_色調補正:     # HSVからRGBに戻す
    # 20251128_色調補正:     img_array_temp = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
    # 20251128_色調補正:     img = Image.fromarray(img_array_temp)
    # 20251128_色調補正: elif hue != 100.0 and not HAS_CV2:
    # 20251128_色調補正:     print("警告: opencv-pythonがインストールされていないため、色相調整をスキップします")

    # 色相（Hue）の調整（ImageMagick -modulate 100,250,102）
    if hue != 100.0 and HAS_CV2:
        img_array_temp = np.array(img)

        # GPU高速化版（CuPy利用可能な場合）
        if HAS_CUPY:
            # RGBからHSVに変換（OpenCV CPU版）
            hsv = cv2.cvtColor(img_array_temp, cv2.COLOR_RGB2HSV)

            # GPU上で色相シフト処理
            hsv_gpu = cp.asarray(hsv, dtype=cp.float32)
            hue_shift = ((hue - 100.0) / 100.0) * 180.0  # OpenCVのHueは0-180
            hsv_gpu[:, :, 0] = (hsv_gpu[:, :, 0] + hue_shift) % 180
            hsv = cp.asnumpy(hsv_gpu).astype(np.uint8)

            # HSVからRGBに戻す（OpenCV CPU版）
            img_array_temp = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
            img = Image.fromarray(img_array_temp)
        else:
            # CPU版（従来の処理）
            # RGBからHSVに変換
            hsv = cv2.cvtColor(img_array_temp, cv2.COLOR_RGB2HSV).astype(np.float32)
            # 色相をシフト（ImageMagickの-modulateの色相は0-200の範囲）
            hue_shift = ((hue - 100.0) / 100.0) * 180.0  # OpenCVのHueは0-180
            hsv[:, :, 0] = (hsv[:, :, 0] + hue_shift) % 180
            # HSVからRGBに戻す
            img_array_temp = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
            img = Image.fromarray(img_array_temp)
    elif hue != 100.0 and not HAS_CV2:
        print("警告: opencv-pythonがインストールされていないため、色相調整をスキップします")

    result = np.array(img)
    return result


def apply_contrast(img_array: np.ndarray, enhance_factor: float = 1.5) -> np.ndarray:
    """
    コントラスト強調を適用（ImageMagickの-contrastに相当）

    Args:
        img_array: 入力画像配列 (H, W, 3)
        enhance_factor: コントラスト強調係数（1.5程度が-contrastに相当）

    Returns:
        補正後の画像配列
    """
    # GPU高速化版（CuPy利用可能な場合）
    if HAS_CUPY:
        img_gpu = cp.asarray(img_array, dtype=cp.float32) / 255.0

        # Mean value
        mean = cp.mean(img_gpu)

        # Enhance contrast
        result_gpu = mean + enhance_factor * (img_gpu - mean)
        result_gpu = cp.clip(result_gpu * 255, 0, 255).astype(cp.uint8)

        return cp.asnumpy(result_gpu)

    # CPU版（PIL ImageEnhance使用）
    img = Image.fromarray(img_array)
    enhancer = ImageEnhance.Contrast(img)
    img_enhanced = enhancer.enhance(enhance_factor)

    # numpyに戻す
    result = np.array(img_enhanced)

    return result


def apply_imagemagick_enhance(
    img_array: np.ndarray,
    level_gamma: float = 1.5,
    modulate_brightness: float = 100.0,
    modulate_saturation: float = 250.0,
    modulate_hue: float = 102.0,
    apply_contrast_enhance: bool = True
) -> np.ndarray:
    """
    ImageMagickの補正処理を適用

    ImageMagickコマンド相当:
    convert input.png -level 0%,100%,1.5 -modulate 100,250,102 -contrast output.png

    Args:
        img_array: 入力画像配列 (H, W, 3)
        level_gamma: レベル補正のガンマ値（デフォルト: 1.5）
        modulate_brightness: 明度（デフォルト: 100）
        modulate_saturation: 彩度（デフォルト: 250）
        modulate_hue: 色相（デフォルト: 102）
        apply_contrast_enhance: コントラスト強調を適用するか（デフォルト: True）

    Returns:
        補正後の画像配列
    """
    # 1. レベル補正（ガンマ補正）
    result = apply_level(img_array, black_point=0.0, white_point=100.0, gamma=level_gamma)

    # 2. 色調補正（明度・彩度・色相）
    result = apply_modulate(result, brightness=modulate_brightness, saturation=modulate_saturation, hue=modulate_hue)

    # 20251128_色調補正: 3. コントラスト強調
    # 20251128_色調補正: if apply_contrast_enhance:
    # 20251128_色調補正:     result = apply_contrast(result, enhance_factor=1.5)

    # 20251129_色調補正_v2: 3. コントラスト強調（ImageMagick -contrast）
    if apply_contrast_enhance:
        result = apply_contrast(result, enhance_factor=1.5)

    return result
