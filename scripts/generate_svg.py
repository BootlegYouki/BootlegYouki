import base64
import os
import re

# Load fonts
script_dir = os.path.dirname(os.path.abspath(__file__))
nippo_path = os.path.join(script_dir, "..", "fonts", "Nippo-Bold.woff2")
with open(nippo_path, "rb") as f:
    nippo_base64 = base64.b64encode(f.read()).decode("utf-8")

jb_path = os.path.join(script_dir, "..", "fonts", "jetbrains-mono-latin-wght-normal.woff2")
with open(jb_path, "rb") as f:
    jb_base64 = base64.b64encode(f.read()).decode("utf-8")

# ============================================================
# TYPING ANIMATION — SMIL keyframe generation
# Two words: BootlegYouki → Mark Darren → loop
# ============================================================

TY = 80    # ms per char typed
TD = 45    # ms per char deleted
TP = 2000  # ms pause after full word
TE = 400   # ms empty pause before next word

# BootlegYouki clip widths (path-data coordinate space, from path boundary analysis)
W1 = [0, 79.2, 154.56, 224.52, 285.6, 321.48, 393.6, 467.76, 546, 621.96, 698.04, 770.64, 793.92]

# "Mark Darren" clip widths (fonttools advance widths at scale=79.2/690, includes space)
W2 = [0, 113.18, 182.96, 234.39, 303.83, 326.79, 407.94, 477.73, 529.15, 580.57, 650.13, 723.36]

CURSOR_GAP = 15.0
CURSOR_W   = 24.0
CURSOR_Y   = 68.16
CURSOR_H   = 23.04

n1 = len(W1) - 1   # 12
n2 = len(W2) - 1   # 11

# Timeline milestones (ms)
t_w1_full  = n1 * TY                 # 960
t_del1     = t_w1_full + TP + TD     # 3005
t_empty1   = t_del1 + (n1 - 1) * TD # 3500
t_w2_empty = t_empty1 + TE + TY     # 3980
t_w2_full  = t_w2_empty + n2 * TY   # 4860
t_del2     = t_w2_full + TP + TD    # 6905
t_empty2   = t_del2 + (n2 - 1) * TD # 7355
t_end      = t_empty2 + TE + TY     # 7835

# Build keyframe events
evt = {}
for i in range(n1 + 1):
    evt[i * TY] = (W1[i], 0.0)
evt[t_w1_full] = (W1[n1], 0.0)
for k in range(n1):
    evt[t_del1 + k * TD] = (W1[n1 - 1 - k], 0.0)
evt[t_empty1]  = (0.0, 0.0)
evt[t_w2_empty] = (0.0, 0.0)
for i in range(1, n2 + 1):
    evt[t_w2_empty + i * TY] = (0.0, W2[i])
evt[t_w2_full] = (0.0, W2[n2])
for k in range(n2):
    evt[t_del2 + k * TD] = (0.0, W2[n2 - 1 - k])
evt[t_empty2] = (0.0, 0.0)
evt[t_end]    = (0.0, 0.0)

all_t = sorted(evt.keys())
DUR_S = t_end / 1000.0

smil_times = ";".join(f"{t/t_end:.6f}" for t in all_t)
smil_cw1   = ";".join(f"{evt[t][0]:.2f}" for t in all_t)
smil_cw2   = ";".join(f"{evt[t][1]:.2f}" for t in all_t)
smil_cx    = ";".join(f"{max(evt[t][0], evt[t][1]) + CURSOR_GAP:.2f}" for t in all_t)

MD_FONT_SIZE = round(1000 * 79.2 / 690, 2)  # 114.78 — matches path-data scale
MD_BASELINE  = 91.2

def get_style_block(theme_mode, nippo_base64, jb_base64):
    if theme_mode == "dark":
        return f"""
      @font-face {{
        font-family: 'Nippo-Bold';
        src: url('data:font/woff2;charset=utf-8;base64,{nippo_base64}') format('woff2');
        font-weight: 900;
        font-style: normal;
      }}
      @font-face {{
        font-family: 'JetBrains-Mono';
        src: url('data:font/woff2;charset=utf-8;base64,{jb_base64}') format('woff2');
        font-weight: normal;
        font-style: normal;
      }}
      .tui-border {{
        stroke: #3D444D;
        stroke-width: 1.5;
        fill: none;
      }}
      .name-word {{
        fill: #ffffff;
        fill-rule: evenodd;
      }}
      .name-dot {{
        fill: #ef4444;
      }}
      .name-sub {{
        font-family: 'JetBrains-Mono', monospace;
        font-size: 32px;
        font-weight: bold;
        fill: #ffffff;
        letter-spacing: 0.5px;
      }}
      .ticker-text {{
        font-family: 'JetBrains-Mono', monospace;
        font-size: 12px;
        font-weight: bold;
        fill: #8b949e;
      }}
      .tui-legend {{
        font-family: 'JetBrains-Mono', monospace;
        font-size: 15px;
        font-weight: bold;
        fill: #8b949e;
      }}
      .stats-bar-bg {{
        fill: #21262d;
      }}
      .expo-icon {{
        fill: #ffffff;
      }}
"""
    elif theme_mode == "light":
        return f"""
      @font-face {{
        font-family: 'Nippo-Bold';
        src: url('data:font/woff2;charset=utf-8;base64,{nippo_base64}') format('woff2');
        font-weight: 900;
        font-style: normal;
      }}
      @font-face {{
        font-family: 'JetBrains-Mono';
        src: url('data:font/woff2;charset=utf-8;base64,{jb_base64}') format('woff2');
        font-weight: normal;
        font-style: normal;
      }}
      .tui-border {{
        stroke: #d0d7de;
        stroke-width: 1.5;
        fill: none;
      }}
      .name-word {{
        fill: #24292f;
        fill-rule: evenodd;
      }}
      .name-dot {{
        fill: #ef4444;
      }}
      .name-sub {{
        font-family: 'JetBrains-Mono', monospace;
        font-size: 32px;
        font-weight: bold;
        fill: #24292f;
        letter-spacing: 0.5px;
      }}
      .ticker-text {{
        font-family: 'JetBrains-Mono', monospace;
        font-size: 12px;
        font-weight: bold;
        fill: #57606a;
      }}
      .tui-legend {{
        font-family: 'JetBrains-Mono', monospace;
        font-size: 15px;
        font-weight: bold;
        fill: #57606a;
      }}
      .stats-bar-bg {{
        fill: #eaeef2;
      }}
      .expo-icon {{
        fill: #000020;
      }}
"""
    else:  # dynamic
        return f"""
      @font-face {{
        font-family: 'Nippo-Bold';
        src: url('data:font/woff2;charset=utf-8;base64,{nippo_base64}') format('woff2');
        font-weight: 900;
        font-style: normal;
      }}
      @font-face {{
        font-family: 'JetBrains-Mono';
        src: url('data:font/woff2;charset=utf-8;base64,{jb_base64}') format('woff2');
        font-weight: normal;
        font-style: normal;
      }}
      .tui-border {{
        stroke: #3D444D;
        stroke-width: 1.5;
        fill: none;
      }}
      .name-word {{
        fill: #ffffff;
        fill-rule: evenodd;
      }}
      .name-dot {{
        fill: #ef4444;
      }}
      .name-sub {{
        font-family: 'JetBrains-Mono', monospace;
        font-size: 32px;
        font-weight: bold;
        fill: #ffffff;
        letter-spacing: 0.5px;
      }}
      .ticker-text {{
        font-family: 'JetBrains-Mono', monospace;
        font-size: 12px;
        font-weight: bold;
        fill: #8b949e;
      }}
      .tui-legend {{
        font-family: 'JetBrains-Mono', monospace;
        font-size: 15px;
        font-weight: bold;
        fill: #8b949e;
      }}
      .stats-bar-bg {{
        fill: #21262d;
      }}
      .expo-icon {{
        fill: #ffffff;
      }}
      @media (prefers-color-scheme: light) {{
        .name-word {{ fill: #24292f; }}
        .tui-legend {{ fill: #57606a; }}
        .name-sub   {{ fill: #24292f; }}
        .ticker-text{{ fill: #57606a; }}
        .stats-bar-bg {{ fill: #eaeef2; }}
        .tui-border {{ stroke: #d0d7de; }}
        .expo-icon {{ fill: #000020; }}
      }}
"""

def generate_banner_svg(theme_mode):
    style_block = get_style_block(theme_mode, nippo_base64, jb_base64)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="20 58 920 200" width="100%" height="100%" xmlns:xlink="http://www.w3.org/1999/xlink">
  <defs>
    <!-- BootlegYouki reveal clip -->
    <clipPath id="clip-w1" clipPathUnits="userSpaceOnUse">
      <rect x="0" y="-20" height="150" width="0">
        <animate attributeName="width"
          values="{smil_cw1}"
          keyTimes="{smil_times}"
          calcMode="discrete"
          dur="{DUR_S:.3f}s"
          repeatCount="indefinite" />
      </rect>
    </clipPath>
    <!-- Mark Darren reveal clip -->
    <clipPath id="clip-w2" clipPathUnits="userSpaceOnUse">
      <rect x="0" y="-20" height="150" width="0">
        <animate attributeName="width"
          values="{smil_cw2}"
          keyTimes="{smil_times}"
          calcMode="discrete"
          dur="{DUR_S:.3f}s"
          repeatCount="indefinite" />
      </rect>
    </clipPath>
    <!-- Brighten filter (SQLite icon) -->
    <filter id="icon-brighten" x="0%" y="0%" width="100%" height="100%">
      <feComponentTransfer>
        <feFuncR type="linear" slope="6"/>
        <feFuncG type="linear" slope="6"/>
        <feFuncB type="linear" slope="6"/>
      </feComponentTransfer>
    </filter>
    <style>
{style_block}
    </style>
  </defs>

  <!-- Name Group — scale(1.1) applies to both path data and text element -->
  <g id="svgGroup" transform="translate(22, 60) scale(1.1)">

    <!-- Word 1: BootlegYouki — single white path, revealed by clip-w1 -->
    <g clip-path="url(#clip-w1)">
      <path class="name-word" d="
        M 67.2 78.12 L 54.12 91.2 L 0 91.2 L 0 7.2 L 53.4 7.2 L 66.48 20.28 L 66.48 40.44 L 58.08 48.84 L 67.2 57.96 L 67.2 78.12 Z
        M 43.2 72 L 24 72 L 24 57.6 L 40.56 57.6 L 43.2 60.24 L 43.2 72 Z
        M 39.84 40.8 L 24 40.8 L 24 26.4 L 42.48 26.4 L 42.48 38.16 L 39.84 40.8 Z
        M 79.2 38.28 L 92.28 25.2 L 129.48 25.2 L 142.56 38.28 L 142.56 78.12 L 129.48 91.2 L 92.28 91.2 L 79.2 78.12 L 79.2 38.28 Z
        M 102.48 70.32 L 102.48 46.08 L 119.28 46.08 L 119.28 70.32 L 102.48 70.32 Z
        M 154.56 38.28 L 167.64 25.2 L 204.84 25.2 L 217.92 38.28 L 217.92 78.12 L 204.84 91.2 L 167.64 91.2 L 154.56 78.12 L 154.56 38.28 Z
        M 177.84 70.32 L 177.84 46.08 L 194.64 46.08 L 194.64 70.32 L 177.84 70.32 Z
        M 273.6 69.6 L 273.6 91.2 L 245.76 91.2 L 232.68 78.12 L 232.68 43.2 L 224.52 43.2 L 224.52 25.2 L 232.68 25.2 L 232.68 10.2 L 255.96 10.2 L 255.96 25.2 L 273.12 25.2 L 273.12 43.2 L 255.96 43.2 L 255.96 69.6 L 273.6 69.6 Z
        M 308.88 1.2 L 308.88 91.2 L 285.6 91.2 L 285.6 1.2 L 308.88 1.2 Z
        M 344.28 72.72 L 360.48 72.72 L 360.48 67.44 L 382.8 67.44 L 382.8 78.12 L 369.72 91.2 L 334.56 91.2 L 321.48 78.12 L 321.48 38.28 L 334.56 25.2 L 369.72 25.2 L 382.8 38.28 L 382.8 62.4 L 344.28 62.4 L 344.28 72.72 Z
        M 360.48 52.08 L 344.28 52.08 L 344.28 43.68 L 360.48 43.68 L 360.48 52.08 Z
        M 394.32 103.32 L 394.32 92.28 L 416.4 92.28 L 416.4 97.2 L 433.68 97.2 L 433.68 86.4 L 406.68 86.4 L 393.6 73.32 L 393.6 38.28 L 406.68 25.2 L 428.4 25.2 L 436.56 33.36 L 436.56 25.2 L 456.96 25.2 L 456.96 103.32 L 443.88 116.4 L 407.4 116.4 L 394.32 103.32 Z
        M 430.92 46.8 L 433.68 49.2 L 433.68 67.92 L 416.88 67.92 L 416.88 46.8 L 430.92 46.8 Z
        M 516.48 67.08 L 516.48 91.2 L 492.48 91.2 L 492.48 67.08 L 467.76 25.92 L 467.76 7.2 L 491.76 7.2 L 491.76 22.56 L 504.48 45.72 L 517.2 22.56 L 517.2 7.2 L 541.2 7.2 L 541.2 26.04 L 516.48 67.08 Z
        M 546 38.28 L 559.08 25.2 L 596.28 25.2 L 609.36 38.28 L 609.36 78.12 L 596.28 91.2 L 559.08 91.2 L 546 78.12 L 546 38.28 Z
        M 569.28 70.32 L 569.28 46.08 L 586.08 46.08 L 586.08 70.32 L 569.28 70.32 Z
        M 664.44 83.04 L 656.28 91.2 L 635.04 91.2 L 621.96 78.12 L 621.96 25.2 L 645.24 25.2 L 645.24 69.6 L 658.8 69.6 L 661.56 67.2 L 661.56 25.2 L 684.84 25.2 L 684.84 91.2 L 664.44 91.2 L 664.44 83.04 Z
        M 721.32 72.36 L 721.32 91.2 L 698.04 91.2 L 698.04 1.2 L 721.32 1.2 L 721.32 46.08 L 734.76 33.6 L 734.76 25.2 L 758.04 25.2 L 758.04 40.2 L 743.04 53.28 L 759.24 74.76 L 759.24 91.2 L 735.96 91.2 L 735.96 80.16 L 727.32 67.08 L 721.32 72.36 Z
        M 793.92 25.2 L 793.92 91.2 L 770.64 91.2 L 770.64 25.2 L 793.92 25.2 Z
        M 793.92 0 L 793.92 18 L 770.64 18 L 770.64 0 L 793.92 0 Z" />
    </g>

    <!-- Word 2: Mark Darren — text element, revealed by clip-w2 -->
    <g clip-path="url(#clip-w2)">
      <text x="0" y="{MD_BASELINE}"
            font-family="'Nippo-Bold', sans-serif"
            font-size="{MD_FONT_SIZE}"
            font-weight="900"
            class="name-word">Mark Darren</text>
    </g>

    <!-- Cursor: solid red square, x position animated via SMIL -->
    <rect class="name-dot" y="{CURSOR_Y}" width="{CURSOR_W}" height="{CURSOR_H}">
      <animate attributeName="x"
        values="{smil_cx}"
        keyTimes="{smil_times}"
        calcMode="discrete"
        dur="{DUR_S:.3f}s"
        repeatCount="indefinite" />
    </rect>
  </g>

  <!-- Subtitle -->
  <g id="svgGroupSub" transform="translate(480, 210)">
    <text x="0" y="30" class="name-sub" text-anchor="middle">Web Developer | App Developer | Designer</text>
  </g>

</svg>
"""

# Compile and write all three versions
for mode, filename in [("dynamic", "banner.svg"), ("light", "banner-light.svg"), ("dark", "banner-dark.svg")]:
    svg_content = generate_banner_svg(mode)
    output_path = os.path.join(script_dir, "..", filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"SVG Compiled Successfully to {filename} ({mode} mode)")

# Bump cache-busting version in README.md
readme_path = os.path.join(script_dir, "..", "README.md")
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as f:
        readme_content = f.read()
    
    match = re.search(r"\?v=(\d+)", readme_content)
    if match:
        old_version = match.group(1)
        new_version = str(int(old_version) + 1)
        new_content = readme_content.replace(f"?v={old_version}", f"?v={new_version}")
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"README.md version bumped to v={new_version}")
    else:
        print("Could not find version parameter in README.md")

