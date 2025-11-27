#!/bin/bash
# st_render Python版のサンプル実行スクリプト

echo "st_render V5_py - サンプル実行"
echo ""

# 出力ディレクトリの設定
OUTPUT_DIR="./output"

# HSDファイルのサンプル
# 実際に使用する際は、ファイル名を変更してください
HSD_FILE="./sample/himawari/fulldisk/band1/HS_H08_20170623_0250_B01_FLDK_R10_S0110.DAT.bz2"

# HSDファイルが存在する場合は処理
if [ -f "$HSD_FILE" ]; then
    echo "=== HSDファイルを処理中: $HSD_FILE ==="
    echo ""

    # Color2スケールで処理（出力ディレクトリ指定）
    echo "1. Color2スケールで処理中..."
    python3 main.py hsdfile file "$HSD_FILE" color 2 outpic himawari_1_color2.png outdir "$OUTPUT_DIR"
    echo ""

    # BDスケールで処理
    echo "2. BDスケールで処理中..."
    python3 main.py hsdfile file "$HSD_FILE" color 1 outpic himawari_2_bd.png outdir "$OUTPUT_DIR"
    echo ""

    # 白黒スケールで処理
    echo "3. 白黒スケールで処理中..."
    python3 main.py hsdfile file "$HSD_FILE" color 0 outpic himawari_3_bw.png outdir "$OUTPUT_DIR"
    echo ""

    # RGB合成（バンド1、2、4を使用）
    echo "4. RGB合成で処理中（バンド4,2,1）..."
    BAND1="./sample/himawari/fulldisk/band1/HS_H08_20170623_0250_B01_FLDK_R10_S0110.DAT.bz2"
    BAND2="./sample/himawari/fulldisk/band2/HS_H08_20170623_0250_B02_FLDK_R10_S0110.DAT.bz2"
    BAND3="./sample/himawari/fulldisk/band3/HS_H08_20170623_0250_B03_FLDK_R05_S0110.DAT.bz2"

    if [ -f "$BAND1" ] && [ -f "$BAND2" ] && [ -f "$BAND3" ]; then
        python3 main.py rgbfile red "$BAND3" green "$BAND2" blue "$BAND1" outpic himawari_4_rgb.png outdir "$OUTPUT_DIR"
        echo ""
    else
        echo "RGB合成に必要なバンド1,2,4のファイルが見つかりません"
        echo ""
    fi

    echo "=== 処理完了 ==="
    echo "生成されたファイル:"
    ls -lh "$OUTPUT_DIR"/*.png 2>/dev/null
    echo ""
else
    echo "HSDファイルが見つかりません: $HSD_FILE"
    echo "ファイルをダウンロードして、このスクリプトと同じディレクトリに配置してください。"
    echo ""
fi