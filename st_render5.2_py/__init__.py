"""
st_render - Himawari/GOES衛星データ可視化ツール (Python版)

このパッケージは、Himawari8/9の標準データ(HSD)およびGOES16-18のL1b netCDFファイルを
PNG画像に変換する機能を提供します。
"""

__version__ = "5.2.0"
__author__ = "Converted to Python from C++ version by @linsanyi031"

from .hsd_reader import hsd_read, HSData
from .calibration import hsd_calibration, goes_calibration
from .colorscale import (
    bw_scale,
    bd_scale,
    color2_scale,
    wvnrl_scale
)

try:
    from .goes_reader import goes_read, GOESData
    GOES_SUPPORT = True
except ImportError:
    GOES_SUPPORT = False

__all__ = [
    'hsd_read',
    'HSData',
    'hsd_calibration',
    'goes_calibration',
    'bw_scale',
    'bd_scale',
    'color2_scale',
    'wvnrl_scale',
    'GOES_SUPPORT',
]

if GOES_SUPPORT:
    __all__.extend(['goes_read', 'GOESData'])
