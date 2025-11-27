#!/usr/bin/env python3
"""
st_render - Himawari/GOES衛星データ可視化ツール (Python版)

Himawari8/9の標準データ(HSD)およびGOES16-18のL1b netCDFファイルを
PNG画像に変換するプログラム
"""
import sys
import os
import argparse
import time
import numpy as np
from PIL import Image

from hsd_reader import hsd_read
from goes_reader import goes_read
from calibration import hsd_calibration, goes_calibration
from colorscale import bw_scale, bd_scale, color2_scale, wvnrl_scale
from rgb_composite import create_rgb_composite, create_natural_color_rgb


def get_output_path(input_filepath: str, output_path: str = None, output_dir: str = None) -> str:
    """
    出力ファイルパスを生成

    Args:
        input_filepath: 入力ファイルのパス
        output_path: 出力ファイル名（指定された場合）
        output_dir: 出力ディレクトリ（指定された場合）

    Returns:
        出力ファイルの絶対パス
    """
    if output_path:
        # output_pathが指定されている場合
        if output_dir:
            # output_dirも指定されている場合は、output_dirに保存
            basename = os.path.basename(output_path)
            final_path = os.path.join(output_dir, basename)
        else:
            # output_pathのみ指定の場合はそのまま使用
            final_path = output_path
    else:
        # output_pathが指定されていない場合、入力ファイル名から生成
        basename = os.path.basename(input_filepath) + ".png"
        if output_dir:
            final_path = os.path.join(output_dir, basename)
        else:
            final_path = input_filepath + ".png"

    # 出力ディレクトリが存在しない場合は作成
    output_directory = os.path.dirname(final_path)
    if output_directory and not os.path.exists(output_directory):
        os.makedirs(output_directory, exist_ok=True)
        print(f"出力ディレクトリを作成しました: {output_directory}")

    return final_path


def hsd_render(filepath: str, color: int, output_path: str = None, output_dir: str = None, delete_dat: bool = False):
    """
    HSDファイルをレンダリング

    Args:
        filepath: HSDファイルのパス
        color: カラースケール (0: 白黒, 1: BD, 2: Color2, 3: 水蒸気)
        output_path: 出力ファイル名 (Noneの場合は自動生成)
        output_dir: 出力ディレクトリ (指定された場合、このディレクトリに保存)
        delete_dat: 処理後にDATファイルを削除するか
    """
    print(f"HSDファイルを処理中: {filepath}")

    # 出力ファイルパスの決定
    output_path = get_output_path(filepath, output_path, output_dir)

    # HSDファイルを読み込む
    hs_data = hsd_read(filepath, delete_dat=delete_dat, debug=True)

    print(f"衛星: {hs_data.satellite_name}")
    print(f"サイズ: {hs_data.width}x{hs_data.height}")
    print(f"バンド: {hs_data.band}")

    # 画像データを生成
    if hs_data.band > 3:
        # 赤外バンドの場合は校正を実行
        print("データ校正中...")
        hsd_calibration(hs_data, debug=True)

        print("hsdRenderdbg1")

        # カラースケール変換
        if color == 1:
            pixels = bd_scale(hs_data.temp)
        elif color == 2:
            pixels = color2_scale(hs_data.temp)
        elif color == 3:
            pixels = wvnrl_scale(hs_data.temp)
        else:
            pixels = bw_scale(hs_data.data, hs_data.bit_num)
    else:
        # 可視光バンドの場合は白黒スケールのみ
        pixels = bw_scale(hs_data.data, hs_data.bit_num)

    print(f"hsdRenderdbg2\n{output_path}")

    # 画像を保存
    # データを2次元に変形
    img_array = pixels.reshape(hs_data.height, hs_data.width, 3)
    img = Image.fromarray(img_array)
    img.save(output_path)

    print(f"hsdRenderdbg3")
    print(f"画像を保存しました: {output_path}")


def goes_render(filepath: str, color: int, output_path: str = None, output_dir: str = None):
    """
    GOES netCDFファイルをレンダリング

    Args:
        filepath: netCDFファイルのパス
        color: カラースケール (0: 白黒, 1: BD, 2: Color2, 3: 水蒸気)
        output_path: 出力ファイル名 (Noneの場合は自動生成)
        output_dir: 出力ディレクトリ (指定された場合、このディレクトリに保存)
    """
    print(f"GOES netCDFファイルを処理中: {filepath}")

    # 出力ファイルパスの決定
    output_path = get_output_path(filepath, output_path, output_dir)

    # GOES netCDFファイルを読み込む
    goes_data = goes_read(filepath, debug=True)

    print(f"サイズ: {goes_data.x}x{goes_data.y}")
    print(f"バンド: {goes_data.band}")

    # データ校正
    print("データ校正中...")
    goes_calibration(goes_data, debug=True)

    print(f"planck_fk1: {goes_data.planck_fk1}")
    print(f"data[0]: {goes_data.data[0]}")
    print(f"temp[0]: {goes_data.temp[0]}")

    # カラースケール変換
    if color == 1:
        pixels = bd_scale(goes_data.temp)
    elif color == 2:
        pixels = color2_scale(goes_data.temp)
    elif color == 3:
        pixels = wvnrl_scale(goes_data.temp)
    else:
        pixels = bw_scale(goes_data.data, 14)  # GOES-Rは14ビット

    # 画像を保存
    # データを2次元に変形
    img_array = pixels.reshape(goes_data.y, goes_data.x, 3)
    img = Image.fromarray(img_array)
    img.save(output_path)

    print(f"画像を保存しました: {output_path}")


def show_help():
    """ヘルプを表示"""
    help_text = """
st_render V5_py - Himawari/GOES衛星データ可視化ツール (Python版)

使用方法:
    HSDファイルの場合:
        python main.py hsdfile file <ファイル名> color <カラースケール> [outpic <出力ファイル名>] [outdir <出力ディレクトリ>]

    GOES netCDFファイルの場合:
        python main.py goesncfile file <ファイル名> color <カラースケール> [outpic <出力ファイル名>] [outdir <出力ディレクトリ>]

    RGB合成の場合:
        python main.py rgbfile red <赤ファイル> green <緑ファイル> blue <青ファイル> [outpic <出力ファイル名>] [outdir <出力ディレクトリ>] [gamma <ガンマ値>]

カラースケール:
    0: 白黒
    1: BD
    2: Color2
    3: 水蒸気 (WVNRL)

オプション:
    outpic: 出力ファイル名を指定（省略時は入力ファイル名.png）
    outdir: 出力ディレクトリを指定（省略時はカレントディレクトリ）
    gamma: ガンマ補正値を指定（RGB合成のみ、省略時は2.2）

例:
    # 基本的な使用方法
    python main.py hsdfile file HS_H09_20250321_0810_B13_R302_R20_S0101.DAT.bz2 color 2

    # 出力ファイル名を指定
    python main.py goesncfile file OR_ABI-L1b-RadM1-M6C13_G16_s20192440901238_e20192440901307_c20192440901338.nc color 2 outpic output.png

    # 出力ディレクトリを指定
    python main.py hsdfile file HS_H09_20250321_0810_B13_R302_R20_S0101.DAT.bz2 color 2 outdir ./output

    # RGB合成（バンド1、2、4を使用）
    python main.py rgbfile red band4.bz2 green band2.bz2 blue band1.bz2 outpic rgb.png outdir ./output
"""
    print(help_text)


def main():
    """メイン関数"""
    print("st_render V5_py")

    # 引数が少ない場合はヘルプを表示
    if len(sys.argv) <= 2:
        show_help()
        return 0

    # 引数をパース
    args = {}
    op = None
    i = 1

    while i < len(sys.argv):
        arg = sys.argv[i]

        if arg == "hsdfile":
            op = "hsd"
        elif arg == "goesncfile":
            op = "goes"
        elif arg == "rgbfile":
            op = "rgb"
        elif arg == "file" and i + 1 < len(sys.argv):
            i += 1
            args['file'] = sys.argv[i]
        elif arg == "red" and i + 1 < len(sys.argv):
            i += 1
            args['red'] = sys.argv[i]
        elif arg == "green" and i + 1 < len(sys.argv):
            i += 1
            args['green'] = sys.argv[i]
        elif arg == "blue" and i + 1 < len(sys.argv):
            i += 1
            args['blue'] = sys.argv[i]
        elif arg == "color" and i + 1 < len(sys.argv):
            i += 1
            args['color'] = int(sys.argv[i])
        elif arg == "outpic" and i + 1 < len(sys.argv):
            i += 1
            args['outpic'] = sys.argv[i]
        elif arg == "outdir" and i + 1 < len(sys.argv):
            i += 1
            args['outdir'] = sys.argv[i]
        elif arg == "gamma" and i + 1 < len(sys.argv):
            i += 1
            args['gamma'] = float(sys.argv[i])

        i += 1

    # 必須引数のチェック
    if op is None:
        print("エラー: コマンドが指定されていません")
        show_help()
        return 1

    if op == "rgb":
        if 'red' not in args or 'green' not in args or 'blue' not in args:
            print("エラー: RGB合成には red, green, blue ファイルが必要です")
            show_help()
            return 1
    else:
        if 'file' not in args or 'color' not in args:
            print("エラー: 必須引数が不足しています")
            show_help()
            return 1

    # 処理開始
    start_time = time.time()

    try:
        if op == "hsd":
            hsd_render(
                args['file'],
                args['color'],
                args.get('outpic', None),
                args.get('outdir', None),
                delete_dat=False
            )
        elif op == "goes":
            goes_render(
                args['file'],
                args['color'],
                args.get('outpic', None),
                args.get('outdir', None)
            )
        elif op == "rgb":
            # 出力ファイル名の決定
            output_path = args.get('outpic', 'rgb_composite.png')
            if args.get('outdir'):
                output_path = os.path.join(args['outdir'], os.path.basename(output_path))

            # RGB合成を実行
            create_rgb_composite(
                red_file=args['red'],
                green_file=args['green'],
                blue_file=args['blue'],
                output_path=output_path,
                gamma=args.get('gamma', 2.2),
                delete_dat=False
            )
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # 処理時間を表示
    elapsed_time = time.time() - start_time
    print(f"処理時間: {elapsed_time:.2f} 秒")

    return 0


if __name__ == "__main__":
    sys.exit(main())
