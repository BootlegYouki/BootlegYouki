import os
import urllib.request
import json
import base64
import re

def get_wakatime_stats(api_key):
    # Encode API key for Basic Auth
    auth_str = base64.b64encode(api_key.encode('utf-8')).decode('utf-8')
    req = urllib.request.Request(
        "https://wakatime.com/api/v1/users/current/stats/last_7_days",
        headers={"Authorization": f"Basic {auth_str}"}
    )
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Error fetching stats from WakaTime: {e}")
        return None

def make_bar_chart(percent, size=20):
    filled = int(round((percent / 100) * size))
    empty = size - filled
    return "█" * filled + "░" * empty

def generate_stats_markdown(data):
    if not data or "data" not in data:
        return "No stats available"
    
    languages = data["data"].get("languages", [])
    if not languages:
        return "No coding activity recorded in the last 7 days."
    
    lines = ["```text"]
    for lang in languages[:5]:  # Top 5 languages
        name = lang["name"].ljust(12)
        bar = make_bar_chart(lang["percent"])
        pct = f"{lang['percent']:.1f}%".rjust(6)
        time_str = lang["text"]
        lines.append(f"{name} {bar} {pct} ({time_str})")
    lines.append("```")
    return "\n".join(lines)

def update_readme(stats_markdown):
    readme_path = "README.md"
    if not os.path.exists(readme_path):
        print("README.md not found.")
        return
        
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    pattern = r"(<!-- WAKATIME_START -->)(.*?)(<!-- WAKATIME_END -->)"
    replacement = f"\\1\n{stats_markdown}\n\\3"
    
    # Check if markers exist
    if not re.search(pattern, content, re.DOTALL):
        # Append to end of file if markers don't exist
        content += f"\n\n<!-- WAKATIME_START -->\n{stats_markdown}\n<!-- WAKATIME_END -->\n"
    else:
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("README.md updated with WakaTime stats.")

def main():
    api_key = os.getenv("WAKATIME_API_KEY")
    if not api_key:
        print("WAKATIME_API_KEY environment variable not set.")
        return
        
    data = get_wakatime_stats(api_key)
    if data:
        stats_md = generate_stats_markdown(data)
        update_readme(stats_md)

if __name__ == "__main__":
    main()
