# AI Health Web Assignment

흉부 X-Ray 이미지를 활용한 폐렴 판독 백오피스 시스템입니다.

## 팀 구성

| 이름 | 담당 기능 |
|------|-----------|
| 박소정 (pecs0310) | 사용자 관리 API (REQ-USER-001~009) |
| 박지은 | 환자 관리 API (REQ-PTNT-001~005) |
| 홍현정 | 진료기록 관리 API (REQ-MDR-001~003) |

---

## 프로젝트 진행 과정

### 1. Team Rule 정의

- **브랜치 전략**: GitHub Flow 사용
  - `main` 브랜치를 기준으로 `feature/기능명` 브랜치를 생성하여 작업
  - 작업 완료 후 PR을 통해 `main` 브랜치로 머지
- **커밋 컨벤션**:
  - `feat`: 새로운 기능 추가
  - `fix`: 버그 수정
  - `docs`: 문서 작성/수정
  - `chore`: 설정 변경
- **코드 리뷰**: PR 생성 후 팀원 검토 후 머지

### 2. 사용자 요구사항 정의

요구사항 정의서를 기반으로 3가지 도메인으로 분리:

- **사용자 관리** (REQ-USER): 회원가입, 로그인, 마이페이지, 권한 관리
- **환자 관리** (REQ-PTNT): 환자 등록, 조회, 수정, 삭제
- **진료기록 관리** (REQ-MDR): 진료기록 등록, X-Ray 업로드, AI 폐렴 예측
- **AI 폐렴 예측** (REQ-PRED): 폐렴 예측 결과 조회, 캐싱

### 3. API 명세서 작성

각 담당자가 API 명세서를 작성하여 `Docs/` 폴더에 업로드:

- `Docs/4일차_USER_API_설계.md` - 사용자 관리 API
- `Docs/5일차_환자관리_API_설계.md` - 환자 관리 API
- `Docs/6일차_폐렴예측_API_설계.md` - AI 폐렴 예측 API

### 4. Git & GitHub Branch 전략

**GitHub Flow** 채택:

```
main
 ├── feature/user-api       # 사용자 관리 API
 ├── feature/patient        # 환자 관리 API
 ├── feature/record         # 진료기록 API
 ├── feature/docker         # Docker 설정
 ├── feature/redis-worker   # Redis Worker 아키텍처
 └── feature/eda-architecture # EDA 설계 문서
```

### 5. 프로젝트 세팅

**기술 스택:**

| 구분 | 기술 |
|------|------|
| Backend | FastAPI (Python ≥ 3.13) |
| Database | MySQL 8.0 |
| ORM | SQLAlchemy (비동기) |
| Migration | Alembic |
| 인증 | JWT (액세스토큰 30분) |
| 패키지 관리 | uv |
| 컨테이너 | Docker + Docker Compose |
| 메시지 브로커 | Redis 7 |
| AI 프레임워크 | PyTorch + timm |

**환경 설정:**
```bash
# 의존성 설치
uv sync

# DB 마이그레이션
uv run alembic upgrade head

# 서버 실행
uv run uvicorn app.main:app --reload
```

### 6. API 및 AI 워커 코드 작성

**구현된 API 목록:**

- **사용자 관리** (9개): 회원가입, 로그인, 로그아웃, 마이페이지, 정보수정, 비밀번호변경, 권한변경, 회원목록, 탈퇴
- **환자 관리** (6개): 환자 등록/조회/수정/삭제, 환자별 진료기록 조회
- **진료기록 관리** (4개): 진료기록 등록/조회, AI 예측 요청, 예측 결과 목록

**AI 워커:**
- `worker/inference.py`: FastViT-SA12 앙상블 모델 (5-Fold) 추론
- `worker/main.py`: Redis 큐에서 작업을 받아 추론 후 결과 발행

### 7. 아키텍처 설계 및 적용

**Event-Driven Architecture (EDA) 도입:**

동시 요청 처리 문제 해결을 위해 FastAPI와 AI Worker를 분리:

```
[클라이언트] → [FastAPI] → [Redis Queue] → [AI Worker] → [MySQL]
                  ↑ 즉시 응답                    ↑ 비동기 처리
```

- FastAPI: 요청 접수 및 Redis 큐에 작업 등록
- Redis: 작업 대기열 관리 (Pub/Sub)
- AI Worker: 큐에서 작업을 꺼내 PyTorch 모델로 추론 후 결과 발행

### 8. 도커 인프라 관련 파일 작성

**컨테이너 구성:**

```yaml
services:
  fastapi:   # FastAPI 서버 (포트 8000)
  mysql:     # MySQL 8.0 (포트 3307)
  redis:     # Redis 7 (포트 6379)
  ai-worker: # AI 추론 워커
```

**실행 방법:**
```bash
# 전체 서비스 실행
docker compose up

# Redis만 실행
docker compose up -d redis

# 이미지 빌드
docker compose build
```

### 9. AWS 배포

> 추후 진행 예정

### 10. QA 진행

**Swagger UI 테스트** (`http://localhost:8000/docs`):

| API | 테스트 결과 |
|-----|------------|
| 회원가입 | ✅ 201 |
| 로그인 | ✅ 200 + JWT 토큰 |
| 마이페이지 조회 | ✅ 200 |
| 정보 수정 | ✅ 200 |
| 비밀번호 변경 | ✅ 200 |
| Admin 권한 확인 | ✅ 403 |
| 로그아웃 | ✅ 200 |
| 회원 탈퇴 | ✅ 200 |

---

## 프로젝트 구조

```
proj_fastapi/
├── app/
│   ├── apis/          # API 라우터
│   ├── core/          # 설정, DB, 보안, Redis 클라이언트
│   ├── models/        # SQLAlchemy 모델
│   ├── repositories/  # DB 쿼리
│   ├── schemas/       # Pydantic 스키마
│   ├── services/      # 비즈니스 로직
│   └── main.py
├── worker/
│   ├── inference.py   # AI 모델 추론
│   ├── main.py        # Redis Worker
│   ├── redis_client.py
│   └── models/        # .pth 모델 파일
├── Docs/              # API 명세서 및 테스트 문서
├── alembic/           # DB 마이그레이션
├── docker-compose.yml
└── pyproject.toml
```

---

## Alembic Migration Guide

### 1. 마이그레이션 파일 생성
```bash
uv run alembic revision --autogenerate -m "변경 내용 설명"
```

### 2. 데이터베이스에 반영
```bash
uv run alembic upgrade head
```

### 3. 이전 상태로 되돌리기
```bash
uv run alembic downgrade -1
```
