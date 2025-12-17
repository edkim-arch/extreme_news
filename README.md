# 관심 제품 뉴스 모니터링 (Python Serverless Ver.)

네이버 뉴스 API를 활용하여 10+1개 관심 키워드의 최근 14일 기사를 모니터링하는 웹 대시보드입니다.  
Vercel 배포에 최적화된 구조로 작성되었습니다.

## 📁 프로젝트 구조
```
news_dashboard_lite/
├── index.html        # Frontend: UI 및 로직
├── local_server.py   # Local: 로컬 실행용 파이썬 서버
├── requirements.txt  # Vercel: 파이썬 의존성 (표준 라이브러리만 사용하여 비어있음)
├── vercel.json       # Vercel: 설정 파일
└── api/
    └── news.py       # Backend: 네이버 API 호출 Serverless Function
```

## 🚀 로컬 실행 방법 (Windows)

1. **상위 폴더에 .env 파일 확인**  
   현재 폴더(`news_dashboard_lite`)의 **상위 폴더**(`..`)에 `.env` 파일이 있어야 합니다.
   ```
   NAVER_CLIENT_ID=your_id
   NAVER_CLIENT_SECRET=your_secret
   ```

2. **서버 실행**
   별도의 설치 과정 없이, Python만 설치되어 있다면 바로 실행 가능합니다.
   ```powershell
   # 프로젝트 폴더로 이동
   cd d:\test\naver_api\news_dashboard_lite

   # 서버 실행
   python local_server.py
   ```

3. **웹 접속**
   브라우저에서 `http://localhost:8000` 접속

## ☁️ Vercel 배포 방법

사내 공유를 위해 Vercel에 배포하려면 다음 절차를 따르세요.

1. **GitHub 업로드**
   이 폴더(`news_dashboard_lite`)를 GitHub 리포지토리로 푸시합니다.

2. **Vercel 프로젝트 생성**
   - Vercel Dashboard에서 "Add New Project" -> GitHub 리포지토리 선택.
   - **Root Directory** 설정: 리포지토리 루트가 아니라 `news_dashboard_lite` 폴더인 경우, "Edit"를 눌러 해당 폴더를 Root로 지정해야 합니다.

3. **환경 변수 설정 (중요)**
   Vercel 배포 설정 화면의 **Environment Variables** 섹션에 네이버 API 키를 등록합니다.
   - `NAVER_CLIENT_ID`: (값 입력)
   - `NAVER_CLIENT_SECRET`: (값 입력)

4. **Deploy**
   배포 버튼 클릭 후 약 1분 뒤 생성된 URL을 사내에 공유합니다.

## 🛠 기능 명세
- **키워드**: 아르기닌, 블랙마카, 단백질쉐이크, 에너지젤, 모노크레아틴, 올인원포맨, 밀크씨슬, 오메가3, 쏘팔메토, 프로바이오틱스, 김종국
- **필터링**: 최근 14일 이내 (`pubDate` 기준)
- **정렬**: 최신순 (내림차순)
- **중복 제거**: 동일 링크 혹은 동일 제목(HTML 태그 제거 후 비교) 시 최신 기사 유지
