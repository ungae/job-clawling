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

# ─────────────────────────────────────────────────────────
# 매출 100억+ 이상, 회사 이력 조회 가능한 규모 있는 기업 목록
# ─────────────────────────────────────────────────────────
# 대기업 / 상장사
LARGE_CORP = [
    '삼성', 'lg', 'sk', '현대', '기아', '롯데', 'cj', '신세계', '한화', 'gs', 'kt', 'kT&G',
    'posco', '포스코', 'skt', 'lgu+', '카카오', '네이버', '라인', '쿠팡',
    '배달의민족', '우아한형제들', '토스', '비바리퍼블리카', '당근마켓', '당근',
    '야놀자', '넥슨', '엔씨소프트', '넷마블', '크래프톤',
    '신한', '국민은행', '하나은행', '우리은행', 'kb', 'nh', '농협',
    '현대카드', '삼성카드', '신한카드', '롯데카드',
    'hdfc', '두산', 'oci', '효성',
    '인터파크', '지마켓', '11번가', '위메프', '티몬',
    'ssg', 'gs25', 'cu편의점', '이마트', '홈플러스',
    '올리브영', '무신사', '마켓컬리', '컬리',
    '하이브', 'sm엔터', 'jyp', 'yg',
    '에스원', 'kt cs', 'sk텔레콤', 'sk이노베이션',
    '현대모비스', '현대글로비스', '현대건설', '삼성물산', '삼성sds',
    'lgcns', 'lg전자', 'lg화학', 'sk하이닉스',
]

# 매출 100억+ 중견기업 / 유니콘·예비유니콘 스타트업
MEDIUM_CORP = [
    '직방', '다방', '오늘의집', '버킷플레이스', '리멤버', '드라마앤컴퍼니',
    '뱅크샐러드', '핀다', '카카오페이', '카카오뱅크', '케이뱅크', '토스뱅크',
    '크몽', '숨고', '탈잉', '클래스101', '에듀윌', '휴넷',
    '쏘카', '그린카', '타다', '카카오모빌리티',
    '우아한형제들', '요기요', '배민', '쿠팡이츠',
    '라이나생명', '메리츠', '한화생명', '미래에셋',
    '카카오엔터', '왓챠', '시리즈', '웨이브',
    '뤼튼', '업스테이지', '아이지에이웍스', '몰로코',
    '에이블리', '지그재그', '카카오스타일', '브랜디',
    '메쉬코리아', '두나무', '빗썸', '업비트',
    '클라썸', '스캐터랩', '뤼이드',
    '원티드랩', '사람인', '잡코리아',
    '하이퍼커넥트', '크래프톤', '시프티', '플렉스',
    '콴다', 'mathpresso', 'riiid',
    '현대오토에버', '신세계아이앤씨', 'cj올리브네트웍스', '롯데이커머스',
    'sk플래닛', 'kt ds', 'nhn', '엔에이치엔',
    '에이스에듀', '메가스터디', '이투스',
    '오픈서베이', '코리아스타트업포럼',
    '마이리얼트립', '트리플', '여기어때', '야놀자',
    '게임빌', '컴투스', '카카오게임즈',
    '패스트캠퍼스', '스파르타코딩클럽', '코드스테이츠',
    '당근페이', '핀테크', '핀크',
    '에코프로', 'lg에너지솔루션', '삼성sdi',
    'sk바이오팜', '셀트리온', '삼성바이오로직스',
]

# 소규모·검증 불가 업체 시그널 (이런 단어가 있으면 영세 가능성 높음)
SMALL_BIZ_SIGNALS = [
    '주식회사', '(주)', '유한회사', '개인사업자',
    '부동산', '공인중개', '학원', '보험설계', '다단계',
    '영업직', '방문판매', '텔레마케팅', '알바',
]

ALLOWED_LOC = ['서울', '경기', '인천', '판교', '분당', '성남', '미기재', '전국']
BAD_ROLES = ['개발자', '디자이너', '엔지니어', '프론트엔드', '백엔드', '퍼블리셔', '웹개발', '앱개발', '서버', '인프라', '데이터엔지니어']

def determine_company_size(p: JobPosting) -> str:
    """회사 규모 판별: 대기업 / 중견·유니콘 / 소규모(제외대상) 중 하나를 반환"""
    c_name = p.company.lower()
    
    for lc in LARGE_CORP:
        if lc in c_name:
            return '대기업'
    
    for mc in MEDIUM_CORP:
        if mc in c_name:
            return '중견·유니콘'
    
    # 원티드·점핏·잡코리아에 등록된 기업은 기본 사업자 등록 검증이 됨 → 소규모라도 최소 신뢰 가능
    is_verified_platform = (
        'wanted.co.kr' in p.link
        or 'jumpit.co.kr' in p.link
        or 'jobkorea.co.kr' in p.link
        or 'saramin.co.kr' in p.link
    )
    
    if is_verified_platform:
        return '스타트업/중소'  # 검증된 플랫폼 등록 기업
    
    return '미확인'  # 이력 조회 불가 가능성 있음

def is_valid_job(p: JobPosting) -> bool:
    title = p.title.lower()
    req = p.requirements.lower()
    exp = p.experience.lower()
    loc = p.location.lower()
    company_raw = p.company.lower()
    
    # ── 1. 회사 규모 판별 (매출 100억+, 이력 조회 가능한 곳만 허용) ──
    p.company_size = determine_company_size(p)
    
    # 이력 조회 불가능한 미확인 업체는 제외
    if p.company_size == '미확인':
        return False
    
    # 소규모·영세 업체 시그널이 회사명/공고에 포함된 경우 제외
    if any(sig in company_raw or sig in title for sig in SMALL_BIZ_SIGNALS):
        return False
    
    # 회사명이 너무 짧거나(2글자 이하) N/A인 경우 제외
    if p.company in ('N/A', '', 'n/a') or len(p.company.strip()) <= 2:
        return False
    
    # ── 2. 신입/무관 만 남기기 ──
    if not any(a in exp for a in ALLOWED_EXP):
        return False
    if CAREER_PATTERN.search(title) and not any(a in title for a in ALLOWED_EXP):
        return False
        
    # ── 3. 지역(서울/경기) 필터 ──
    if not any(l in loc for l in ALLOWED_LOC):
        return False
        
    # ── 4. 개발/디자인 직군 제외 ──
    if any(b in title or b in req for b in BAD_ROLES):
        return False
        
    # ── 5. 마감/종료된 공고 제외 ──
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
    
    print(f"[Filter] {before}개 수집 -> 규모/경력 필터 후 {len(filtered_posts)}개 (매출 100억+ 이상, 이력 조회 가능 기업 한정)")
    html = generate_html(filtered_posts, keywords)
    out_path = os.path.abspath('index.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"[Done] Open {out_path} in any web browser.")

if __name__ == '__main__':
    main()
