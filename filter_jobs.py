import json

def main():
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # Extract ALL_JOBS data
    start_idx = html.find('const ALL_JOBS   = [')
    if start_idx == -1:
        start_idx = html.find('const ALL_JOBS = [')
    if start_idx == -1:
        print("Could not find job data.")
        return
        
    start_idx += html[start_idx:].find('[')
    end_idx = html.find('];', start_idx) + 1
    
    jobs_json = html[start_idx:end_idx]
    try:
        jobs = json.loads(jobs_json)
    except Exception as e:
        print("JSON parse error:", e)
        return

    # Scoring logic
    # Key portfolio strengths: AI Agent, GenAI, LLM, Senior Service, Platform/Community, PM, Service Planning
    
    high_keywords = ['ai', 'llm', '에이전트', '생성형', '시니어', 'pm', '프로덕트', '기획', '플랫폼', '커뮤니티']
    exclude_keywords = ['영업', '마케팅', '디자인', '백엔드', '프론트엔드', '개발자', '엔지니어', '세일즈', '회계', '재무', '인사']
    
    scored_jobs = []
    
    for job in jobs:
        score = 0
        title = job.get('title', '').lower()
        req = job.get('requirements', '').lower()
        
        # Base exclusion (if purely dev or sales and not PM/Planning)
        if any(ex in title for ex in exclude_keywords):
            if not any(hk in title for hk in ['pm', '기획', '프로덕트']):
                continue
                
        # Scoring Title
        for hk in high_keywords:
            if hk in title:
                score += 5
                
        # Scoring Requirements
        for hk in high_keywords:
            if hk in req:
                score += 2
                
        if score > 0:
            scored_jobs.append((score, job))
            
    scored_jobs.sort(key=lambda x: x[0], reverse=True)
    top_jobs = scored_jobs[:30]
    
    with open('top_jobs_output.json', 'w', encoding='utf-8') as f:
        json.dump([j[1] for j in top_jobs], f, ensure_ascii=False, indent=2)
        
    print(f"Scored {len(scored_jobs)} jobs. Top 30 saved to top_jobs_output.json")

if __name__ == '__main__':
    main()
