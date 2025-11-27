# st_render V5_py - Himawari/GOES衛星データ可視化ツール (Python版)

Himawari8/9の標準データ(HSD)およびGOES16-18のL1b netCDFファイルをPNG画像に変換するPythonプログラムです。

C++版（st_render5.2_cpp）からPythonに移植されました。

## 特徴

- Himawari8/9のHSD形式データに対応
- GOES16-18のL1b netCDF形式データに対応
- bz2圧縮ファイルの自動解凍
- **複数セグメントの自動結合** - 10分割されたセグメントファイルを自動検出・結合して完全な画像を生成
- 複数のカラースケールに対応（白黒、BD、Color2、水蒸気）
- 放射輝度から輝度温度への校正処理
- RGB合成機能（異なる解像度のバンド間での自動リサイズ対応）

## 必要な環境

- Python 3.7以上
- 必要なライブラリ:
  - numpy
  - Pillow
  - netCDF4 (GOES衛星データを処理する場合)

## インストール

```bash
# 依存ライブラリのインストール
pip install -r requirements.txt
```

または、個別にインストール:

```bash
pip install numpy Pillow netCDF4
```

## 使用方法

### 基本的な使用方法

#### HSDファイルの場合

```bash
python main.py hsdfile file <ファイル名> color <カラースケール> [outpic <出力ファイル名>] [outdir <出力ディレクトリ>]
```

例:
```bash
# 基本的な使用（カレントディレクトリに出力）
python main.py hsdfile file HS_H09_20250321_0810_B13_R302_R20_S0101.DAT.bz2 color 2

# 出力ディレクトリを指定
python main.py hsdfile file HS_H09_20250321_0810_B13_R302_R20_S0101.DAT.bz2 color 2 outdir ./output

# 出力ファイル名を指定
python main.py hsdfile file HS_H09_20250321_0810_B13_R302_R20_S0101.DAT.bz2 color 1 outpic himawari_bd.png

# 出力ファイル名とディレクトリの両方を指定
python main.py hsdfile file HS_H09_20250321_0810_B13_R302_R20_S0101.DAT.bz2 color 1 outpic result.png outdir ./images
```

#### GOES netCDFファイルの場合

```bash
python main.py goesncfile file <ファイル名> color <カラースケール> [outpic <出力ファイル名>] [outdir <出力ディレクトリ>]
```

例:
```bash
# 基本的な使用
python main.py goesncfile file OR_ABI-L1b-RadM1-M6C13_G16_s20192440901238_e20192440901307_c20192440901338.nc color 2

# 出力ディレクトリを指定
python main.py goesncfile file OR_ABI-L1b-RadM1-M6C13_G16_s20192440901238_e20192440901307_c20192440901338.nc color 2 outdir ./output
```

#### RGB合成の場合

```bash
python main.py rgbfile red <赤チャンネルファイル> green <緑チャンネルファイル> blue <青チャンネルファイル> [outpic <出力ファイル名>] [outdir <出力ディレクトリ>] [gamma <ガンマ値>]
```

例:
```bash
# バンド4(赤)、バンド2(緑)、バンド1(青)を使用したNatural Color RGB合成
python main.py rgbfile red band4.bz2 green band2.bz2 blue band1.bz2 outpic rgb.png outdir ./output

# ガンマ補正値を指定
python main.py rgbfile red band4.bz2 green band2.bz2 blue band1.bz2 outpic rgb.png outdir ./output gamma 2.5
```

**注意**: Himawari-8/9の場合、True Color RGBにはバンド3(赤)が推奨されますが、バンド3が利用できない場合はバンド4(近赤外)を赤チャンネルとして使用できます。

### セグメント結合機能

Himawari8/9のフルディスクデータは通常10個のセグメント（S0110～S1010）に分割されています。このプログラムは**自動的に**全セグメントを検出・結合して完全な画像を生成します。

#### 動作の仕組み

1つのセグメントファイル（例：`HS_H08_20170623_0250_B01_FLDK_R10_S0110.DAT.bz2`）を指定すると：

1. ファイル名からセグメント番号を解析
2. 同じ時刻・バンドの他のセグメント（S0210～S1010）を自動検索
3. 全10セグメントを縦に結合して完全な画像を生成

#### 例

```bash
# セグメント1つを指定するだけで、全セグメントが自動結合される
python main.py hsdfile file HS_H08_20170623_0250_B01_FLDK_R10_S0110.DAT.bz2 color 2 outdir ./output

# 結果: 11000x11000ピクセルの完全な画像が生成される（セグメント単体は11000x1100）
```

#### 解像度による違い

- **R10 (1km解像度)**: 11000x1100ピクセル/セグメント → 11000x11000ピクセル (結合後)
- **R05 (0.5km解像度)**: 22000x2200ピクセル/セグメント → 22000x22000ピクセル (結合後)
- **R20 (2km解像度)**: 5500x550ピクセル/セグメント → 5500x5500ピクセル (結合後)

**RGB合成での注意**: 異なる解像度のバンドを使用した場合、自動的に最小サイズに合わせてリサイズされます。

### パラメータ

#### カラースケール

- `0`: 白黒スケール
- `1`: BDスケール
- `2`: Color2スケール
- `3`: 水蒸気スケール (WVNRL)

#### オプション

- `outpic <ファイル名>`: 出力ファイル名を指定（省略時は「入力ファイル名.png」またはRGB合成の場合は「rgb_composite.png」）
- `outdir <ディレクトリ>`: 出力ディレクトリを指定（省略時はカレントディレクトリ）
  - 指定したディレクトリが存在しない場合は自動的に作成されます
  - `outpic`と`outdir`の両方を指定した場合、`outdir`に`outpic`で指定したファイル名で保存されます
- `gamma <値>`: ガンマ補正値を指定（RGB合成のみ、省略時は2.2）
  - 値が大きいほど明るい画像になります
  - 推奨値: 1.8〜2.5

## データソース

### Himawari8/9データ

- [NOAA Himawari8 on AWS](https://registry.opendata.aws/noaa-himawari/)
- Browse bucket から必要なHSDファイルをダウンロード
- `.bz2` 形式でも `.DAT` 形式でも使用可能

### GOES16-18データ

- [NOAA GOES on AWS](https://registry.opendata.aws/noaa-goes/)
- Browse bucket から必要なL1b netCDFファイル (`.nc`) をダウンロード

## プログラムの構造

```
st_render5.2_py/
├── __init__.py           # パッケージ初期化
├── main.py               # メインプログラム
├── hsd_reader.py         # HSDファイル読み込み
├── goes_reader.py        # GOES netCDFファイル読み込み
├── segment_merger.py     # セグメント結合機能
├── rgb_composite.py      # RGB合成機能
├── calibration.py        # データ校正（放射輝度→輝度温度）
├── colorscale.py         # カラースケール変換
├── requirements.txt      # 依存ライブラリ
├── run_example.sh        # サンプル実行スクリプト
└── README.md             # このファイル
```

## Pythonモジュールとしての使用

このプログラムはPythonモジュールとしても使用できます:

```python
from st_render5.2_py import hsd_read, hsd_calibration, bd_scale
from PIL import Image

# HSDファイルを読み込む
hs_data = hsd_read("HS_H09_20250321_0810_B13_R302_R20_S0101.DAT.bz2")

# 校正を実行
hsd_calibration(hs_data)

# カラースケール変換
pixels = bd_scale(hs_data.temp)

# 画像として保存
img_array = pixels.reshape(hs_data.height, hs_data.width, 3)
img = Image.fromarray(img_array, 'RGB')
img.save("output.png")
```

## C++版との違い

- Python標準ライブラリの`bz2`モジュールを使用（7zipは不要）
- numpyの配列操作による高速化
- Pillowを使用したPNG出力
- netCDF4-pythonを使用したnetCDFファイル読み込み
- **複数セグメントの自動結合機能** - ファイル名から自動的にセグメントを検出・結合

## ライセンス

C++版のst_render5と同様のライセンスに従います。

## 謝辞

- 元のC++版: @linsanyi031
- lodepng: PNG画像処理ライブラリ
- netCDF4: netCDFファイル読み込みライブラリ
- numpy, Pillow: Python科学計算・画像処理ライブラリ

## 注意事項

- bz2圧縮ファイルを処理する場合、解凍後のDATファイルが作業ディレクトリに保存されます
- 大きなファイルを処理する場合、十分なメモリが必要です
  - 単一セグメント（11000x1100ピクセル）: 約100MB
  - 完全な画像（11000x11000ピクセル）: 約500MB～1GB
- 出力ファイル名を指定する際は、既存のファイルを上書きしないよう注意してください
- セグメント結合処理には時間がかかります（10セグメントで2～5分程度）
