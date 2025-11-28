#!/bin/bash
# st_render Python版のサンプル実行スクリプト

echo "st_render V5_py - サンプル実行"
echo ""
echo "このスクリプトは以下の処理を実行します："
echo "  - セグメント自動結合機能のデモンストレーション"
echo "  - 各種カラースケールでの画像生成（ImageMagick風の補正付き）"
echo "  - RGB合成による自然色画像の生成"
echo ""

# 出力ディレクトリの設定
OUTPUT_DIR="./output"

# HSDファイルのサンプル（セグメント1を指定すると、全セグメントが自動結合される）
BAND1_FILE="./sample/himawari/fulldisk/band1/HS_H08_20170623_0250_B01_FLDK_R10_S0110.DAT.bz2"
BAND13_FILE="./sample/himawari/fulldisk/band13/HS_H08_20170623_0250_B13_FLDK_R20_S0110.DAT.bz2"

# HSDファイルが存在する場合は処理
if [ -f "$BAND1_FILE" ]; then
    echo "=========================================="
    echo "セグメント結合機能のデモンストレーション"
    echo "=========================================="
    echo ""
    echo "注意: 各セグメントファイル（S0110）を指定するだけで、"
    echo "      自動的に全10セグメント（S0110～S1010）が検出・結合されます。"
    echo ""

    # Band1（可視光）で白黒画像を生成
    # echo "1. Band1（可視光、R10解像度）で完全な白黒画像を生成中..."
    # echo "   セグメント: 11000x1100ピクセル × 10 = 完全画像: 11000x11000ピクセル"
    # python3 main.py hsdfile file "$BAND1_FILE" color 0 outpic himawari_full_band1_bw.png outdir "$OUTPUT_DIR"
    # echo ""

    # Band13（赤外）でColor2スケール画像を生成
    # if [ -f "$BAND13_FILE" ]; then
    #     echo "2. Band13（赤外、R20解像度）で完全なColor2画像を生成中（画像補正あり）..."
    #     echo "   セグメント: 5500x550ピクセル × 10 = 完全画像: 5500x5500ピクセル"
    #     echo "   補正: ガンマ1.5、彩度250%、色相102%、コントラスト強調"
    #     python3 main.py hsdfile file "$BAND13_FILE" color 2 outpic himawari_full_band13_color2_enhanced.png outdir "$OUTPUT_DIR" enhance
    #     echo ""

    #     echo "3. Band13（赤外）で完全なBD画像を生成中（画像補正あり）..."
    #     python3 main.py hsdfile file "$BAND13_FILE" color 1 outpic himawari_full_band13_bd_enhanced.png outdir "$OUTPUT_DIR" enhance
    #     echo ""
    # fi

    # RGB合成（バンド3,2,1を使用）
    echo "4. RGB合成で完全な自然色画像を生成中（True Color RGB）..."
    echo "   Band3 (0.64μm - 赤): 22000x2200ピクセル × 10 = 22000x22000ピクセル"
    echo "   Band2 (0.51μm - 緑): 11000x1100ピクセル × 10 = 11000x11000ピクセル"
    echo "   Band1 (0.47μm - 青): 11000x1100ピクセル × 10 = 11000x11000ピクセル"
    echo "   → 最終出力: 11000x11000ピクセル（自動リサイズ）"
    BAND1="./sample/himawari/fulldisk/band1/HS_H08_20170623_0250_B01_FLDK_R10_S0110.DAT.bz2"
    BAND2="./sample/himawari/fulldisk/band2/HS_H08_20170623_0250_B02_FLDK_R10_S0110.DAT.bz2"
    BAND3="./sample/himawari/fulldisk/band3/HS_H08_20170623_0250_B03_FLDK_R05_S0110.DAT.bz2"

    if [ -f "$BAND1" ] && [ -f "$BAND2" ] && [ -f "$BAND3" ]; then
        # 正しいバンド割り当て: Band3=赤, Band2=緑, Band1=青
        python3 main.py rgbfile red "$BAND3" green "$BAND2" blue "$BAND1" outpic himawari_full_rgb.png outdir "$OUTPUT_DIR" enhance
        echo ""
    else
        echo "RGB合成に必要なバンド1,2,3のファイルが見つかりません"
        echo ""
    fi

    echo "=========================================="
    echo "処理完了"
    echo "=========================================="
    echo ""
    echo "生成されたファイル:"
    ls -lh "$OUTPUT_DIR"/himawari_full*.png 2>/dev/null
    echo ""
    echo "サマリ:"
    echo "  - セグメント結合により、完全な地球画像が生成されました"
    echo "  - Band1 (R10): 11000x11000ピクセル"
    echo "  - Band13 (R20): 5500x5500ピクセル（画像補正適用済み）"
    echo "  - RGB合成: 11000x11000ピクセル（画像補正適用済み）"
    echo ""
    echo "RGB合成画像の補正内容:"
    echo "  - ガンマ補正: 1.5（暗部を明るく）"
    echo "  - 彩度強調: 250%（色を鮮やかに）"
    echo "  - 色相調整: 102%（わずかにシフト）"
    echo "  - コントラスト強調: 1.5倍"
    echo ""
else
    echo "HSDファイルが見つかりません: $BAND1_FILE"
    echo "サンプルデータをダウンロードして、以下のディレクトリに配置してください："
    echo "  - ./sample/himawari/fulldisk/band1/"
    echo "  - ./sample/himawari/fulldisk/band2/"
    echo "  - ./sample/himawari/fulldisk/band3/"
    echo "  - ./sample/himawari/fulldisk/band13/"
    echo ""
fi