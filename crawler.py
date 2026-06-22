import time
import json
import urllib.parse
from typing import List
import requests
from bs4 import BeautifulSoup
from model import JobPosting
import yaml

# Load configuration
with open('config.yaml', 'r', encoding='utf-8') as f:
    CONFIG = yaml.safe_load(f)

HEADERS = {
    'User-Agent': CONFIG['user_agent'],
    'Accept-Language': 'ko-KR,ko;q=0.9',
}

# ────────────────────────────────────────────
# 공통 fetch
# ────────────────────────────────────────────
def fetch_html(url: str) -> str:
    for attempt in range(3):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            time.sleep(1)
            return resp.text
        except Exception as e:
            if attempt == 2:
                raise e
            time.sleep(2 ** attempt)


def fetch_json(url: str) -> dict:
    for attempt in range(3):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            time.sleep(1)
            return resp.json()
        except Exception as e:
            if attempt == 2:
                raise e
            time.sleep(2 ** attempt)


# ────────────────────────────────────────────
# 사람인
# ────────────────────────────────────────────
def parse_saramin(html: str) -> List[JobPosting]:
    soup = BeautifulSoup(html, 'html.parser')
    postings: List[JobPosting] = []
    for item in soup.select('.item_recruit'):
        comp_tag     = item.select_one('.corp_name')
        title_tag    = item.select_one('.job_tit a')
        req_tag      = item.select_one('.job_sector')
        deadline_tag = item.select_one('.job_date .date')
        link_tag     = item.select_one('.job_tit a')
        company      = comp_tag.get_text(strip=True)     if comp_tag     else 'N/A'
        title        = title_tag.get_text(strip=True)    if title_tag    else 'N/A'
        requirements = req_tag.get_text(strip=True)      if req_tag      else 'N/A'
        deadline     = deadline_tag.get_text(strip=True) if deadline_tag else '상시'
        
        # 사람인은 보통 .job_condition 안의 span들에 [지역, 경력, 학력, 근무형태] 순으로 표시됨
        job_cond_tags = item.select('.job_condition span')
        location = '미기재'
        experience = '미기재'
        education = '미기재'
        if job_cond_tags:
            if len(job_cond_tags) > 0:
                location = job_cond_tags[0].get_text(strip=True)
            if len(job_cond_tags) > 1:
                experience = job_cond_tags[1].get_text(strip=True)
            if len(job_cond_tags) > 2:
                education = job_cond_tags[2].get_text(strip=True)
                
        link = (
            urllib.parse.urljoin('https://www.saramin.co.kr', link_tag['href'])
            if link_tag and link_tag.has_attr('href') else '#'
        )
        postings.append(JobPosting(company, title, requirements, deadline, link, experience, education, location))
    return postings


def crawl_saramin(keyword: str, max_results: int) -> List[JobPosting]:
    base = CONFIG['sites']['saramin'].format(keyword=urllib.parse.quote(keyword))
    postings: List[JobPosting] = []
    page = 1
    while len(postings) < max_results:
        url = f'{base}&recruitPage={page}'
        new = parse_saramin(fetch_html(url))
        if not new:
            break
        postings.extend(new)
        page += 1
    return postings[:max_results]


# ────────────────────────────────────────────
# 잡코리아
# ────────────────────────────────────────────
def parse_jobkorea(html: str) -> List[JobPosting]:
    soup = BeautifulSoup(html, 'html.parser')
    postings: List[JobPosting] = []
    for item in soup.select('.list-default li.post-list-corp'):
        comp_tag     = item.select_one('.name')
        title_tag    = item.select_one('.title')
        req_tag      = item.select_one('.etc')
        deadline_tag = item.select_one('.date')
        link_tag     = item.select_one('a.title')
        company      = comp_tag.get_text(strip=True)     if comp_tag     else 'N/A'
        title        = title_tag.get_text(strip=True)    if title_tag    else 'N/A'
        requirements = req_tag.get_text(strip=True)      if req_tag      else 'N/A'
        deadline     = deadline_tag.get_text(strip=True) if deadline_tag else '상시'
        
        exp_tag      = item.select_one('.option span.exp')
        edu_tag      = item.select_one('.option span.edu')
        loc_tag      = item.select_one('.option span.loc')
        experience   = exp_tag.get_text(strip=True) if exp_tag else '미기재'
        education    = edu_tag.get_text(strip=True) if edu_tag else '미기재'
        location     = loc_tag.get_text(strip=True) if loc_tag else '미기재'
        
        link = (
            urllib.parse.urljoin('https://www.jobkorea.co.kr', link_tag['href'])
            if link_tag and link_tag.has_attr('href') else '#'
        )
        postings.append(JobPosting(company, title, requirements, deadline, link, experience, education, location))
    return postings


def crawl_jobkorea(keyword: str, max_results: int) -> List[JobPosting]:
    postings: List[JobPosting] = []
    page = 1
    while len(postings) < max_results:
        url = CONFIG['sites']['jobkorea'].format(keyword=urllib.parse.quote(keyword), page=page)
        new = parse_jobkorea(fetch_html(url))
        if not new:
            break
        postings.extend(new)
        page += 1
    return postings[:max_results]


# ────────────────────────────────────────────
# 원티드 (JSON API)
# ────────────────────────────────────────────
def crawl_wanted(keyword: str, max_results: int) -> List[JobPosting]:
    postings: List[JobPosting] = []
    offset = 0
    per_page = 20
    while len(postings) < max_results:
        url = CONFIG['sites']['wanted'].format(
            keyword=urllib.parse.quote(keyword),
            offset=offset,
        )
        try:
            data = fetch_json(url)
        except Exception:
            break
        jobs = data.get('data', [])
        if not jobs:
            break
        for job in jobs:
            company = job.get('company', {}).get('name', 'N/A')
            title   = job.get('position', 'N/A')
            due_raw = job.get('due_time', '')
            deadline = due_raw[:10].replace('-', '.') if due_raw else '상시'
            cats = job.get('category_tags', [])
            requirements = ','.join(
                c.get('tag_name_ko', '') for c in cats if c.get('tag_name_ko')
            ) or 'N/A'
            job_id = job.get('id')
            link = f'https://www.wanted.co.kr/wd/{job_id}' if job_id else '#'
            experience = '무관/미기재'
            education = '무관/미기재'
            location = job.get('address', {}).get('location', '미기재')
            postings.append(JobPosting(company, title, requirements, deadline, link, experience, education, location))
        offset += per_page
        if len(jobs) < per_page:
            break
    return postings[:max_results]


# ────────────────────────────────────────────
# 링커리어 (__NEXT_DATA__ Apollo State)
# ────────────────────────────────────────────
def crawl_linkareer(keyword: str, max_results: int) -> List[JobPosting]:
    postings: List[JobPosting] = []
    page = 1
    while len(postings) < max_results:
        url = CONFIG['sites']['linkareer'].format(
            keyword=urllib.parse.quote(keyword),
            page=page,
        )
        try:
            html = fetch_html(url)
        except Exception:
            break
        soup = BeautifulSoup(html, 'html.parser')
        nd   = soup.find('script', id='__NEXT_DATA__')
        if not nd:
            break
        try:
            apollo = json.loads(nd.string)['props']['pageProps']['__APOLLO_STATE__']
        except (KeyError, json.JSONDecodeError):
            break

        new_count = 0
        for val in apollo.values():
            if not isinstance(val, dict) or val.get('__typename') != 'Activity':
                continue
            title        = val.get('title', 'N/A')
            company      = val.get('organizationName', 'N/A') or 'N/A'
            close_at = val.get('recruitCloseAt', '')
            if isinstance(close_at, int):
                from datetime import datetime, timezone
                deadline = datetime.fromtimestamp(close_at / 1000, tz=timezone.utc).strftime('%Y.%m.%d')
            elif isinstance(close_at, str) and close_at:
                deadline = close_at[:10].replace('-', '.')
            else:
                deadline = '상시'
            # categories는 __ref 리스트일 수 있음
            cats = val.get('categories', [])
            cat_names = []
            for c in cats:
                if isinstance(c, dict):
                    if 'name' in c:
                        cat_names.append(c['name'])
                    elif '__ref' in c:
                        ref_obj = apollo.get(c['__ref'], {})
                        cat_names.append(ref_obj.get('name', ''))
            requirements = ','.join(filter(None, cat_names)) or 'N/A'
            act_id = val.get('id')
            link   = f'https://linkareer.com/activity/{act_id}' if act_id else '#'
            experience = '신입/인턴'
            education = '무관/미기재'
            location = '미기재'
            postings.append(JobPosting(company, title, requirements, deadline, link, experience, education, location))
            new_count += 1

        if new_count == 0:
            break
        page += 1
    return postings[:max_results]


# ────────────────────────────────────────────
# 점핏 (JSON API)
# ────────────────────────────────────────────
def crawl_jumpit(keyword: str, max_results: int) -> List[JobPosting]:
    postings: List[JobPosting] = []
    page = 1
    while len(postings) < max_results:
        url = CONFIG['sites']['jumpit'].format(
            keyword=urllib.parse.quote(keyword),
            page=page
        )
        try:
            data = fetch_json(url)
        except Exception:
            break
        
        jobs = data.get('result', {}).get('positions', [])
        if not jobs:
            break
            
        for job in jobs:
            company = job.get('companyName', 'N/A')
            title = job.get('title', 'N/A')
            tech_stacks = job.get('techStacks', [])
            requirements = ','.join(tech_stacks) if tech_stacks else 'N/A'
            closed_at = job.get('closedAt', '')
            deadline = closed_at[:10].replace('-', '.') if closed_at else '상시'
            job_id = job.get('id')
            link = f'https://www.jumpit.co.kr/position/{job_id}' if job_id else '#'
            
            newcomer = job.get('newcomer', False)
            minCareer = job.get('minCareer', 0)
            maxCareer = job.get('maxCareer', 0)
            if newcomer:
                experience = '신입'
            elif minCareer > 0:
                experience = f'경력 {minCareer}~{maxCareer}년'
            else:
                experience = '경력무관'
            education = '무관/미기재'
            
            locations = job.get('locations', [])
            location = locations[0] if locations else '미기재'
            
            postings.append(JobPosting(company, title, requirements, deadline, link, experience, education, location))
            
        page += 1
    return postings[:max_results]


# ────────────────────────────────────────────
# 통합 진입점
# ────────────────────────────────────────────
CRAWLERS = {
    'saramin':   crawl_saramin,
    'jobkorea':  crawl_jobkorea,
    'wanted':    crawl_wanted,
    'linkareer': crawl_linkareer,
    'jumpit':    crawl_jumpit,
}

def search_site(site_key: str, keyword: str) -> List[JobPosting]:
    crawler = CRAWLERS.get(site_key)
    if crawler is None:
        return []
    # 한도를 대폭 상향하여 사실상 무제한으로 수집 (키워드/사이트당 최대 200개 제한으로 무한 루프 방지)
    per_kw = 200
    return crawler(keyword, per_kw)
