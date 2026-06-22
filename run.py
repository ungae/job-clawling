import os
import re
import yaml
from typing import List
from model import JobPosting
from crawler import search_site
from dashboard import generate_html

def load_config():
    with open('config.yaml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

# 신입/인턴/무관이 없고 경력만 명시된 공고는 제외
INCLUDE_WORDS = ['신입', '인턴', '경력무관', '무관']
CAREER_PATTERN = re.compile(r'경력\s*\d|경력직|경력자|경력\s*채용|경력\s*모집')

def is_career_only(p: JobPosting) -> bool:
    title = p.title
    # 포함 키워드가 있으면 유지
    if any(w in title for w in INCLUDE_WORDS):
        return False
    # 명확한 경력 패턴이 있으면 제외
    if CAREER_PATTERN.search(title):
        return True
    # 단순 '경력' 단어가 있어도 제외 (신입/인턴 없는 경우)
    if '경력' in title:
        return True
    return False

def main():
    cfg = load_config()
    keywords = cfg['keywords']
    all_posts: List[JobPosting] = []
    
    for site_key in cfg['sites']:
        for kw in keywords:
            posts = search_site(site_key, kw)
            all_posts.extend(posts)
    # deduplicate by (company, title, link)
    seen = set()
    uniq_posts: List[JobPosting] = []
    for p in all_posts:
        key = (p.company, p.title, p.link)
        if key not in seen:
            uniq_posts.append(p)
            seen.add(key)
    # 경력 전용 공고 제외
    before = len(uniq_posts)
    filtered_posts = [p for p in uniq_posts if not is_career_only(p)]
    print(f"[Filter] {before}개 수집 -> 경력 제외 후 {len(filtered_posts)}개")
    html = generate_html(filtered_posts, keywords)
    out_path = os.path.abspath('index.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"[Done] Open {out_path} in any web browser.")

if __name__ == '__main__':
    main()
