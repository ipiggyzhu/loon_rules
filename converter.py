# converter.py
import requests
import os
from datetime import datetime, timezone, timedelta

# --- 配置需要转换的复杂规则源 ---
SOURCES_TO_CONVERT = [
    # 可以添加多个
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/SpywareFilter/sections/tracking_servers.txt",
    "https://raw.githubusercontent.com/privacy-protection-tools/anti-ad/master/anti-ad-adguard.txt",
    "https://raw.githubusercontent.com/damengzhu/banad/main/jiekouAD.txt"
]
OUTPUT_FILE = "generated/converted-ad-rules.list" # 输出到新文件夹

def fetch_source(url):
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        print(f"✅ Fetched {url}")
        return response.text.split('\n')
    except requests.RequestException as e:
        print(f"❌ Error fetching {url}: {e}")
        return []

def parse_to_domain_set(lines):
    domains = set()
    for line in lines:
        line = line.split('#')[0].strip()
        if not line or line.startswith(('!', '[', '/')):
            continue
        
        if line.startswith('||') and line.endswith('^'):
            domain = line[2:-1]
        elif ' ' in line and not line.startswith('DOMAIN-'):
            domain = line.split()[1]
        else:
            domain = line
        
        domain = domain.strip().lower()
        if domain:
            domains.add(domain)
    return domains

def main():
    print("--- Starting Conversion Process ---")
    all_domains = set()
    for url in SOURCES_TO_CONVERT:
        lines = fetch_source(url)
        domains = parse_to_domain_set(lines)
        all_domains.update(domains)

    # 确保输出目录存在
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    # 写入文件
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        # 这个文件不需要复杂的头部，因为它只是一个中间产物
        f.write(f"# This file is auto-generated from multiple sources by converter.py\n")
        f.write(f"# Total unique domains: {len(all_domains)}\n\n")
        for domain in sorted(list(all_domains)):
            # 输出为最干净的 Loon 格式
            f.write(f"DOMAIN-SUFFIX,{domain},REJECT\n")
    
    print(f"🎉 Successfully generated {OUTPUT_FILE} with {len(all_domains)} rules.")

if __name__ == "__main__":
    main()
