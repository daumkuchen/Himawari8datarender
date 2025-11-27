"""
RGB合成モジュール
複数のHSDファイル（バンド1-3）からRGB画像を生成
"""
import numpy as np
from typing import List, Tuple, Optional
from PIL import Image
import os

from hsd_reader import hsd_read, HSData


def normalize_band_data(data: np.ndarray, bit_num: int, gamma: float = 2.2) -> np.ndarray:
    """
    バンドデータを正規化し、ガンマ補正を適用

    Args:
        data: 元のデータ配列 (UInt16)
        bit_num: ビット数
        gamma: ガンマ補正値（デフォルト: 2.2）

    Returns:
        正規化された配列 (0-255のUInt8)
    """
    # 最大値でスケーリング
    max_value = (2 ** bit_num) - 1
    normalized = data.astype(np.float32) / max_value

    # ガンマ補正
    corrected = np.power(normalized, 1.0 / gamma)

    # 0-255にスケーリング
    scaled = (corrected * 255).clip(0, 255).astype(np.uint8)

    return scaled


def create_rgb_composite(
    red_file: str,
    green_file: str,
    blue_file: str,
    output_path: str,
    gamma: float = 2.2,
    delete_dat: bool = False
) -> Tuple[int, int]:
    """
    3つのHSDファイルからRGB合成画像を生成

    Args:
        red_file: 赤チャンネル用のHSDファイルパス
        green_file: 緑チャンネル用のHSDファイルパス
        blue_file: 青チャンネル用のHSDファイルパス
        output_path: 出力ファイルパス
        gamma: ガンマ補正値
        delete_dat: 処理後にDATファイルを削除するか

    Returns:
        (width, height) のタプル
    """
    print("RGB合成を開始します...")

    # 各バンドのHSDファイルを読み込む
    print(f"赤チャンネル読み込み中: {red_file}")
    red_data = hsd_read(red_file, delete_dat=delete_dat, debug=False)

    print(f"緑チャンネル読み込み中: {green_file}")
    green_data = hsd_read(green_file, delete_dat=delete_dat, debug=False)

    print(f"青チャンネル読み込み中: {blue_file}")
    blue_data = hsd_read(blue_file, delete_dat=delete_dat, debug=False)

    # サイズの確認と調整
    print(f"バンド情報: R={red_data.band}({red_data.width}x{red_data.height}), "
          f"G={green_data.band}({green_data.width}x{green_data.height}), "
          f"B={blue_data.band}({blue_data.width}x{blue_data.height})")

    # 最小サイズを基準とする
    target_width = min(red_data.width, green_data.width, blue_data.width)
    target_height = min(red_data.height, green_data.height, blue_data.height)

    print(f"出力画像サイズ: {target_width}x{target_height}")

    # 各チャンネルを正規化
    print("データを正規化中...")
    red_channel = normalize_band_data(red_data.data, red_data.bit_num, gamma)
    green_channel = normalize_band_data(green_data.data, green_data.bit_num, gamma)
    blue_channel = normalize_band_data(blue_data.data, blue_data.bit_num, gamma)

    # 必要に応じてリサイズ
    if red_data.width != target_width or red_data.height != target_height:
        print(f"赤チャンネルをリサイズ中: {red_data.width}x{red_data.height} -> {target_width}x{target_height}")
        red_img = Image.fromarray(red_channel.reshape(red_data.height, red_data.width))
        red_img = red_img.resize((target_width, target_height), Image.Resampling.LANCZOS)
        red_channel = np.array(red_img).flatten()

    if green_data.width != target_width or green_data.height != target_height:
        print(f"緑チャンネルをリサイズ中: {green_data.width}x{green_data.height} -> {target_width}x{target_height}")
        green_img = Image.fromarray(green_channel.reshape(green_data.height, green_data.width))
        green_img = green_img.resize((target_width, target_height), Image.Resampling.LANCZOS)
        green_channel = np.array(green_img).flatten()

    if blue_data.width != target_width or blue_data.height != target_height:
        print(f"青チャンネルをリサイズ中: {blue_data.width}x{blue_data.height} -> {target_width}x{target_height}")
        blue_img = Image.fromarray(blue_channel.reshape(blue_data.height, blue_data.width))
        blue_img = blue_img.resize((target_width, target_height), Image.Resampling.LANCZOS)
        blue_channel = np.array(blue_img).flatten()

    width = target_width
    height = target_height

    # RGB画像を作成
    print("RGB画像を合成中...")
    rgb_array = np.stack([red_channel, green_channel, blue_channel], axis=-1)
    rgb_array = rgb_array.reshape(height, width, 3)

    # 画像として保存
    img = Image.fromarray(rgb_array)

    # 出力ディレクトリが存在しない場合は作成
    output_directory = os.path.dirname(output_path)
    if output_directory and not os.path.exists(output_directory):
        os.makedirs(output_directory, exist_ok=True)
        print(f"出力ディレクトリを作成しました: {output_directory}")

    img.save(output_path)
    print(f"RGB合成画像を保存しました: {output_path}")

    return width, height


def create_natural_color_rgb(
    band1_file: str,
    band2_file: str,
    band4_file: str,
    output_path: str,
    gamma: float = 2.2,
    delete_dat: bool = False
) -> Tuple[int, int]:
    """
    Natural Color RGB合成
    バンド1（青）、バンド2（緑）、バンド4（赤）を使用

    Args:
        band1_file: バンド1（0.47μm, 青）のHSDファイルパス
        band2_file: バンド2（0.51μm, 緑）のHSDファイルパス
        band4_file: バンド4（0.86μm, 赤代用）のHSDファイルパス
        output_path: 出力ファイルパス
        gamma: ガンマ補正値
        delete_dat: 処理後にDATファイルを削除するか

    Returns:
        (width, height) のタプル
    """
    print("Natural Color RGB合成を開始します...")
    print("注意: バンド3が利用できないため、バンド4を赤チャンネルとして使用します")

    return create_rgb_composite(
        red_file=band4_file,   # バンド4を赤として使用
        green_file=band2_file, # バンド2を緑として使用
        blue_file=band1_file,  # バンド1を青として使用
        output_path=output_path,
        gamma=gamma,
        delete_dat=delete_dat
    )
