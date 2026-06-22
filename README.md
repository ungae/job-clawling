# 📊 채용 대시보드 프로젝트

## 1️⃣ 파이썬 설치하기
1. https://www.python.org/downloads/windows/ 로 이동해 **Python 3.12** (또는 최신 버전) 설치 파일을 다운로드합니다.
2. 설치 화면에서 **"Add Python to PATH"** 옵션을 반드시 체크하고 **"Install Now"** 를 눌러 설치합니다.
3. 설치가 끝나면 **PowerShell**(또는 명령 프롬프트)를 열고 아래 명령을 입력해 버전을 확인합니다.
```
python --version
```
`Python 3.x.x` 라고 나오면 성공!

## 2️⃣ 프로젝트 폴더 만들기
```powershell
mkdir C:\\socialism_experience_app
cd C:\\socialism_experience_app
```

## 3️⃣ 파일 복사하기
아래 파일들을 그대로 복사해서 같은 폴더에 저장합니다.
| 파일 | 역할 |
|------|------|
| `config.yaml` | 검색 키워드·사이트·최대 결과 수·User‑Agent 설정 |
| `requirements.txt` | 파이썬 의존성 목록 |
| `model.py` | `JobPosting` 데이터 클래스를 정의 |
| `crawler.py` | 웹 페이지 요청·HTML 파싱·크롤링 로직 |
| `dashboard.py` | 차트와 표가 포함된 HTML 생성 |
| `run.py` | 전체 흐름을 연결하고 `job_dashboard.html` 생성 |
| `README.md` | 이 가이드 (현재 파일) |
| `.gitignore` | `__pycache__/` 와 생성된 HTML을 Git에 포함하지 않게 함 |

## 4️⃣ 의존성 설치하기
프로젝트 폴더 안에서 아래 명령을 실행합니다.
```
pip install -r requirements.txt
```
잠시 후 `requests`, `beautifulsoup4`, `pyyaml` 가 설치됩니다.

## 5️⃣ 스크립트 실행하기
```
python run.py
```
스크립트가 끝나면 다음과 같은 메시지가 보입니다.
```
✅ Done! Open C:\\socialism_experience_app\\job_dashboard.html in any web browser.
```

## 6️⃣ 결과 확인하기
파일 탐색기에서 `job_dashboard.html`을 더블 클릭하거나, 웹 브라우저(Chrome, Edge, Firefox 등)에서 열어 주세요.
- **막대 차트** : 6개의 키워드(서비스 기획, 프로덕트 매니저, PM, 퍼포먼스 마케팅, 콘텐츠 마케터, 디지털 마케팅)가 각각 몇 개의 채용 공고에 들어갔는지 표시합니다.
- **표** : 회사명, 공고 제목, 주요 요구 역량, 마감일, 상세 링크가 **마감일 순**(가장 빨리 마감되는 순)으로 정렬되어 나타납니다.

## 7️⃣ 설정 바꾸기
- **키워드 추가·제거** : `config.yaml` 의 `keywords:` 리스트를 편집합니다.
- **최대 크롤링 수** : `max_results:` 값을 원하는 숫자로 바꿉니다.
- **다른 사이트 추가** : `sites:` 에 새로운 URL 템플릿을 넣고, `crawler.py`에 해당 사이트를 파싱하는 함수를 추가하면 됩니다.

## 8️⃣ 자주 묻는 질문(FAQ)
- **왜 1초 딜레이가 있나요?**
  - 사이트에 과도한 요청을 보내면 차단당하거나 서버에 부담을 줄 수 있어요. 최소한의 딜레이를 두어 예의를 지킵니다.
- **HTML이 안 뜨면?**
  - 콘솔에 에러 메시지가 있나요? 에러 내용을 알려 주시면 돕겠습니다.
- **키워드가 표에 안 보이면?**
  - 해당 키워드가 현재 검색된 공고의 제목·요구사항에 포함되어 있지 않을 수 있습니다.

---

🎉 **이제 채용 정보를 한눈에 볼 수 있는 대시보드가 준비되었습니다!**
궁금한 점이 있으면 언제든 물어보세요.
