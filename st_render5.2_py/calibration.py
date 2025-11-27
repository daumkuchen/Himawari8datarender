"""
データ校正モジュール（放射輝度から輝度温度への変換）
"""
import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .hsd_reader import HSData
    from .goes_reader import GOESData


def hsd_calibration(hs_data: 'HSData', debug: bool = False) -> np.ndarray:
    """
    HSDデータの校正（放射輝度から輝度温度への変換）

    Planck関数の逆関数を使用して、観測された放射輝度から輝度温度を計算します。

    Args:
        hs_data: HSDデータ構造体
        debug: デバッグ出力を表示するか

    Returns:
        輝度温度の配列 (numpy.ndarray)
    """
    if debug:
        print("hsdCalibration1")

    # 波長の単位変換 (μm -> m)
    wl = hs_data.wavelength * 1e-6
    wl5 = wl ** 5

    # Planck定数関連の計算
    hc_over_k_wl = (hs_data.H * hs_data.c) / (hs_data.k * wl)
    h2cc = 2 * hs_data.H * hs_data.c * hs_data.c
    h2cc_over_wl5 = h2cc / wl5
    h2cc_over_wl5 *= 1e-6

    slope = hs_data.slope
    intc = hs_data.intc

    if debug:
        print("hsdCalibration2")

    # データサイズ
    xy = hs_data.width * hs_data.height

    if debug:
        print(f"xy: {xy}")
        print(f"data[0]: {hs_data.data[0]}")

    # ルックアップテーブルを使用して高速化
    unique_values = np.unique(hs_data.data)
    lookup_table = {}

    for val in unique_values:
        # 放射輝度の計算
        radiance = slope * val + intc

        # Planck関数の逆関数で輝度温度を計算
        # T = (hc/kλ) / ln((2hc²/λ⁵) / L + 1)
        temp = hc_over_k_wl / np.log((h2cc_over_wl5 / radiance) + 1)
        lookup_table[val] = temp

    if debug:
        print("hsdCalibration3")

    # ルックアップテーブルを使用して変換
    temp_array = np.zeros(xy, dtype=np.float64)
    for i, val in enumerate(hs_data.data):
        temp_array[i] = lookup_table[val]

    if debug:
        print("hsdCalibration4")

    # HSDataに温度データを保存
    hs_data.temp = temp_array

    return temp_array


def goes_calibration(goes_data: 'GOESData', debug: bool = False) -> np.ndarray:
    """
    GOESデータの校正（放射輝度から輝度温度への変換）

    Args:
        goes_data: GOESデータ構造体
        debug: デバッグ出力を表示するか

    Returns:
        輝度温度の配列 (numpy.ndarray)
    """
    # 放射輝度の計算
    radiance = goes_data.data * goes_data.scale_factor + goes_data.add_offset

    # Planck関数の逆関数で輝度温度を計算
    # T = fk2 / ln((fk1 / L) + 1)
    temp_array = goes_data.planck_fk2 / np.log((goes_data.planck_fk1 / radiance) + 1)

    # GOESDataに温度データを保存
    goes_data.temp = temp_array

    if debug:
        print(f"planck_fk1: {goes_data.planck_fk1}")
        print(f"data[0]: {goes_data.data[0]}")
        print(f"temp[0]: {temp_array[0]}")

    return temp_array
