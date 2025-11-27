"""
GOES衛星 netCDFファイル読み込みモジュール
"""
import numpy as np
from dataclasses import dataclass
from typing import Optional

try:
    from netCDF4 import Dataset
    NETCDF_AVAILABLE = True
except ImportError:
    NETCDF_AVAILABLE = False
    print("警告: netCDF4がインストールされていません。GOES衛星データの処理には netCDF4 が必要です。")
    print("インストール方法: pip install netCDF4")


@dataclass
class GOESData:
    """GOES衛星データ構造体"""
    x: int
    y: int
    band: int
    scale_factor: float
    add_offset: float
    planck_fk1: float
    planck_fk2: float
    planck_bc1: float
    planck_bc2: float
    data: Optional[np.ndarray] = None
    temp: Optional[np.ndarray] = None


def goes_read(filepath: str, debug: bool = False) -> GOESData:
    """
    GOES衛星のnetCDFファイルを読み込む

    Args:
        filepath: netCDFファイルのパス
        debug: デバッグ出力を表示するか

    Returns:
        GOESData構造体

    Raises:
        ImportError: netCDF4がインストールされていない場合
        FileNotFoundError: ファイルが見つからない場合
    """
    if not NETCDF_AVAILABLE:
        raise ImportError("netCDF4がインストールされていません。pip install netCDF4 を実行してください。")

    # netCDFファイルを開く
    nc = Dataset(filepath, 'r')

    try:
        # x座標のサイズを取得
        x_var = nc.variables['x']
        x_size = len(x_var)

        # y座標のサイズを取得
        y_var = nc.variables['y']
        y_size = len(y_var)

        if debug:
            print(f"x: {x_size}")
            print(f"y: {y_size}")

        # 放射輝度データを読み込む
        rad_var = nc.variables['Rad']
        rad_data = rad_var[:].data  # numpy配列として取得

        # スケールファクターとオフセット
        scale_factor = float(rad_var.scale_factor)
        add_offset = float(rad_var.add_offset)

        if debug:
            print("1")

        # Planck定数関連のパラメータを読み込む
        planck_fk1_var = nc.variables['planck_fk1']
        planck_fk1 = float(planck_fk1_var[:])

        if debug:
            print("2")

        planck_fk2_var = nc.variables['planck_fk2']
        planck_fk2 = float(planck_fk2_var[:])

        if debug:
            print("3")

        planck_bc1_var = nc.variables['planck_bc1']
        planck_bc1 = float(planck_bc1_var[:])

        if debug:
            print("4")

        planck_bc2_var = nc.variables['planck_bc2']
        planck_bc2 = float(planck_bc2_var[:])

        if debug:
            print("5")
            print(f"planck_fk1: {planck_fk1}")
            print(f"planck_fk2: {planck_fk2}")

        # バンド番号を取得（ファイル名から推測）
        # ファイル名の形式: OR_ABI-L1b-RadM1-M6C13_G16_...
        import os
        basename = os.path.basename(filepath)
        if 'C' in basename:
            # Cの後の数字を抽出
            c_pos = basename.index('C')
            band_str = basename[c_pos+1:c_pos+3]
            band = int(band_str)
        else:
            band = 0

        # GOESData構造体を作成
        goes_data = GOESData(
            x=x_size,
            y=y_size,
            band=band,
            scale_factor=scale_factor,
            add_offset=add_offset,
            planck_fk1=planck_fk1,
            planck_fk2=planck_fk2,
            planck_bc1=planck_bc1,
            planck_bc2=planck_bc2,
            data=rad_data.flatten()  # 1次元配列に変換
        )

    finally:
        nc.close()

    return goes_data
