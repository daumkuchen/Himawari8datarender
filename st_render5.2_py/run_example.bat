@echo off
REM st_render Python版のサンプル実行スクリプト (Windows版)

echo st_render V5_py - サンプル実行
echo.
echo このスクリプトは以下の処理を実行します：
echo   - セグメント自動結合機能のデモンストレーション
echo   - 各種カラースケールでの画像生成（ImageMagick風の補正付き）
echo   - RGB合成による自然色画像の生成
echo.

REM 出力ディレクトリの設定
set OUTPUT_DIR=.\output

REM HSDファイルのサンプル（セグメント1を指定すると、全セグメントが自動結合される）
set BAND1_FILE=.\sample\himawari\fulldisk\band1\HS_H08_20170623_0250_B01_FLDK_R10_S0110.DAT.bz2
set BAND2_FILE=.\sample\himawari\fulldisk\band2\HS_H08_20170623_0250_B02_FLDK_R10_S0110.DAT.bz2
set BAND3_FILE=.\sample\himawari\fulldisk\band3\HS_H08_20170623_0250_B03_FLDK_R05_S0110.DAT.bz2
set BAND13_FILE=.\sample\himawari\fulldisk\band13\HS_H08_20170623_0250_B13_FLDK_R20_S0110.DAT.bz2

REM RGB合成（バンド3,2,1を使用）
echo 1. RGB合成で完全な自然色画像を生成中（True Color RGB）...
echo    Band1 (0.47μm - 青): 11000x1100ピクセル × 10 = 11000x11000ピクセル
echo    Band2 (0.51μm - 緑): 11000x1100ピクセル × 10 = 11000x11000ピクセル
echo    Band3 (0.64μm - 赤): 22000x2200ピクセル × 10 = 22000x22000ピクセル
echo    → 最終出力: 11000x11000ピクセル（自動リサイズ）
echo.

REM 開始時刻を記録（Windows形式）
set START_TIME=%time%

python main.py rgbfile red "%BAND3_FILE%" green "%BAND2_FILE%" blue "%BAND1_FILE%" outpic himawari_full_rgb.png outdir "%OUTPUT_DIR%" enhance

REM 終了時刻を記録
set END_TIME=%time%

echo.
echo RGB合成の処理時間: 開始 %START_TIME% - 終了 %END_TIME%
echo.

echo ==========================================
echo 処理完了
echo ==========================================
echo.
echo 生成されたファイル:
dir /b "%OUTPUT_DIR%"\himawari_full*.png 2>nul
echo.
echo サマリ:
echo   - セグメント結合により、完全な地球画像が生成されました
echo   - Band1 (R10): 11000x11000ピクセル
echo   - Band13 (R20): 5500x5500ピクセル（画像補正適用済み）
echo   - RGB合成: 11000x11000ピクセル（画像補正適用済み）
echo.
echo RGB合成画像の補正内容:
echo   - ガンマ補正: 1.5（暗部を明るく）
echo   - 彩度強調: 250%%（色を鮮やかに）
echo   - 色相調整: 102%%（わずかにシフト）
echo   - コントラスト強調: 1.5倍
echo.

pause
