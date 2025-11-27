"""
Himawari Standard Data (HSD) ファイル読み込みモジュール
"""
import struct
import os
import bz2
import numpy as np
from dataclasses import dataclass
from typing import Optional


@dataclass
class HSData:
    """Himawari Standard Data構造体"""
    satellite_name: str
    width: int
    height: int
    band: int
    wavelength: float
    bit_num: int
    slope: float
    intc: float
    c0: float = 0.0
    c1: float = 0.0
    c2: float = 0.0
    c: float = 0.0
    H: float = 0.0
    k: float = 0.0
    data: Optional[np.ndarray] = None
    temp: Optional[np.ndarray] = None


def decompress_bz2(filepath: str) -> str:
    """
    bz2ファイルを解凍

    Args:
        filepath: bz2ファイルのパス

    Returns:
        解凍後のDATファイルのパス
    """
    if not filepath.endswith('.bz2'):
        return filepath

    dat_filepath = filepath[:-4]  # .bz2を除去

    # すでにDATファイルが存在する場合はスキップ
    if os.path.exists(dat_filepath):
        print(f"DATファイルが既に存在します: {dat_filepath}")
        return dat_filepath

    print(f"bz2ファイルを解凍中: {filepath}")
    with bz2.open(filepath, 'rb') as f_in:
        with open(dat_filepath, 'wb') as f_out:
            f_out.write(f_in.read())

    print(f"解凍完了: {dat_filepath}")
    return dat_filepath


def hsd_read(filepath: str, delete_dat: bool = False, debug: bool = False) -> HSData:
    """
    HSDファイルを読み込む

    Args:
        filepath: HSDファイルのパス (.DAT または .DAT.bz2)
        delete_dat: 処理後にDATファイルを削除するか
        debug: デバッグ出力を表示するか

    Returns:
        HSData構造体
    """
    if debug:
        print("debughsdRead1")

    # bz2の場合は解凍
    dat_filepath = decompress_bz2(filepath)

    if debug:
        print(f"DATファイル: {dat_filepath}")
        print("debughsdRead2")

    # バイナリファイルを開く
    with open(dat_filepath, 'rb') as fp:
        if debug:
            print("debughsdRead3")

        # ヘッダー部分の読み込み
        fp.seek(6)  # 最初の6バイトをスキップ

        # 衛星名 (16 bytes)
        satellite_name = fp.read(16).decode('ascii', errors='ignore').strip('\x00')

        fp.seek(260, 1)  # 相対位置で260バイトスキップ

        if debug:
            print("debughsdRead4")

        # 1バイト読み込み（使用しない）
        fp.read(1)

        fp.seek(4, 1)  # 4バイトスキップ

        if debug:
            print("debughsdRead5")

        # 幅と高さ (UInt16, little endian)
        width = struct.unpack('<H', fp.read(2))[0]
        height = struct.unpack('<H', fp.read(2))[0]

        if debug:
            print(f"debughsdRead6\nwidth: {width}\nheight: {height}")

        # 41バイトスキップ
        fp.seek(41, 1)

        # 269バイトスキップ
        fp.seek(269, 1)

        # バンド番号 (UInt16)
        band = struct.unpack('<H', fp.read(2))[0]

        # 波長 (double, 8 bytes)
        wavelength = struct.unpack('<d', fp.read(8))[0]

        if debug:
            print(f"wavelength: {wavelength}")

        # ビット数 (UInt16)
        bit_num = struct.unpack('<H', fp.read(2))[0]

        if debug:
            print(f"bits: {bit_num}")

        # 4バイトスキップ
        fp.seek(4, 1)

        # Slope と intc (double)
        slope = struct.unpack('<d', fp.read(8))[0]
        intc = struct.unpack('<d', fp.read(8))[0]

        # バンド7以上の場合、校正パラメータを読み込む
        if band > 6:
            c0 = struct.unpack('<d', fp.read(8))[0]
            c1 = struct.unpack('<d', fp.read(8))[0]
            c2 = struct.unpack('<d', fp.read(8))[0]
            fp.seek(24, 1)  # 24バイトスキップ
            c = struct.unpack('<d', fp.read(8))[0]
            H = struct.unpack('<d', fp.read(8))[0]
            k = struct.unpack('<d', fp.read(8))[0]
            fp.seek(40, 1)  # 40バイトスキップ
        else:
            c0 = c1 = c2 = c = H = k = 0.0
            fp.seek(112, 1)  # 112バイトスキップ

        # さらにスキップ
        fp.seek(1 + 47 + 258 + 1, 1)

        # len8, len9, len10
        len8 = struct.unpack('<H', fp.read(2))[0]
        fp.seek(len8 - 2, 1)

        len9 = struct.unpack('<H', fp.read(2))[0]
        fp.seek(len9 - 2, 1)

        len10 = struct.unpack('<I', fp.read(4))[0]
        fp.seek(len10, 1)

        fp.seek(254, 1)

        # 画像データを読み込む (UInt16配列)
        n = width * height
        if debug:
            print(f"データサイズ: {n}")

        # バイナリデータを読み込んでnumpy配列に変換
        data_bytes = fp.read(n * 2)
        data = np.frombuffer(data_bytes, dtype=np.uint16, count=n)

        if debug:
            print(f"data[0]: {data[0]}")

    # HSData構造体を作成
    hs_data = HSData(
        satellite_name=satellite_name,
        width=width,
        height=height,
        band=band,
        wavelength=wavelength,
        bit_num=bit_num,
        slope=slope,
        intc=intc,
        c0=c0,
        c1=c1,
        c2=c2,
        c=c,
        H=H,
        k=k,
        data=data
    )

    # DATファイルを削除する場合
    if delete_dat and dat_filepath != filepath:
        try:
            os.remove(dat_filepath)
            print(f"DATファイルを削除しました: {dat_filepath}")
        except Exception as e:
            print(f"DATファイルの削除に失敗: {e}")

    return hs_data
