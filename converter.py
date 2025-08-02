import requests
import os

# --- 配置区 ---
SOURCES_TO_CONVERT = [
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/SpywareFilter/sections/tracking_servers.txt",
    "https://raw.githubusercontent.com/privacy-protection-tools/anti-ad/master/anti-ad-adguard.txt",
    "https://raw.githubusercontent.com/damengzhu/banad/main/jiekouAD.txt"
]
OUTPUT_FILE = "generated/converted-ad-rules.list"

def main():
    print("--- Starting Conversion Process ---")
    all_rules = set()
    for url in SOURCES_TO_CONVERT:
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            print(f"✅ Fetched {url}")
            lines = response.text.split('\n')
            for line in lines:
                # 跳过注释和空行
                line = line.split('#')[0].strip()
                if not line or line.startswith(('!', '[', '/')):
                    continue
                
                # 关键逻辑：智能生成干净的Loon规则，不再包含任何策略
                parts = line.split(',')
                # Adblock Plus 格式 (||example.com^) -> DOMAIN-SUFFIX,example.com
                if line.startswith('||') and line.endswith('^'):
                    domain = line[2:-1]
                    rule = f"DOMAIN-SUFFIX,{domain.strip().lower()}"
                # 已有的Loon/QX格式 (DOMAIN-SUFFIX,example.com,REJECT) -> DOMAIN-SUFFIX,example.com
                elif len(parts) >= 2 and parts[0].strip().upper().startswith('DOMAIN'):
                    rule = f"{parts[0].strip().upper()},{parts[1].strip().lower()}"
                # 纯域名格式 (example.com) -> DOMAIN-SUFFIX,example.com
                else:
                    rule = f"DOMAIN-SUFFIX,{line.strip().lower()}"
                
                all_rules.add(rule)
        except requests.RequestException as e:
            print(f"❌ Error fetching {url}: {e}")

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"# Auto-generated converter.py\n")
        f.write(f"# Total unique rules: {len(all_rules)}\n\n")
        for rule in sorted(list(all_rules)):
            f.write(f"{rule}\n")
    print(f"🎉 Generated {OUTPUT_FILE} with {len(all_rules)} rules.")

if __name__ == "__main__":
    main()
