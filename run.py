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

# 신입/인턴/무관 허용어 (이외 경력은 제외)
ALLOWED_EXP = ['신입', '무관', '인턴', '미기재']
CAREER_PATTERN = re.compile(r'경력\s*\d|경력직|경력자|경력\s*채용|경력\s*모집')

LARGE_CORP = ['삼성', 'lg', 'sk', '현대', '기아', '롯데', 'cj', '신세계', '한화', 'gs', 'kt', '카카오', '네이버', '라인', '쿠팡', '배달의민족', '우아한형제들', '토스', '비바리퍼블리카', '당근', '야놀자', '넥슨', '엔씨소프트', '넷마블', '신한', '국민', '하나은행', '우리은행']
ALLOWED_LOC = ['서울', '경기', '인천', '판교', '분당', '성남', '미기재', '전국']
BAD_ROLES = ['개발자', '디자이너', '엔지니어', '프론트엔드', '백엔드', '퍼블리셔', '웹개발', '앱개발', '서버', '인프라', '데이터엔지니어']

def determine_company_size(p: JobPosting) -> str:
    c_name = p.company.lower()
    for lc in LARGE_CORP:
        if lc in c_name:
            return '대기업'
    
    is_startup_site = 'wanted.co.kr' in p.link or 'jumpit.co.kr' in p.link
    if is_startup_site or '랩스' in c_name or '스튜디오' in c_name or '컴퍼니' in c_name or '코퍼레이션' in c_name:
        return '스타트업'
        
    return '중소/중견'

def is_valid_job(p: JobPosting) -> bool:
    title = p.title.lower()
    req = p.requirements.lower()
    exp = p.experience.lower()
    loc = p.location.lower()
    
    # 1. 대기업 제외
    p.company_size = determine_company_size(p)
    if p.company_size == '대기업':
        return False
        
    # 2. 신입/무관 만 남기기
    if not any(a in exp for a in ALLOWED_EXP):
        return False
    if CAREER_PATTERN.search(title) and not any(a in title for a in ALLOWED_EXP):
        return False
        
    # 3. 지역(서울/경기) 필터
    if not any(l in loc for l in ALLOWED_LOC):
        return False
        
    # 4. 개발/디자인 제외
    if any(b in title or b in req for b in BAD_ROLES):
        return False
        
    # 5. 마감/종료된 공고 제외
    dl = p.deadline.lower()
    if '마감' in dl or '종료' in dl:
        return False
        
    # 날짜(YYYY.MM.DD)인 경우 과거 날짜인지 확인
    import re, datetime
    match = re.search(r'(\d{4})[./-](\d{1,2})[./-](\d{1,2})', dl)
    if match:
        try:
            y, m, d = map(int, match.groups())
            deadline_date = datetime.date(y, m, d)
            if deadline_date < datetime.date.today():
                return False
        except ValueError:
            pass
            
    return True

def score_job(p: JobPosting) -> int:
    score = 0
    title = p.title.lower()
    req = p.requirements.lower()
    
    high_keywords = ['ai', 'llm', '에이전트', '생성형', '시니어', 'pm', '프로덕트', '기획', '플랫폼']
    exclude_keywords = ['영업', '마케팅', '디자인', '백엔드', '프론트엔드', '개발자', '엔지니어', '세일즈', '회계', '재무', '인사']
    
    if any(ex in title for ex in exclude_keywords):
        if not any(hk in title for hk in ['pm', '기획', '프로덕트']):
            return -100
            
    for hk in high_keywords:
        if hk in title:
            score += 5
            
    for hk in high_keywords:
        if hk in req:
            score += 2
            
    return score

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
    # 강력 필터링 (신입/무관, 지역, 대기업제외, 요건제외)
    before = len(uniq_posts)
    filtered_posts = [p for p in uniq_posts if is_valid_job(p)]
    
    # 스코어링 및 정렬
    for p in filtered_posts:
        p.score = score_job(p)
        
    filtered_posts.sort(key=lambda x: x.score, reverse=True)
    
    print(f"[Filter] {before}개 수집 -> 경력 제외 후 {len(filtered_posts)}개")
    html = generate_html(filtered_posts, keywords)
    out_path = os.path.abspath('index.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"[Done] Open {out_path} in any web browser.")

if __name__ == '__main__':
    main()
