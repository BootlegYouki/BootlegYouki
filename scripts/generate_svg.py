import base64
import os
import re
import urllib.request
import json

LANGUAGE_COLORS = {
    "TypeScript": "#3178c6",
    "JavaScript": "#f1e05a",
    "Rust": "#dea584",
    "Svelte": "#ff3e00",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "Python": "#3572A5",
    "Go": "#00ADD8",
    "C++": "#f34b7d",
    "C#": "#178600",
    "Java": "#b07219",
    "Ruby": "#701516",
    "PHP": "#4F5D95",
    "Vue": "#41b883",
    "Swift": "#f05138",
    "Kotlin": "#A97BFF",
    "Dart": "#00B4AB"
}

def get_github_languages(username, token):
    if not token:
        return {
            "TypeScript": 520000,
            "Rust": 310000,
            "Svelte": 170000
        }

    query = """
    query($username: String!) {
      user(login: $username) {
        repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
          nodes {
            languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
              edges {
                size
                node {
                  name
                }
              }
            }
          }
        }
      }
    }
    """
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": {"username": username}}).encode("utf-8"),
        headers={
            "Authorization": f"token {token}",
            "User-Agent": "GitHub-Action-Stats-Updater"
        }
    )
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            if "errors" in res_data:
                print("GraphQL errors:", res_data["errors"])
                return {"TypeScript": 520000, "Rust": 310000, "Svelte": 170000}

            lang_totals = {}
            repos = res_data["data"]["user"]["repositories"]["nodes"]
            for repo in repos:
                if not repo or not repo.get("languages"):
                    continue
                for edge in repo["languages"]["edges"]:
                    size = edge["size"]
                    name = edge["node"]["name"]
                    lang_totals[name] = lang_totals.get(name, 0) + size
            return lang_totals
    except Exception as e:
        print(f"Error calling GitHub GraphQL API for languages, using fallback: {e}")
        return {
            "TypeScript": 249000,
            "HTML": 238000,
            "JavaScript": 162000,
            "Svelte": 127000,
            "CSS": 110000,
            "PHP": 88000,
            "Visual Basic .NET": 26000
        }

# Load local token if present in scratch/.env (git-ignored)
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, ".env")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip() and not line.startswith("#") and "=" in line:
                key, val = line.strip().split("=", 1)
                os.environ[key.strip()] = val.strip()

github_token = os.getenv("GITHUB_TOKEN")
repo_slug = os.getenv("GITHUB_REPOSITORY")
username = repo_slug.split("/")[0] if repo_slug else "BootlegYouki"

print(f"Loading GitHub language stats for {username}...")
lang_stats = get_github_languages(username, github_token)

sorted_langs = sorted(lang_stats.items(), key=lambda x: x[1], reverse=True)
total_bytes = sum(val for name, val in sorted_langs)

if total_bytes == 0:
    sorted_langs = [("TypeScript", 52), ("Rust", 31), ("Svelte", 17)]
    total_bytes = 100

processed_langs = []
other_bytes = 0

for name, val in sorted_langs:
    pct = (val / total_bytes) * 100
    if pct >= 1.0 and name not in ("Visual Basic .NET", "Visual Basic"):
        processed_langs.append((name, pct, LANGUAGE_COLORS.get(name, "#8b949e")))
    else:
        other_bytes += val

if other_bytes > 0:
    other_pct = (other_bytes / total_bytes) * 100
    processed_langs.append(("Other", other_pct, "#8b949e"))

# Load fonts
script_dir = os.path.dirname(os.path.abspath(__file__))
nippo_path = os.path.join(script_dir, "..", "fonts", "Nippo-Bold.woff2")
with open(nippo_path, "rb") as f:
    nippo_base64 = base64.b64encode(f.read()).decode("utf-8")

jb_path = os.path.join(script_dir, "..", "fonts", "jetbrains-mono-latin-wght-normal.woff2")
with open(jb_path, "rb") as f:
    jb_base64 = base64.b64encode(f.read()).decode("utf-8")

# Read user SVGs from icons.md
icons_file_path = os.path.join(script_dir, "icons.md")
with open(icons_file_path, "r", encoding="utf-8") as f:
    raw_content = f.read()

svg_blocks = re.findall(r"(<svg[^>]*>.*?</svg>)", raw_content, re.DOTALL)

titles = [
    "React", "Svelte", "TypeScript", "Tauri", "Rust",
    "Expo", "Node.js", "PostgreSQL", "SQLite", "Supabase",
    "Electron", "Tailwind", "Vite"
]

if len(svg_blocks) != len(titles):
    print(f"Warning: Expected {len(titles)} SVGs, but found {len(svg_blocks)} in icons.md")

tools = []
for idx, title in enumerate(titles):
    if idx < len(svg_blocks):
        svg_str = svg_blocks[idx]
        vb_match = re.search(r'viewBox=["\']\s*([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s*["\']', svg_str)
        if vb_match:
            v_x, v_y, v_w, v_h = map(float, vb_match.groups())
        else:
            v_x, v_y, v_w, v_h = 0.0, 0.0, 256.0, 256.0

        inner_match = re.search(r'<svg[^>]*>(.*)</svg>', svg_str, re.DOTALL)
        inner_content = inner_match.group(1) if inner_match else ""

        if title == "Rust":
            inner_content = f'<g fill="#ce412b">{inner_content}</g>'
        elif title == "Expo":
            inner_content = inner_content.replace('fill="#000020"', 'fill="#ffffff"')
        elif title == "PostgreSQL":
            inner_content = f'<g fill="#336791">{inner_content}</g>'

        tools.append({"name": title, "v_x": v_x, "v_y": v_y, "v_w": v_w, "v_h": v_h, "content": inner_content})
    else:
        tools.append({"name": title, "v_x": 0.0, "v_y": 0.0, "v_w": 256.0, "v_h": 256.0, "content": ""})

# Card Layout
card_w = 62.0
card_h = 62.0
W_box = 42.0
H_box = 42.0
X_box_start = (card_w - W_box) / 2.0
Y_box_start = (card_h - H_box) / 2.0

panel_w = 920.0
N = len(tools)
gap_w = 8.0
grid_w = N * card_w + (N - 1) * gap_w
start_x = 20.0 + (panel_w - grid_w) / 2.0

ticker_elements = []

icon_filters = {8: "icon-brighten"}

for idx, tool in enumerate(tools):
    x_offset = start_x + idx * (card_w + gap_w)
    scale = min(W_box / tool["v_w"], H_box / tool["v_h"])
    w_scaled = tool["v_w"] * scale
    h_scaled = tool["v_h"] * scale
    dx = X_box_start + (W_box - w_scaled) / 2.0 - tool["v_x"] * scale
    dy = Y_box_start + (H_box - h_scaled) / 2.0 - tool["v_y"] * scale
    filter_attr = f' filter="url(#{icon_filters[idx]})"' if idx in icon_filters else ""
    element = f"""      <g transform="translate({x_offset:.2f}, 20)">
        <rect x="0" y="0" width="{card_w}" height="{card_h}" class="tui-border" />
        <g transform="translate({dx:.3f}, {dy:.3f}) scale({scale:.5f})"{filter_attr}>
          {tool["content"]}
        </g>
      </g>"""
    ticker_elements.append(element)

ticker_elements_str = "\n".join(ticker_elements)

# Stats Bar
bar_x = 20
bar_y = 372
bar_w = 920
bar_h = 10

bar_segments = []
legend_items = []
current_x = bar_x

gap = 26
item_widths = []
total_legend_w = 0
for name, pct, color in processed_langs:
    item_w = 12 + (len(name) + 6) * 7.5
    item_widths.append(item_w)
    total_legend_w += item_w
total_legend_w += (len(processed_langs) - 1) * gap

current_legend_x = 480 - (total_legend_w / 2)

for i, (name, pct, color) in enumerate(processed_langs):
    seg_w = (pct / 100) * bar_w
    bar_segments.append(f'<rect x="{current_x:.2f}" y="{bar_y}" width="{seg_w:.2f}" height="{bar_h}" fill="{color}" />')
    current_x += seg_w
    circle = f'<circle cx="{current_legend_x}" cy="{bar_y + 30}" r="5" fill="{color}" />'
    text   = f'<text x="{current_legend_x + 12}" y="{bar_y + 34}" class="ticker-text">{name} {pct:.1f}%</text>'
    legend_items.extend([circle, text])
    current_legend_x += item_widths[i] + gap

segments_str = "\n    ".join(bar_segments)
legend_str   = "\n    ".join(legend_items)

stats_panel_svg = f"""
  <!-- GitHub Stats Panel -->
  <g id="svgGroupStats">
    <rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" fill="#21262d" rx="3" />
    <g clip-path="url(#bar-clip)">
      {segments_str}
    </g>
    {legend_str}
  </g>
"""

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

svg_template = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="20 58 920 374" width="100%" height="100%" xmlns:xlink="http://www.w3.org/1999/xlink">
  <defs>
    <!-- Progress bar clip -->
    <clipPath id="bar-clip">
      <rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" rx="3" />
    </clipPath>
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
      @media (prefers-color-scheme: light) {{
        .name-word {{ fill: #24292f; }}
        .tui-legend {{ fill: #57606a; }}
        .name-sub   {{ fill: #24292f; }}
        .ticker-text{{ fill: #57606a; }}
      }}
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
            fill="#ffffff">Mark Darren</text>
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

  <!-- Tech Icons Row -->
  <g id="svgGroupTicker" transform="translate(0, 250)">
{ticker_elements_str}
  </g>

{stats_panel_svg}
</svg>
"""

output_svg_path = os.path.join(script_dir, "..", "banner.svg")
with open(output_svg_path, "w", encoding="utf-8") as f:
    f.write(svg_template)

print("SVG Compiled Successfully to static layout!")

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

