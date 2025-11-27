"""
セグメント結合モジュール
HSDファイルの複数セグメントを結合して完全な画像を生成
"""
import numpy as np
import os
import re
from typing import List, Tuple, Optional
from pathlib import Path

from hsd_reader import hsd_read, HSData


def parse_segment_number(filepath: str) -> Optional[int]:
    """
    ファイルパスからセグメント番号を抽出

    Args:
        filepath: HSDファイルのパス

    Returns:
        セグメント番号 (1-10)、見つからない場合はNone

    Example:
        HS_H08_20170623_0250_B01_FLDK_R10_S0110.DAT.bz2 -> 1
        HS_H08_20170623_0250_B01_FLDK_R10_S1010.DAT.bz2 -> 10
    """
    # ファイル名からセグメント番号を抽出 (S0110, S0210, ..., S1010)
    match = re.search(r'_S(\d{2})10', filepath)
    if match:
        return int(match.group(1))
    return None


def find_all_segments(filepath: str) -> List[str]:
    """
    指定されたファイルと同じ時刻・バンドの全セグメントを検索

    Args:
        filepath: 基準となるHSDファイルのパス

    Returns:
        全セグメントのパスのリスト（セグメント番号順）
    """
    # ファイル名からセグメント番号部分以外を抽出
    base_pattern = re.sub(r'_S\d{4}', '_S{:02d}10', filepath)

    directory = os.path.dirname(filepath)
    segments = []

    # セグメント1-10を検索
    for seg_num in range(1, 11):
        segment_path = base_pattern.format(seg_num)

        # .bz2と.DATの両方をチェック
        if os.path.exists(segment_path):
            segments.append(segment_path)
        elif segment_path.endswith('.bz2'):
            # .bz2が見つからない場合、.DATをチェック
            dat_path = segment_path[:-4]  # .bz2を除去
            if os.path.exists(dat_path):
                segments.append(dat_path)

    return segments


def merge_segments(segment_files: List[str], delete_dat: bool = False, debug: bool = False) -> HSData:
    """
    複数のセグメントを結合して1つのHSDataオブジェクトを生成

    Args:
        segment_files: セグメントファイルのパスリスト（順序付き）
        delete_dat: 処理後にDATファイルを削除するか
        debug: デバッグ情報を出力するか

    Returns:
        結合されたHSDataオブジェクト
    """
    if not segment_files:
        raise ValueError("セグメントファイルが指定されていません")

    if debug:
        print(f"セグメント結合を開始します（{len(segment_files)}個のセグメント）")

    # 各セグメントを読み込む
    segments_data = []
    total_height = 0
    width = None

    for i, seg_file in enumerate(segment_files, 1):
        if debug:
            print(f"セグメント{i}/{len(segment_files)}を読み込み中: {os.path.basename(seg_file)}")

        seg_data = hsd_read(seg_file, delete_dat=delete_dat, debug=False)
        segments_data.append(seg_data)

        # 幅の整合性チェック
        if width is None:
            width = seg_data.width
        elif width != seg_data.width:
            raise ValueError(f"セグメント{i}の幅が一致しません: {seg_data.width} != {width}")

        total_height += seg_data.height

        if debug:
            print(f"  サイズ: {seg_data.width}x{seg_data.height}")

    if debug:
        print(f"結合後の画像サイズ: {width}x{total_height}")

    # データを縦に結合
    merged_data = np.concatenate([seg.data for seg in segments_data])

    # 最初のセグメントのメタデータをベースに結合データを作成
    base_segment = segments_data[0]

    # 結合されたHSDataオブジェクトを作成
    merged_hs_data = HSData(
        satellite_name=base_segment.satellite_name,
        width=width,
        height=total_height,
        band=base_segment.band,
        wavelength=base_segment.wavelength,
        bit_num=base_segment.bit_num,
        slope=base_segment.slope,
        intc=base_segment.intc,
        c0=base_segment.c0,
        c1=base_segment.c1,
        c2=base_segment.c2,
        c=base_segment.c,
        H=base_segment.H,
        k=base_segment.k,
        data=merged_data
    )

    if debug:
        print("セグメント結合が完了しました")

    return merged_hs_data


def read_hsd_full(filepath: str, delete_dat: bool = False, debug: bool = False,
                  auto_merge: bool = True) -> HSData:
    """
    HSDファイルを読み込み、必要に応じてセグメントを自動結合

    Args:
        filepath: HSDファイルのパス
        delete_dat: 処理後にDATファイルを削除するか
        debug: デバッグ情報を出力するか
        auto_merge: 自動的にセグメントを検索・結合するか

    Returns:
        HSDataオブジェクト（auto_mergeがTrueの場合は結合済み）
    """
    if not auto_merge:
        # セグメント結合なしで単一ファイルを読み込む
        return hsd_read(filepath, delete_dat=delete_dat, debug=debug)

    # セグメント番号を確認
    seg_num = parse_segment_number(filepath)

    if seg_num is None:
        # セグメント番号が見つからない場合は単一ファイルとして処理
        if debug:
            print("セグメント番号が見つかりません。単一ファイルとして処理します。")
        return hsd_read(filepath, delete_dat=delete_dat, debug=debug)

    # 全セグメントを検索
    all_segments = find_all_segments(filepath)

    if len(all_segments) == 0:
        # セグメントが見つからない場合は単一ファイルとして処理
        if debug:
            print("他のセグメントが見つかりません。単一ファイルとして処理します。")
        return hsd_read(filepath, delete_dat=delete_dat, debug=debug)

    if len(all_segments) == 1:
        # セグメントが1つしかない場合
        if debug:
            print("セグメントは1つのみです。")
        return hsd_read(filepath, delete_dat=delete_dat, debug=debug)

    # 複数セグメントを結合
    if debug:
        print(f"{len(all_segments)}個のセグメントが見つかりました。結合を開始します。")

    return merge_segments(all_segments, delete_dat=delete_dat, debug=debug)
