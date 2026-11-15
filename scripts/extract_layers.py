import json
import math
import os
import subprocess

SRC = "public/assets/aistudio/file_000000002270821199a727b6f268f437_729c8eb7.png"
OUT_DIR = "public/assets/layers"
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(".playwright-cli", exist_ok=True)

W, H = 938, 1677
SX0, SY0 = 83, 110
SX1, SY1 = 855, 1616
CW = SX1 - SX0 + 1  # 773
CH = SY1 - SY0 + 1  # 1507

proc = subprocess.run(["convert", SRC, "-depth", "8", "rgb:-"], capture_output=True, check=True)
raw = proc.stdout
assert len(raw) == W * H * 3


def get_px(x: int, y: int) -> tuple[int, int, int]:
    x = max(0, min(W - 1, x))
    y = max(0, min(H - 1, y))
    i = (y * W + x) * 3
    return raw[i], raw[i + 1], raw[i + 2]


def write_rgba_png(path: str, w: int, h: int, buf: bytearray):
    p = subprocess.run(
        ["convert", "-size", f"{w}x{h}", "-depth", "8", "rgba:-", path],
        input=bytes(buf),
        capture_output=True,
    )
    if p.returncode != 0:
        raise RuntimeError(p.stderr.decode())


def color_dist(c1, c2):
    return math.sqrt((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2 + (c1[2] - c2[2]) ** 2)


def clamp(v, lo=0, hi=255):
    return max(lo, min(hi, int(round(v))))


def crop_and_save(name: str, canvas_rgba: bytearray, x0: int, y0: int, x1: int, y1: int, pad: int = 0):
    x0 = max(0, x0 - pad)
    y0 = max(0, y0 - pad)
    x1 = min(CW - 1, x1 + pad)
    y1 = min(CH - 1, y1 + pad)
    bw = x1 - x0 + 1
    bh = y1 - y0 + 1
    out = bytearray(bw * bh * 4)
    for yy in range(bh):
        src_off = ((y0 + yy) * CW + x0) * 4
        dst_off = yy * bw * 4
        out[dst_off : dst_off + bw * 4] = canvas_rgba[src_off : src_off + bw * 4]
    write_rgba_png(os.path.join(OUT_DIR, f"{name}.png"), bw, bh, out)
    return {"x": x0, "y": y0, "width": bw, "height": bh}


manifest = {
    "canvasWidth": CW,
    "canvasHeight": CH,
    "layers": {},
}

# 1. Sky Background (sampled cleanly from untouched paper band y=360..760)
sky_rgba = bytearray(CW * CH * 4)
for cy in range(1025):
    oy = SY0 + cy
    if oy < 360:
        sample_y = 360 + (360 - oy) % 360
    elif oy > 760:
        sample_y = 360 + (oy - 360) % 360
    else:
        sample_y = oy
    for cx in range(CW):
        ox = SX0 + cx
        r, g, b = get_px(ox, sample_y)
        i = (cy * CW + cx) * 4
        sky_rgba[i : i + 4] = bytes((r, g, b, 255))

manifest["layers"]["sky"] = crop_and_save("sky-bg", sky_rgba, 0, 0, CW - 1, 1020)


# 2. Logo & Menu Button
def extract_against_sky(x0, y0, x1, y1, lo_dist=14, hi_dist=36):
    buf = bytearray(CW * CH * 4)
    ref = (253, 237, 178)
    for oy in range(y0, y1 + 1):
        cy = oy - SY0
        for ox in range(x0, x1 + 1):
            cx = ox - SX0
            if not (0 <= cx < CW and 0 <= cy < CH):
                continue
            r, g, b = get_px(ox, oy)
            d = color_dist((r, g, b), ref)
            if d <= lo_dist:
                a = 0
            elif d >= hi_dist:
                a = 255
            else:
                a = clamp(((d - lo_dist) / (hi_dist - lo_dist)) * 255)
            if 0 < a < 255:
                af = a / 255.0
                r = clamp((r - (1 - af) * ref[0]) / af)
                g = clamp((g - (1 - af) * ref[1]) / af)
                b = clamp((b - (1 - af) * ref[2]) / af)
            i = (cy * CW + cx) * 4
            buf[i : i + 4] = bytes((r, g, b, a))
    return buf


logo_buf = extract_against_sky(124, 118, 386, 218, lo_dist=14, hi_dist=34)
manifest["layers"]["logo"] = crop_and_save("logo", logo_buf, 124 - SX0, 118 - SY0, 386 - SX0, 218 - SY0, pad=2)

menu_buf = extract_against_sky(725, 122, 845, 228, lo_dist=10, hi_dist=32)
manifest["layers"]["menuBtn"] = crop_and_save("menu-btn", menu_buf, 725 - SX0, 122 - SY0, 845 - SX0, 228 - SY0, pad=2)


# 3. Sun + attached cloud overlap (100% untouched original pixels inside sun circle, alpha-matted against cream sky)
sun_cx, sun_cy, sun_r = 638.0, 218.0, 53.0
sun_buf = bytearray(CW * CH * 4)
ref_sky = (253, 237, 178)
for oy in range(160, 266):
    cy = oy - SY0
    for ox in range(580, 696):
        cx = ox - SX0
        dist = math.hypot(ox - sun_cx, oy - sun_cy)
        if dist <= sun_r + 2.0:
            r, g, b = get_px(ox, oy)
            d = color_dist((r, g, b), ref_sky)
            if d <= 6:
                a = 0
            elif d >= 22:
                a = 255
            else:
                a = clamp(((d - 6) / 16.0) * 255)
            # Also keep crisp circular anti-aliased edge on top half
            if oy <= 215 and dist > sun_r - 0.5:
                rim_a = clamp((sun_r + 1.5 - dist) / 2.0 * 255)
                a = min(a, rim_a)
            if 0 < a < 255:
                af = a / 255.0
                r = clamp((r - (1 - af) * ref_sky[0]) / af)
                g = clamp((g - (1 - af) * ref_sky[1]) / af)
                b = clamp((b - (1 - af) * ref_sky[2]) / af)
            i = (cy * CW + cx) * 4
            sun_buf[i : i + 4] = bytes((r, g, b, a))

manifest["layers"]["sun"] = crop_and_save("sun", sun_buf, 580 - SX0, 160 - SY0, 696 - SX0, 266 - SY0)


# 4. Clouds (cleanly separating cloudLeft, cloudMid, and cloudRight with zero sun/logo overlap!)
def extract_cloud_region(x0, y0, x1, y1, mode="normal"):
    buf = bytearray(CW * CH * 4)
    ref = (253, 237, 178)
    for oy in range(y0, y1 + 1):
        cy = oy - SY0
        for ox in range(x0, x1 + 1):
            cx = ox - SX0
            if not (0 <= cx < CW and 0 <= cy < CH):
                continue
            r, g, b = get_px(ox, oy)
            if mode == "mid":
                dist_sun = math.hypot(ox - sun_cx, oy - sun_cy)
                if dist_sun <= sun_r + 0.5:
                    continue
            elif mode == "right":
                # Strictly exclude the sun & mid-cloud region (ox <= 758, oy <= 258)
                if oy <= 258 and ox <= 758:
                    continue
            d = color_dist((r, g, b), ref)
            bright_diff = (r - ref[0]) + (g - ref[1]) + (b - ref[2])
            eff_d = max(d, bright_diff * 0.8)
            if eff_d <= 8:
                a = 0
            elif eff_d >= 26:
                a = 255
            else:
                a = clamp(((eff_d - 8) / 18.0) * 255)
            if 0 < a < 255:
                af = a / 255.0
                r = clamp((r - (1 - af) * ref[0]) / af)
                g = clamp((g - (1 - af) * ref[1]) / af)
                b = clamp((b - (1 - af) * ref[2]) / af)
            i = (cy * CW + cx) * 4
            buf[i : i + 4] = bytes((r, g, b, a))
    return buf


cloud_left_buf = extract_cloud_region(83, 218, 305, 332)
manifest["layers"]["cloudLeft"] = crop_and_save("cloud-left", cloud_left_buf, 83 - SX0, 218 - SY0, 305 - SX0, 332 - SY0)

cloud_mid_buf = extract_cloud_region(435, 198, 755, 258, mode="mid")
manifest["layers"]["cloudMid"] = crop_and_save("cloud-mid", cloud_mid_buf, 435 - SX0, 198 - SY0, 755 - SX0, 258 - SY0)

cloud_right_buf = extract_cloud_region(580, 226, 855, 345, mode="right")
manifest["layers"]["cloudRight"] = crop_and_save("cloud-right", cloud_right_buf, 580 - SX0, 226 - SY0, 855 - SX0, 345 - SY0)


# 5. Classifiers
def is_sky_px(r, g, b):
    return r > 228 and g > 208 and b > 152 and (r - b) < 95


def is_dune1_teal(r, g, b):
    return r < 30 and 30 <= g <= 95 and 40 <= b <= 115


def is_dune2_orange(r, g, b):
    return r > 180 and 75 <= g <= 145 and b < 45


def is_dune3_yellow(r, g, b):
    return r > 220 and 195 <= g <= 242 and 80 <= b <= 165


def is_dune4_amber(r, g, b):
    return r > 205 and 138 <= g <= 198 and b < 55


def is_dune5_red(r, g, b):
    return 115 <= r <= 235 and g < 40 and b < 40


def is_dune6_teal(r, g, b):
    return r < 35 and 30 <= g <= 100 and 45 <= b <= 120


def smooth_curve(pts_dict, xs):
    keys = sorted(pts_dict.keys())
    out = [0] * len(xs)
    for idx, x in enumerate(xs):
        if x in pts_dict:
            out[idx] = pts_dict[x]
        elif x < keys[0]:
            out[idx] = pts_dict[keys[0]]
        elif x > keys[-1]:
            out[idx] = pts_dict[keys[-1]]
        else:
            lo = max(k for k in keys if k <= x)
            hi = min(k for k in keys if k >= x)
            t = (x - lo) / max(1, hi - lo)
            out[idx] = int(round(pts_dict[lo] * (1 - t) + pts_dict[hi] * t))
    return out


# Dune 1 ridge
d1_pts = {}
for cx in range(CW):
    ox = SX0 + cx
    if ox <= 665:
        for oy in range(845, 960):
            r, g, b = get_px(ox, oy)
            if is_dune1_teal(r, g, b):
                d1_pts[cx] = oy - SY0
                break
d1_pts[665 - SX0] = d1_pts.get(665 - SX0, 912 - SY0)
d1_pts[720 - SX0] = 907 - SY0
d1_pts[790 - SX0] = 903 - SY0
d1_pts[CW - 1] = 905 - SY0
y_d1 = smooth_curve(d1_pts, range(CW))

# Dune 2 top & bottom
d2_top_pts = {}
d2_bot_pts = {}
for cx in range(CW):
    ox = SX0 + cx
    if not (705 <= ox <= 845):
        for oy in range(955, 1085):
            r, g, b = get_px(ox, oy)
            if is_dune2_orange(r, g, b) and r > 215 and g > 105:
                d2_top_pts[cx] = oy - SY0
                break
    if ox <= 505:
        for oy in range(1165, 1050, -1):
            r, g, b = get_px(ox, oy)
            if is_dune2_orange(r, g, b):
                d2_bot_pts[cx] = oy - SY0
                break
d2_top_pts[CW - 1] = 975 - SY0
y_d2_top = smooth_curve(d2_top_pts, range(CW))
d2_bot_pts[560 - SX0] = 1162 - SY0
d2_bot_pts[CW - 1] = 1230 - SY0
y_d2_bot = smooth_curve(d2_bot_pts, range(CW))

# Dune 3 top: cleanly tucked 4px inside Dune 2 bottom edge so zero straight seam!
y_d3_top = [max(0, y_d2_bot[cx] - 4) for cx in range(CW)]

# Dune 4 top
d4_pts = {}
for cx in range(CW):
    ox = SX0 + cx
    if ox >= 330:
        for oy in range(1135, 1300):
            r, g, b = get_px(ox, oy)
            if is_dune4_amber(r, g, b) and r > 235 and g > 152:
                d4_pts[cx] = oy - SY0
                break
d4_pts[0] = 1350 - SY0
d4_pts[325 - SX0] = 1278 - SY0
y_d4_top = smooth_curve(d4_pts, range(CW))

# Dune 5 top
d5_pts = {}
for cx in range(CW):
    ox = SX0 + cx
    if ox <= 595:
        for oy in range(1260, 1410):
            r, g, b = get_px(ox, oy)
            if is_dune5_red(r, g, b) and r > 170:
                d5_pts[cx] = oy - SY0
                break
d5_pts[CW - 1] = 1435 - SY0
y_d5_top = smooth_curve(d5_pts, range(CW))

# Dune 6 top
d6_pts = {}
for cx in range(CW):
    ox = SX0 + cx
    for oy in range(1530, 1365, -1):
        r, g, b = get_px(ox, oy)
        if not is_dune6_teal(r, g, b):
            d6_pts[cx] = (oy + 1) - SY0
            break
y_d6_top = smooth_curve(d6_pts, range(CW))


def sample_dune_texture(cx: int, cy: int, clean_y_min: int, clean_y_max: int, fallback_rgb, check_fn, prefer_horizontal=False):
    ox = SX0 + cx
    oy = SY0 + cy
    if prefer_horizontal:
        # Try same oy horizontally first so lighting gradient matches 100%!
        for dx in (0, -140, 140, -210, 210, -270, 270):
            sx = ox + dx
            if SX0 <= sx <= SX1:
                c = get_px(sx, oy)
                if check_fn(*c):
                    return c
    if clean_y_min <= oy <= clean_y_max:
        c = get_px(ox, oy)
        if check_fn(*c):
            return c
    span = max(8, clean_y_max - clean_y_min)
    ty = clean_y_min + ((oy - clean_y_min) % span)
    for dx in (0, 28, -28, 60, -60, 110, -110, 170, -170):
        sx = max(SX0, min(SX1, ox + dx))
        c = get_px(sx, ty)
        if check_fn(*c):
            return c
    return fallback_rgb


def build_dune_layer(
    name: str,
    y_top_arr: list[int],
    y_bot_arr: list[int] | None,
    top_shadow_px: int,
    bot_shadow_px: int,
    clean_band_fn,
    check_fn,
    fallback_rgb,
    preserve_orig_pred,
    prefer_horizontal=False,
):
    buf = bytearray(CW * CH * 4)
    min_y = max(0, min(y_top_arr) - top_shadow_px - 2)
    max_y = CH - 1 if y_bot_arr is None else min(CH - 1, max(y_bot_arr) + bot_shadow_px + 2)
    for cx in range(CW):
        ox = SX0 + cx
        yt = y_top_arr[cx]
        yb = (CH - 1) if y_bot_arr is None else y_bot_arr[cx]
        cy_min, cy_max = clean_band_fn(cx, ox)
        for cy in range(max(0, yt - top_shadow_px), min(CH, yb + bot_shadow_px + 1)):
            oy = SY0 + cy
            r, g, b = get_px(ox, oy)
            if cy < yt:
                t = 1.0 - (yt - cy) / max(1, top_shadow_px)
                if preserve_orig_pred(ox, oy, r, g, b):
                    a = clamp((t ** 1.5) * 210)
                else:
                    r, g, b = 12, 18, 22
                    a = clamp((t ** 2.2) * 90)
            elif cy > yb and y_bot_arr is not None:
                t = 1.0 - (cy - yb) / max(1, bot_shadow_px)
                a = clamp((t ** 1.5) * 215)
                r, g, b = 45, 22, 4
            else:
                a = 255
                if not (preserve_orig_pred(ox, oy, r, g, b) and check_fn(r, g, b)):
                    r, g, b = sample_dune_texture(
                        cx, cy, cy_min, cy_max, fallback_rgb, check_fn, prefer_horizontal=prefer_horizontal
                    )
            i = (cy * CW + cx) * 4
            buf[i : i + 4] = bytes((r, g, b, a))
    manifest["layers"][name] = crop_and_save(name, buf, 0, min_y, CW - 1, max_y)


build_dune_layer(
    "dune-1",
    y_d1,
    None,
    top_shadow_px=2,
    bot_shadow_px=0,
    clean_band_fn=lambda cx, ox: (915, 965) if ox < 600 else (920, 955),
    check_fn=is_dune1_teal,
    fallback_rgb=(1, 63, 80),
    preserve_orig_pred=lambda ox, oy, r, g, b: ox < 650 and oy < 965,
)

build_dune_layer(
    "dune-2",
    y_d2_top,
    y_d2_bot,
    top_shadow_px=14,
    bot_shadow_px=20,
    clean_band_fn=lambda cx, ox: (1000, 1085) if ox < 500 else (1065, 1115),
    check_fn=is_dune2_orange,
    fallback_rgb=(251, 120, 1),
    preserve_orig_pred=lambda ox, oy, r, g, b: not (705 <= ox <= 845 and oy < 1135) and not (510 <= ox <= 835 and oy >= 1040 and not is_dune2_orange(r, g, b)),
    prefer_horizontal=True,
)

build_dune_layer(
    "dune-3",
    y_d3_top,
    None,
    top_shadow_px=3,
    bot_shadow_px=0,
    clean_band_fn=lambda cx, ox: (1160, 1235),
    check_fn=is_dune3_yellow,
    fallback_rgb=(254, 223, 122),
    preserve_orig_pred=lambda ox, oy, r, g, b: is_dune3_yellow(r, g, b) and not (115 <= ox <= 252 and 1195 <= oy <= 1345) and not (510 <= ox <= 620 and 1120 <= oy <= 1245),
    prefer_horizontal=True,
)

build_dune_layer(
    "dune-4",
    y_d4_top,
    None,
    top_shadow_px=8,
    bot_shadow_px=0,
    clean_band_fn=lambda cx, ox: (1250, 1340) if ox >= 420 else (1275, 1310),
    check_fn=is_dune4_amber,
    fallback_rgb=(253, 166, 1),
    preserve_orig_pred=lambda ox, oy, r, g, b: is_dune4_amber(r, g, b) and not (575 <= ox <= 805 and 1210 <= oy <= 1390),
    prefer_horizontal=True,
)

build_dune_layer(
    "dune-5",
    y_d5_top,
    None,
    top_shadow_px=8,
    bot_shadow_px=0,
    clean_band_fn=lambda cx, ox: (1335, 1410),
    check_fn=is_dune5_red,
    fallback_rgb=(193, 2, 1),
    preserve_orig_pred=lambda ox, oy, r, g, b: is_dune5_red(r, g, b) and not (150 <= ox <= 286 and 1325 <= oy <= 1470),
    prefer_horizontal=True,
)

build_dune_layer(
    "dune-6",
    y_d6_top,
    None,
    top_shadow_px=15,
    bot_shadow_px=0,
    clean_band_fn=lambda cx, ox: (1485, 1580),
    check_fn=is_dune6_teal,
    fallback_rgb=(1, 63, 82),
    preserve_orig_pred=lambda ox, oy, r, g, b: oy < 1525 or (160 <= ox <= 775 and oy < 1605),
    prefer_horizontal=True,
)


# 6. Build Camel Mask first so Palm Tree never steals camel pixels and vice-versa!
def is_camel_pixel(ox, oy, r, g, b):
    if not (510 <= ox <= 835 and 1045 <= oy <= 1242):
        return False
    cx = ox - SX0
    if (oy - SY0) > y_d4_top[cx] + 3:
        return False
    # Exclude Dune 1 curved shadow above Camel 1 (ox < 695, oy < 1068)
    if oy < 1068 and ox < 695:
        return False
    # Exclude palm fronds above Camel 2
    if oy < 1055 and ox > 730:
        return False
    # Exclude palm trunk gap between Camel 2's front and back legs
    if 777 <= ox <= 808 and oy >= 1118 and (r > g or b < 45):
        return False
    # Camel & person dark teal silhouette (b >= g and r < 48)
    if r < 48 and b >= g - 4 and (r + g + b) < 205:
        return True
    # Rope between person and Camel 1 (dark thin line, exclude bright orange dune shadow b < 25 & r > 125)
    if 545 <= ox <= 586 and 1076 <= oy <= 1165 and r < 140 and g < 130 and (b >= 30 or r < 95):
        return True
    return False


# Extract Palm Tree cleanly (keeping all orange dates, fronds, and brown trunk only!)
palm_buf = bytearray(CW * CH * 4)
for oy in range(812, 1146):
    cy = oy - SY0
    for ox in range(635, 856):
        cx = ox - SX0
        r, g, b = get_px(ox, oy)
        if is_sky_px(r, g, b):
            continue
        if oy >= 1136 and is_dune4_amber(r, g, b):
            continue
        if oy > 1004:
            # Below the dates, ONLY the palm trunk exists (ox in 777..799)
            if not (777 <= ox <= 799):
                continue
            if is_camel_pixel(ox, oy, r, g, b) or is_dune2_orange(r, g, b) or is_dune4_amber(r, g, b) or b > g + 5 or r > 150:
                found = False
                for sy in (1012 + (oy % 32), 1020 + (oy % 24), 1015):
                    tr, tg, tb = get_px(ox, sy)
                    if tr > tg and tr < 135 and not is_dune2_orange(tr, tg, tb):
                        i = (cy * CW + cx) * 4
                        palm_buf[i : i + 4] = bytes((tr, tg, tb, 255))
                        found = True
                        break
                if found:
                    continue
                continue
        else:
            # Above oy = 1004: fronds & date clusters
            if ox < 665 and oy > 892:
                continue
            # Exclude Dune 1 dark teal rim & background behind fronds
            if r < 35 and b > g + 5 and oy > 892 and (ox < 745 or (oy <= 955 and ox > 795)):
                continue
            # Exclude Dune 2 orange outside date clusters
            if is_dune2_orange(r, g, b):
                in_dates = (690 <= ox <= 855 and 942 <= oy <= 1004)
                if not in_dates:
                    continue
                if 114 <= g <= 128 and b <= 5 and r >= 245:
                    continue
        i = (cy * CW + cx) * 4
        palm_buf[i : i + 4] = bytes((r, g, b, 255))

manifest["layers"]["palm-tree"] = crop_and_save("palm-tree", palm_buf, 635 - SX0, 812 - SY0, 855 - SX0, 1144 - SY0, pad=1)


# Extract Camel Caravan
camel_buf = bytearray(CW * CH * 4)
for oy in range(1045, 1242):
    cy = oy - SY0
    for ox in range(510, 835):
        cx = ox - SX0
        r, g, b = get_px(ox, oy)
        if is_camel_pixel(ox, oy, r, g, b):
            i = (cy * CW + cx) * 4
            camel_buf[i : i + 4] = bytes((r, g, b, 255))

manifest["layers"]["camel-caravan"] = crop_and_save("camel-caravan", camel_buf, 510 - SX0, 1045 - SY0, 835 - SX0, 1242 - SY0, pad=1)


# Extract Cactus 1, Cactus 2, Dry Tree
def extract_subject(name: str, x0: int, y0: int, x1: int, y1: int, keep_fn):
    buf = bytearray(CW * CH * 4)
    for oy in range(y0, y1 + 1):
        cy = oy - SY0
        for ox in range(x0, x1 + 1):
            cx = ox - SX0
            if not (0 <= cx < CW and 0 <= cy < CH):
                continue
            r, g, b = get_px(ox, oy)
            a = keep_fn(ox, oy, r, g, b)
            if a > 0:
                i = (cy * CW + cx) * 4
                buf[i : i + 4] = bytes((r, g, b, a))
    manifest["layers"][name] = crop_and_save(name, buf, x0 - SX0, y0 - SY0, x1 - SX0, y1 - SY0, pad=1)


extract_subject(
    "cactus-1",
    115,
    1195,
    252,
    1340,
    lambda ox, oy, r, g, b: 0
    if ((oy - SY0) > y_d5_top[ox - SX0] + 3 or is_sky_px(r, g, b) or is_dune3_yellow(r, g, b) or is_dune5_red(r, g, b))
    else (255 if (g > r or (r + g + b < 160)) else 0),
)

extract_subject(
    "cactus-2",
    150,
    1325,
    286,
    1472,
    lambda ox, oy, r, g, b: 0
    if ((oy - SY0) > y_d6_top[ox - SX0] + 3 or is_dune5_red(r, g, b) or is_dune6_teal(r, g, b))
    else (255 if (g > r - 5 or (r + g + b < 140)) else 0),
)

extract_subject(
    "dry-tree",
    578,
    1210,
    802,
    1390,
    lambda ox, oy, r, g, b: 0
    if (oy - SY0) > y_d6_top[ox - SX0] + 3
    else (255 if (r < 115 and g < 85 and b < 45) else 0),
)

os.makedirs("src/data", exist_ok=True)
with open("src/data/layersManifest.json", "w") as f:
    json.dump(manifest, f, indent=2)

# Composite check
comp = bytearray(CW * CH * 4)
order = [
    ("sky", "sky-bg"),
    ("sun", "sun"),
    ("cloudLeft", "cloud-left"),
    ("cloudMid", "cloud-mid"),
    ("cloudRight", "cloud-right"),
    ("logo", "logo"),
    ("menuBtn", "menu-btn"),
    ("dune-1", "dune-1"),
    ("dune-2", "dune-2"),
    ("palm-tree", "palm-tree"),
    ("dune-3", "dune-3"),
    ("camel-caravan", "camel-caravan"),
    ("cactus-1", "cactus-1"),
    ("dune-4", "dune-4"),
    ("dry-tree", "dry-tree"),
    ("dune-5", "dune-5"),
    ("cactus-2", "cactus-2"),
    ("dune-6", "dune-6"),
]

for key, file_stem in order:
    info = manifest["layers"][key]
    lx, ly, lw, lh = info["x"], info["y"], info["width"], info["height"]
    p = subprocess.run(
        ["convert", os.path.join(OUT_DIR, f"{file_stem}.png"), "-depth", "8", "rgba:-"],
        capture_output=True,
        check=True,
    )
    lbuf = p.stdout
    for yy in range(lh):
        dy = ly + yy
        if dy >= CH:
            continue
        for xx in range(lw):
            dx = lx + xx
            if dx >= CW:
                continue
            si = (yy * lw + xx) * 4
            sa = lbuf[si + 3]
            if sa == 0:
                continue
            di = (dy * CW + dx) * 4
            if sa == 255:
                comp[di : di + 4] = lbuf[si : si + 4]
            else:
                af = sa / 255.0
                comp[di] = clamp(lbuf[si] * af + comp[di] * (1 - af))
                comp[di + 1] = clamp(lbuf[si + 1] * af + comp[di + 1] * (1 - af))
                comp[di + 2] = clamp(lbuf[si + 2] * af + comp[di + 2] * (1 - af))
                comp[di + 3] = 255

write_rgba_png(".playwright-cli/composite_check_v2.png", CW, CH, comp)
print("v2 extraction done!")
