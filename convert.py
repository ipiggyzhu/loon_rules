import requests
import os
from datetime import datetime, timezone, timedelta

# --- 核心配置区 ---
# 在这里定义您想生成的所有规则文件
# 每个条目代表一个输出文件
CONFIG = {
    "ad-rules.list": {
        "title": "My Custom Ad Rules for Loon",
        "sources": [
            # 您可以添加任意多个去广告规则源
            "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/SpywareFilter/sections/tracking_servers.txt",
            "https://raw.githubusercontent.com/privacy-protection-tools/anti-ad/master/anti-ad-adguard.txt",
            "https://raw.githubusercontent.com/damengzhu/banad/main/jiekouAD.txt"
        ],
        "rule_template": "DOMAIN-SUFFIX,{domain},REJECT"
    },
    "direct-rules.list": {
        "title": "My Custom Direct Rules for Loon",
        "sources": [
            # 您可以添加任意多个直连规则源
            "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Loon/Direct/Direct.list"
        ],
        "rule_template": "DOMAIN-SUFFIX,{domain},DIRECT"
    }
    # 添加代理规则，只需在这里新增一个条目，例如：
    # "proxy-rules.list": {
    #     "title": "My Custom Proxy Rules for Loon",
    #     "sources": ["https://some/proxy/list.txt"],
    #     "rule_template": "DOMAIN-SUFFIX,{domain},PROXY"
    # }
}

def fetch_source(url):
    """从 URL 获取内容并按行分割"""
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        print(f"✅ Fetched {url}")
        return response.text.split('\n')
    except requests.RequestException as e:
        print(f"❌ Error fetching {url}: {e}")
        return []

def parse_to_domain_set(lines):
    """解析行并提取域名到集合中以自动去重"""
    domains = set()
    for line in lines:
        # 移除行内注释和多余空格
        line = line.split('#')[0].strip()
        
        # 跳过注释、空行和特殊规则
        if not line or line.startswith(('!', '[', '/')):
            continue
        
        # 兼容不同格式
        if line.startswith('||') and line.endswith('^'): # Adblock Plus
            domain = line[2:-1]
        elif ' ' in line and not line.startswith('DOMAIN-'): # Hosts file
            domain = line.split()[1]
        elif line.startswith('DOMAIN-SUFFIX,'): # Loon/Quantumult X rule
            domain = line.split(',')[1]
        else:
            domain = line # Plain domain list

        # 清理域名并添加
        domain = domain.strip().lower()
        if domain:
            domains.add(domain)
    return domains

def main():
    """主执行函数"""
    for filename, config in CONFIG.items():
        print(f"\n--- Generating {filename} ---")
        
        all_domains = set()
        for url in config["sources"]:
            lines = fetch_source(url)
            domains = parse_to_domain_set(lines)
            all_domains.update(domains)
        
        if not all_domains:
            print(f"⚠️ No domains found for {filename}, skipping generation.")
            continue

        # 生成文件头
        beijing_time = datetime.now(timezone(timedelta(hours=8)))
        update_time = beijing_time.strftime('%Y-%m-%d %H:%M:%S')
        
        header = f"""# Title: {config['title']}
# Last Updated: {update_time} (Asia/Shanghai)
# Total Rules: {len(all_domains)}
# Sources:
"""
        for url in config["sources"]:
            header += f"# - {url}\n"
        
        # 写入文件
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(header + '\n')
            # 排序以保证每次生成的文件内容一致，便于版本控制
            for domain in sorted(list(all_domains)):
                f.write(config["rule_template"].format(domain=domain) + '\n')
        
        print(f"🎉 Successfully generated {filename} with {len(all_domains)} rules.")

if __name__ == "__main__":
    main()
