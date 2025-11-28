"""
カラースケール変換モジュール
"""
import numpy as np


def bw_scale(data: np.ndarray, bit_num: int) -> np.ndarray:
    """
    白黒スケール変換

    Args:
        data: 元のデータ配列 (UInt16)
        bit_num: ビット数

    Returns:
        RGB画像データ (numpy.ndarray, shape=(height, width, 3))
    """
    # ビットシフト
    if bit_num > 8:
        shift = bit_num - 8
    else:
        shift = 0

    # ビットシフトして8ビットに変換
    gray = (data >> shift).astype(np.uint8)

    # RGB3チャンネルに複製
    rgb = np.stack([gray, gray, gray], axis=-1)

    return rgb


def bd_scale_value(temp: float) -> int:
    """
    BDカラースケール（単一値）

    Args:
        temp: 輝度温度 (K)

    Returns:
        グレースケール値 (0-255)
    """
    if temp > 303.15:
        return 0
    elif temp > 282.15:
        return int((303.15 - temp) * 12)
    elif temp > 242.15:
        return int((282.15 - temp) * 2 + 100)
    elif temp > 231.15:
        return 80
    elif temp > 219.15:
        return 130
    elif temp > 209.15:
        return 190
    elif temp > 203.15:
        return 0
    elif temp > 197.15:
        return 255
    elif temp > 192.15:
        return 170
    else:
        return 120


def bd_scale(temp_array: np.ndarray) -> np.ndarray:
    """
    BDカラースケール変換（配列処理）

    Args:
        temp_array: 輝度温度配列 (K)

    Returns:
        RGB画像データ (numpy.ndarray, shape=(height, width, 3))
    """
    # ベクトル化した条件分岐
    result = np.zeros(len(temp_array), dtype=np.uint8)

    # 欠損値（0K）は黒のまま
    valid_mask = temp_array > 0

    result[valid_mask & (temp_array > 303.15)] = 0
    mask = valid_mask & (temp_array > 282.15) & (temp_array <= 303.15)
    result[mask] = ((303.15 - temp_array[mask]) * 12).astype(np.uint8)
    mask = valid_mask & (temp_array > 242.15) & (temp_array <= 282.15)
    result[mask] = ((282.15 - temp_array[mask]) * 2 + 100).astype(np.uint8)
    result[valid_mask & (temp_array > 231.15) & (temp_array <= 242.15)] = 80
    result[valid_mask & (temp_array > 219.15) & (temp_array <= 231.15)] = 130
    result[valid_mask & (temp_array > 209.15) & (temp_array <= 219.15)] = 190
    result[valid_mask & (temp_array > 203.15) & (temp_array <= 209.15)] = 0
    result[valid_mask & (temp_array > 197.15) & (temp_array <= 203.15)] = 255
    result[valid_mask & (temp_array > 192.15) & (temp_array <= 197.15)] = 170
    mask = valid_mask & (temp_array <= 192.15)
    result[mask] = 120

    # RGB3チャンネルに複製
    rgb = np.stack([result, result, result], axis=-1)

    return rgb


def color2_r(temp_array: np.ndarray) -> np.ndarray:
    """Color2スケール - 赤チャンネル"""
    result = np.zeros(len(temp_array), dtype=np.uint8)

    # 欠損値（0K）は黒のまま
    valid_mask = temp_array > 0

    result[valid_mask & (temp_array > 303.15)] = 0
    mask = valid_mask & (temp_array > 243.15) & (temp_array <= 303.15)
    result[mask] = ((303.15 - temp_array[mask]) * 4).astype(np.uint8)
    result[valid_mask & (temp_array > 223.15) & (temp_array <= 243.15)] = 50
    result[valid_mask & (temp_array > 203.15) & (temp_array <= 223.15)] = 0
    mask = valid_mask & (temp_array > 193.15) & (temp_array <= 203.15)
    result[mask] = ((203.15 - temp_array[mask]) * 15 + 100).astype(np.uint8)
    mask = valid_mask & (temp_array > 183.15) & (temp_array <= 193.15)
    result[mask] = ((temp_array[mask] - 183.15) * 25).astype(np.uint8)
    mask = valid_mask & (temp_array <= 183.15)
    result[mask] = ((temp_array[mask] - 173.15) * 25).astype(np.uint8)

    return result


def color2_g(temp_array: np.ndarray) -> np.ndarray:
    """Color2スケール - 緑チャンネル"""
    result = np.zeros(len(temp_array), dtype=np.uint8)

    # 欠損値（0K）は黒のまま
    valid_mask = temp_array > 0

    result[valid_mask & (temp_array > 303.15)] = 0
    mask = valid_mask & (temp_array > 243.15) & (temp_array <= 303.15)
    result[mask] = ((303.15 - temp_array[mask]) * 4).astype(np.uint8)
    mask = valid_mask & (temp_array > 223.15) & (temp_array <= 243.15)
    result[mask] = ((temp_array[mask] - 223.15) * 6 + 120).astype(np.uint8)
    result[valid_mask & (temp_array > 213.15) & (temp_array <= 223.15)] = 0
    mask = valid_mask & (temp_array > 203.15) & (temp_array <= 213.15)
    result[mask] = ((213.15 - temp_array[mask]) * 15 + 100).astype(np.uint8)
    result[valid_mask & (temp_array > 193.15) & (temp_array <= 203.15)] = 0
    mask = valid_mask & (temp_array > 183.15) & (temp_array <= 193.15)
    result[mask] = ((temp_array[mask] - 183.15) * 25).astype(np.uint8)
    mask = valid_mask & (temp_array <= 183.15)
    result[mask] = ((temp_array[mask] - 173.15) * 25).astype(np.uint8)

    return result


def color2_b(temp_array: np.ndarray) -> np.ndarray:
    """Color2スケール - 青チャンネル"""
    result = np.zeros(len(temp_array), dtype=np.uint8)

    # 欠損値（0K）は黒のまま
    valid_mask = temp_array > 0

    result[valid_mask & (temp_array > 303.15)] = 0
    mask = valid_mask & (temp_array > 243.15) & (temp_array <= 303.15)
    result[mask] = ((303.15 - temp_array[mask]) * 4).astype(np.uint8)
    mask = valid_mask & (temp_array > 223.15) & (temp_array <= 243.15)
    result[mask] = ((temp_array[mask] - 223.15) * 6 + 120).astype(np.uint8)
    mask = valid_mask & (temp_array > 213.15) & (temp_array <= 223.15)
    result[mask] = ((223.15 - temp_array[mask]) * 15 + 100).astype(np.uint8)
    result[valid_mask & (temp_array > 183.15) & (temp_array <= 213.15)] = 0
    mask = valid_mask & (temp_array <= 183.15)
    result[mask] = ((temp_array[mask] - 173.15) * 25).astype(np.uint8)

    return result


def color2_scale(temp_array: np.ndarray) -> np.ndarray:
    """
    Color2カラースケール変換

    Args:
        temp_array: 輝度温度配列 (K)

    Returns:
        RGB画像データ (numpy.ndarray, shape=(height, width, 3))
    """
    r = color2_r(temp_array)
    g = color2_g(temp_array)
    b = color2_b(temp_array)

    rgb = np.stack([r, g, b], axis=-1)

    return rgb


def wvnrl_r(temp_array: np.ndarray) -> np.ndarray:
    """水蒸気カラースケール - 赤チャンネル"""
    result = np.full(len(temp_array), 128, dtype=np.uint8)

    # 欠損値（0K）は黒
    valid_mask = temp_array > 0
    result[~valid_mask] = 0

    result[valid_mask & (temp_array > 273.15)] = 127
    mask = valid_mask & (temp_array > 263.15) & (temp_array <= 273.15)
    result[mask] = ((temp_array[mask] - 263.15) * 10.8 + 20).astype(np.uint8)
    mask = valid_mask & (temp_array > 253.15) & (temp_array <= 263.15)
    result[mask] = (20 + (263.15 - temp_array[mask]) * 3).astype(np.uint8)
    mask = valid_mask & (temp_array > 243.15) & (temp_array <= 253.15)
    result[mask] = (50 + (253.15 - temp_array[mask]) * 7.8).astype(np.uint8)
    mask = valid_mask & (temp_array > 233.15) & (temp_array <= 243.15)
    result[mask] = ((127 + 243.15 - temp_array[mask]) * 12.8).astype(np.uint8)
    result[valid_mask & (temp_array > 223.15) & (temp_array <= 233.15)] = 255
    mask = valid_mask & (temp_array <= 223.15)
    result[mask] = (127 + (temp_array[mask] - 203.15) * 6.4).astype(np.uint8)

    return result


def wvnrl_g(temp_array: np.ndarray) -> np.ndarray:
    """水蒸気カラースケール - 緑チャンネル"""
    result = np.zeros(len(temp_array), dtype=np.uint8)

    # 欠損値（0K）は黒のまま
    valid_mask = temp_array > 0

    result[valid_mask & (temp_array > 273.15)] = 0
    mask = valid_mask & (temp_array > 263.15) & (temp_array <= 273.15)
    result[mask] = ((273.15 - temp_array[mask]) * 10).astype(np.uint8)
    mask = valid_mask & (temp_array > 253.15) & (temp_array <= 263.15)
    result[mask] = (100 + (263.15 - temp_array[mask]) * 5).astype(np.uint8)
    mask = valid_mask & (temp_array > 243.15) & (temp_array <= 253.15)
    result[mask] = (150 + (253.15 - temp_array[mask]) * 10.5).astype(np.uint8)
    result[valid_mask & (temp_array > 233.15) & (temp_array <= 243.15)] = 255
    mask = valid_mask & (temp_array > 223.15) & (temp_array <= 233.15)
    result[mask] = (180 + (temp_array[mask] - 223.15) * 7.5).astype(np.uint8)
    mask = valid_mask & (temp_array <= 223.15)
    result[mask] = ((temp_array[mask] - 203.15) * 9).astype(np.uint8)

    return result


def wvnrl_b(temp_array: np.ndarray) -> np.ndarray:
    """水蒸気カラースケール - 青チャンネル"""
    result = np.zeros(len(temp_array), dtype=np.uint8)

    # 欠損値（0K）は黒のまま
    valid_mask = temp_array > 0

    result[valid_mask & (temp_array > 273.15)] = 140
    mask = valid_mask & (temp_array > 263.15) & (temp_array <= 273.15)
    result[mask] = (140 + (273.15 - temp_array[mask]) * 9).astype(np.uint8)
    mask = valid_mask & (temp_array > 253.15) & (temp_array <= 263.15)
    result[mask] = (230 + (263.15 - temp_array[mask]) * 2.5).astype(np.uint8)
    result[valid_mask & (temp_array > 243.15) & (temp_array <= 253.15)] = 255
    mask = valid_mask & (temp_array > 233.15) & (temp_array <= 243.15)
    result[mask] = (127 + (temp_array[mask] - 233.15) * 12.8).astype(np.uint8)
    mask = valid_mask & (temp_array > 223.15) & (temp_array <= 233.15)
    result[mask] = (100 + (temp_array[mask] - 223.15) * 2.8).astype(np.uint8)
    mask = valid_mask & (temp_array <= 223.15)
    result[mask] = ((temp_array[mask] - 203.15) * 5).astype(np.uint8)

    return result


def wvnrl_scale(temp_array: np.ndarray) -> np.ndarray:
    """
    水蒸気カラースケール変換

    Args:
        temp_array: 輝度温度配列 (K)

    Returns:
        RGB画像データ (numpy.ndarray, shape=(height, width, 3))
    """
    r = wvnrl_r(temp_array)
    g = wvnrl_g(temp_array)
    b = wvnrl_b(temp_array)

    rgb = np.stack([r, g, b], axis=-1)

    return rgb
