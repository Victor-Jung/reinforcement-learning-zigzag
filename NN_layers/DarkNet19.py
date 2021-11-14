# Unique Layers : 1 2 3 4 6 7 9 10 14 15 19
layer_info = \
{1: {'B': 1, 'K': 32, 'C': 3, 'OX': 224, 'OY': 224, 'FX': 3, 'FY': 3, 'SX': 1, 'SY': 1, 'SFX': 1, 'SFY': 1, 'PY': 0, 'PX': 0, 'G': 1},
 2: {'B': 1, 'K': 64, 'C': 32, 'OX': 112, 'OY': 112, 'FX': 3, 'FY': 3, 'SX': 1, 'SY': 1, 'SFX': 1, 'SFY': 1, 'PY': 0, 'PX': 0, 'G': 1},
 3: {'B': 1, 'K': 128, 'C': 64, 'OX': 56, 'OY': 56, 'FX': 3, 'FY': 3, 'SX': 1, 'SY': 1, 'SFX': 1, 'SFY': 1, 'PY': 0, 'PX': 0, 'G': 1},
 4: {'B': 1, 'K': 64, 'C': 128, 'OX': 56, 'OY': 56, 'FX': 1, 'FY': 1, 'SX': 1, 'SY': 1, 'SFX': 1, 'SFY': 1, 'PY': 0, 'PX': 0, 'G': 1},
 5: {'B': 1, 'K': 128, 'C': 64, 'OX': 56, 'OY': 56, 'FX': 3, 'FY': 3, 'SX': 1, 'SY': 1, 'SFX': 1, 'SFY': 1, 'PY': 0, 'PX': 0, 'G': 1},
 6: {'B': 1, 'K': 256, 'C': 128, 'OX': 28, 'OY': 28, 'FX': 3, 'FY': 3, 'SX': 1, 'SY': 1, 'SFX': 1, 'SFY': 1, 'PY': 0, 'PX': 0, 'G': 1},
 7: {'B': 1, 'K': 128, 'C': 256, 'OX': 28, 'OY': 28, 'FX': 1, 'FY': 1, 'SX': 1, 'SY': 1, 'SFX': 1, 'SFY': 1, 'PY': 0, 'PX': 0, 'G': 1},
 8: {'B': 1, 'K': 256, 'C': 128, 'OX': 28, 'OY': 28, 'FX': 3, 'FY': 3, 'SX': 1, 'SY': 1, 'SFX': 1, 'SFY': 1, 'PY': 0, 'PX': 0, 'G': 1},
 9: {'B': 1, 'K': 512, 'C': 256, 'OX': 14, 'OY': 14, 'FX': 3, 'FY': 3, 'SX': 1, 'SY': 1, 'SFX': 1, 'SFY': 1, 'PY': 0, 'PX': 0, 'G': 1},
 10: {'B': 1, 'K': 256, 'C': 512, 'OX': 14, 'OY': 14, 'FX': 1, 'FY': 1, 'SX': 1, 'SY': 1, 'SFX': 1, 'SFY': 1, 'PY': 0, 'PX': 0, 'G': 1},
 11: {'B': 1, 'K': 512, 'C': 256, 'OX': 14, 'OY': 14, 'FX': 3, 'FY': 3, 'SX': 1, 'SY': 1, 'SFX': 1, 'SFY': 1, 'PY': 0, 'PX': 0, 'G': 1},
 12: {'B': 1, 'K': 256, 'C': 512, 'OX': 14, 'OY': 14, 'FX': 1, 'FY': 1, 'SX': 1, 'SY': 1, 'SFX': 1, 'SFY': 1, 'PY': 0, 'PX': 0, 'G': 1},
 13: {'B': 1, 'K': 512, 'C': 256, 'OX': 14, 'OY': 14, 'FX': 3, 'FY': 3, 'SX': 1, 'SY': 1, 'SFX': 1, 'SFY': 1, 'PY': 0, 'PX': 0, 'G': 1},
 14: {'B': 1, 'K': 1024, 'C': 512, 'OX': 7, 'OY': 7, 'FX': 3, 'FY': 3, 'SX': 1, 'SY': 1, 'SFX': 1, 'SFY': 1, 'PY': 0, 'PX': 0, 'G': 1},
 15: {'B': 1, 'K': 512, 'C': 1024, 'OX': 7, 'OY': 7, 'FX': 1, 'FY': 1, 'SX': 1, 'SY': 1, 'SFX': 1, 'SFY': 1, 'PY': 0, 'PX': 0, 'G': 1},
 16: {'B': 1, 'K': 1024, 'C': 512, 'OX': 7, 'OY': 7, 'FX': 3, 'FY': 3, 'SX': 1, 'SY': 1, 'SFX': 1, 'SFY': 1, 'PY': 0, 'PX': 0, 'G': 1},
 17: {'B': 1, 'K': 512, 'C': 1024, 'OX': 7, 'OY': 7, 'FX': 1, 'FY': 1, 'SX': 1, 'SY': 1, 'SFX': 1, 'SFY': 1, 'PY': 0, 'PX': 0, 'G': 1},
 18: {'B': 1, 'K': 1024, 'C': 512, 'OX': 7, 'OY': 7, 'FX': 3, 'FY': 3, 'SX': 1, 'SY': 1, 'SFX': 1, 'SFY': 1, 'PY': 0, 'PX': 0, 'G': 1},
 19: {'B': 1, 'K': 1000, 'C': 1024, 'OX': 7, 'OY': 7, 'FX': 1, 'FY': 1, 'SX': 1, 'SY': 1, 'SFX': 1, 'SFY': 1, 'PY': 0, 'PX': 0, 'G': 1}}
