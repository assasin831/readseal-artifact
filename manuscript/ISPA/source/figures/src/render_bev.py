"""Render one nuScenes LiDAR sweep top-down for Fig. 1 (fig0_scene).

Input: n015-2018-07-24-11-22-45+0800__LIDAR_TOP__1532402927647951.pcd.bin, a LIDAR_TOP
sweep of nuScenes-mini scene-0061 (float32 x, y, z, intensity, ring; x right, y forward).
nuScenes is (c) Motional, CC BY-NC-SA 4.0. Output: bev_frame.png, the panel image.
Points are drawn in their sensor frame; height above a local ground estimate sets the color.
"""
import sys, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from scipy.ndimage import minimum_filter

SRC = sys.argv[1] if len(sys.argv) > 1 else 'n015-2018-07-24-11-22-45+0800__LIDAR_TOP__1532402927647951.pcd.bin'
LIM = 36.0          # half-width of the panel, m
SIZE_PT = 84.0      # panel size in the figure, pt
PX = 840            # 720 dpi at that size

p = np.fromfile(SRC, dtype=np.float32).reshape(-1, 5)
p = p[np.hypot(p[:, 0], p[:, 1]) > 2.5]          # drop returns from the ego vehicle
x, y, z = p[:, 0], p[:, 1], p[:, 2]

# local ground: 5th-percentile height per 2 m cell, then a 3x3 minimum
C, L = 2.0, 60.0; n = int(2 * L / C)
ix = np.clip(((x + L) / C).astype(int), 0, n - 1); iy = np.clip(((y + L) / C).astype(int), 0, n - 1)
G = np.full((n, n), np.inf)
key = ix * n + iy; o = np.argsort(key); ks, zs = key[o], z[o]
u, st = np.unique(ks, return_index=True); en = np.r_[st[1:], len(ks)]
for k, s, e in zip(u, st, en):
    G.flat[k] = np.percentile(zs[s:e], 5)
G = minimum_filter(G, size=3); G[np.isinf(G)] = -1.84
h = z - G[ix, iy]

m = (np.abs(x) < LIM + 1) & (np.abs(y) < LIM + 1)
g = m & (h < 0.3); obj = np.where(m & (h >= 0.3))[0]; obj = obj[np.argsort(h[obj])]
cmap = LinearSegmentedColormap.from_list('h', ['#3d7fd0', '#41c0d3', '#f6c453', '#ff8a5b'])
inch = SIZE_PT / 72
fig = plt.figure(figsize=(inch, inch), dpi=PX / inch); ax = fig.add_axes([0, 0, 1, 1])
bg = '#0d1520'; ax.set_facecolor(bg); fig.patch.set_facecolor(bg)
ax.scatter(x[g], y[g], c='#3a5068', s=0.06, lw=0)
ax.scatter(x[obj], y[obj], c=np.clip(h[obj], 0.3, 4), cmap=cmap, vmin=0.3, vmax=4, s=0.2, lw=0)
ax.set_xlim(-LIM, LIM); ax.set_ylim(-LIM, LIM); ax.set_aspect('equal'); ax.axis('off')
fig.savefig('bev_frame.png', facecolor=bg); plt.close(fig)

# ---- bev_feat.png: the texture on the front face of the BEV-map tensor in Fig. 1 ----
# An illustration of a BEV feature channel, not a model output: the occupancy of above-ground points on
# the map's 180 x 180 grid (0.6 m cells, 108 m across), smoothed and drawn in the figure's amber palette.
from scipy.ndimage import gaussian_filter
N, HALF = 180, 54.0
inside = (np.abs(x) < HALF) & (np.abs(y) < HALF)
gx = ((x + HALF) / (2 * HALF) * N).astype(int).clip(0, N - 1); gy = ((y + HALF) / (2 * HALF) * N).astype(int).clip(0, N - 1)
obj = np.zeros((N, N)); gnd = np.zeros((N, N))
np.add.at(obj, (N - 1 - gy[inside & (h >= 0.3)], gx[inside & (h >= 0.3)]), 1.0)
np.add.at(gnd, (N - 1 - gy[inside & (h < 0.3)], gx[inside & (h < 0.3)]), 1.0)
f = gaussian_filter(np.log1p(obj), 2.0) + 0.45 * gaussian_filter(np.log1p(gnd), 3.5)
f = np.clip(f / np.percentile(f, 99.5), 0, 1) ** 0.75
warm = LinearSegmentedColormap.from_list('warm', ['#FFF6DF', '#F8E3AE', '#E9B23A', '#C2410C', '#6B2A0E'])
rgb = (warm(f)[..., :3] * 255).astype(np.uint8)
from PIL import Image
Image.fromarray(rgb).resize((360, 360), Image.LANCZOS).save('bev_feat.png', optimize=True)
