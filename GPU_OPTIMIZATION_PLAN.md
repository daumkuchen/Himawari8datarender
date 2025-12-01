# Himawari-8 RGB画像生成 GPU高速化プラン

## 現状分析

### 処理時間の内訳（合計: 88秒）
- **画像補正処理**: 55-75秒
  - 色相調整（HSV色空間変換）: 30-40秒
  - ガンマ補正（べき乗計算）: 15-20秒
  - PIL ImageEnhance処理: 10-15秒
- **その他の処理**: 13-33秒
  - 画像読み込み、リサイズ、保存など

### ボトルネック
1. **HSV色空間変換** (RGB→HSV→RGB): 11000×11000ピクセル = 1.21億ピクセルに対する2回の変換
2. **ガンマ補正のべき乗演算**: 3.63億回のべき乗計算
3. **PIL ImageEnhance**: CPU実装のため低速

---

## GPU高速化戦略

### アプローチ1: CuPy による高速化（推奨）

#### 概要
- NumPy互換のGPUアクセラレーション
- 既存コードの変更が最小限
- CUDA環境があれば即座に利用可能

#### 実装箇所

##### 1. ガンマ補正の高速化
**ファイル**: `st_render5.2_py/image_enhance.py:45-46`

```python
# 現在の実装（CPU）
if gamma != 1.0:
    result = np.power(result, 1.0 / gamma)

# GPU実装（CuPy）
import cupy as cp

if gamma != 1.0:
    result_gpu = cp.asarray(result)
    result_gpu = cp.power(result_gpu, 1.0 / gamma)
    result = cp.asnumpy(result_gpu)
```

**期待効果**: 15-20秒 → 1-2秒（**10-15秒短縮**）

##### 2. HSV色空間変換の高速化
**ファイル**: `st_render5.2_py/image_enhance.py:106-115`

```python
# 現在の実装（OpenCV CPU）
hsv = cv2.cvtColor(img_array_temp, cv2.COLOR_RGB2HSV).astype(np.float32)
hue_shift = ((hue - 100.0) / 100.0) * 180.0
hsv[:, :, 0] = (hsv[:, :, 0] + hue_shift) % 180
img_array_temp = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)

# GPU実装（CuPy + OpenCV CUDA）
import cv2.cuda as cv2cuda

# GPU上で処理
gpu_img = cv2cuda.GpuMat()
gpu_img.upload(img_array_temp)
gpu_hsv = cv2cuda.cvtColor(gpu_img, cv2.COLOR_RGB2HSV)
hsv = gpu_hsv.download().astype(np.float32)

# 色相シフト（CuPyで高速化）
hsv_gpu = cp.asarray(hsv)
hue_shift = ((hue - 100.0) / 100.0) * 180.0
hsv_gpu[:, :, 0] = (hsv_gpu[:, :, 0] + hue_shift) % 180
hsv = cp.asnumpy(hsv_gpu).astype(np.uint8)

# GPU上でRGBに戻す
gpu_hsv.upload(hsv)
gpu_rgb = cv2cuda.cvtColor(gpu_hsv, cv2.COLOR_HSV2RGB)
img_array_temp = gpu_rgb.download()
```

**期待効果**: 30-40秒 → 2-3秒（**27-37秒短縮**）

##### 3. 彩度・コントラスト強調の高速化
**ファイル**: `st_render5.2_py/image_enhance.py:85-88, 150-151`

```python
# PIL ImageEnhanceをCuPyで実装
import cupy as cp

def apply_saturation_gpu(img_array, saturation_factor):
    """GPU上で彩度調整"""
    img_gpu = cp.asarray(img_array, dtype=cp.float32) / 255.0

    # RGB to grayscale (luminance)
    gray = 0.299 * img_gpu[:,:,0] + 0.587 * img_gpu[:,:,1] + 0.114 * img_gpu[:,:,2]
    gray = cp.stack([gray, gray, gray], axis=2)

    # Blend original with grayscale
    result = gray + saturation_factor * (img_gpu - gray)
    result = cp.clip(result * 255, 0, 255).astype(cp.uint8)

    return cp.asnumpy(result)

def apply_contrast_gpu(img_array, enhance_factor):
    """GPU上でコントラスト調整"""
    img_gpu = cp.asarray(img_array, dtype=cp.float32) / 255.0

    # Mean value
    mean = cp.mean(img_gpu)

    # Enhance contrast
    result = mean + enhance_factor * (img_gpu - mean)
    result = cp.clip(result * 255, 0, 255).astype(cp.uint8)

    return cp.asnumpy(result)
```

**期待効果**: 10-15秒 → 1-2秒（**8-13秒短縮**）

---

### アプローチ2: OpenCV CUDA モジュール

#### 概要
- OpenCVのCUDAバックエンドを使用
- cv2.cuda.GpuMatで画像をGPUメモリに配置
- リサイズ、色空間変換をGPU上で実行

#### 実装箇所

##### リサイズ処理の高速化
**ファイル**: `st_render5.2_py/rgb_composite.py`

```python
# 現在の実装（OpenCV CPU）
red_img = cv2.resize(red_img, (target_width, target_height), interpolation=cv2.INTER_AREA)

# GPU実装
import cv2.cuda as cv2cuda

gpu_img = cv2cuda.GpuMat()
gpu_img.upload(red_img)
gpu_resized = cv2cuda.resize(gpu_img, (target_width, target_height), interpolation=cv2.INTER_AREA)
red_img = gpu_resized.download()
```

**期待効果**: わずかな高速化（数秒程度）

---

### アプローチ3: 簡易最適化（色相調整スキップ）

#### 概要
- GPU環境不要
- コード修正が最小限
- `hue=102.0` → `hue=100.0` に変更してHSV変換をスキップ

#### 実装

**ファイル**: `st_render5.2_py/rgb_composite.py:139`（apply_imagemagick_enhance呼び出し部分）

```python
# 現在
img_array_enhanced = apply_imagemagick_enhance(img_array)

# 色相調整なし版
img_array_enhanced = apply_imagemagick_enhance(
    img_array,
    modulate_hue=100.0  # 102.0 → 100.0 に変更
)
```

**期待効果**: 88秒 → 48-58秒（**30-40秒短縮**）

---

## 推奨実装プラン

### フェーズ1: CuPy導入（最優先）

**必要な環境**
```bash
pip install cupy-cuda12x  # CUDA 12.x の場合
# または
pip install cupy-cuda11x  # CUDA 11.x の場合
```

**実装手順**
1. `image_enhance.py` にCuPy判定処理を追加
2. ガンマ補正をCuPy実装に置き換え
3. 彩度・コントラスト調整をCuPy実装に追加
4. HSV色空間変換にCuPy統合

**期待される総処理時間**: 88秒 → **20-30秒**（約3倍高速化）

---

### フェーズ2: OpenCV CUDA統合（オプション）

**必要な環境**
- CUDA対応版OpenCV（ソースからビルド必要）
```bash
# OpenCV with CUDAをソースからビルド
# ビルド時に -DWITH_CUDA=ON を指定
```

**実装手順**
1. cv2.cuda.GpuMatを使用した色空間変換
2. GPU上でのリサイズ処理

**期待される総処理時間**: 20-30秒 → **15-20秒**（さらに1.5倍高速化）

---

### フェーズ3: エンドツーエンドGPU処理（将来的拡張）

**概要**
- HSDファイル読み込みからJPEG保存まで全てGPU上で実行
- GPUメモリ上でデータを保持し、CPU↔GPU転送を最小化

**期待される総処理時間**: **10秒以下**（さらなる高速化）

---

## 実装優先順位

### 最優先（即実装可能）
1. **CuPyによるガンマ補正高速化** - 10-15秒短縮
2. **CuPyによるHSV変換高速化** - 27-37秒短縮

### 優先度: 中
3. **CuPyによる彩度・コントラスト高速化** - 8-13秒短縮
4. **OpenCV CUDAリサイズ** - 数秒短縮

### 将来的検討
5. **エンドツーエンドGPU処理** - さらなる高速化

---

## GPU要件

### 最小要件
- **GPU**: NVIDIA GPU（CUDA Compute Capability 3.5以上）
- **VRAM**: 4GB以上（11000×11000×3チャンネル×4バイト = 約1.5GB）
- **CUDA**: 11.x または 12.x
- **Driver**: 最新のNVIDIA GPU Driver

### 推奨環境
- **GPU**: RTX 3060 以上（または同等のデータセンターGPU）
- **VRAM**: 8GB以上
- **CUDA**: 12.x
- **メモリ**: システムメモリ 16GB以上

---

## 期待される最終結果

| 最適化段階 | 処理時間 | 短縮時間 |
|----------|---------|---------|
| 現状（CPU） | 88秒 | - |
| フェーズ1（CuPy） | 20-30秒 | **58-68秒短縮** |
| フェーズ2（OpenCV CUDA） | 15-20秒 | **68-73秒短縮** |
| フェーズ3（完全GPU） | 10秒以下 | **78秒以上短縮** |

**目標の60秒以下は、フェーズ1のCuPy導入のみで達成可能です。**

---

## 次のステップ

1. CUDA環境の確認
   ```bash
   nvidia-smi
   nvcc --version
   ```

2. CuPyのインストール
   ```bash
   pip install cupy-cuda12x  # CUDA 12.xの場合
   ```

3. `image_enhance.py` のGPU対応実装

4. テスト実行と処理時間測定

5. 必要に応じてフェーズ2へ進む
