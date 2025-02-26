# API Gateway 서비스

API Gateway 서비스는 New Data Collector의 모든 클라이언트 요청에 대한 단일 진입점을 제공합니다.

## 구조

```text
api-gateway/
├── app/
│   ├── __init__.py
│   ├── config.py                # 설정 관리
│   ├── main.py                  # 애플리케이션 진입점
│   ├── middleware/              # 미들웨어
│   │   ├── __init__.py
│   │   ├── auth.py              # 인증 미들웨어
│   │   ├── logging.py           # 로깅 미들웨어
│   │   └── rate_limit.py        # 속도 제한 미들웨어
│   ├── proxy/                   # 프록시 기능
│   │   ├── __init__.py
│   │   └── service_proxy.py     # 서비스 프록시
│   ├── routes/                  # 라우트
│   │   ├── __init__.py
│   │   └── api.py               # API 라우트
│   └── utils/                   # 유틸리티
│       ├── __init__.py
│       └── logging_config.py    # 로깅 설정
├── Dockerfile                   # 프로덕션 Dockerfile
├── Dockerfile.dev               # 개발 Dockerfile
├── requirements.txt             # 기본 의존성
├── requirements.dev.txt         # 개발 의존성
└── README.md                    # 문서
```

## 주요 기능

- 요청 라우팅 및 로드 밸런싱
- 인증 토큰 검증
- 속도 제한(Rate Limiting) 적용
- 요청/응답 로깅
- 서비스 디스커버리 통합
- API 문서화

## 기술 스택

- FastAPI: 고성능 웹 프레임워크
- HTTPX: 비동기 HTTP 클라이언트
- Redis: 속도 제한 구현
- Prometheus: 메트릭 수집
- JWT: 토큰 기반 인증

## 개발 환경 설정

### 요구 사항

- Python 3.11 이상
- Docker 및 Docker Compose

### 로컬 실행

1. 가상 환경 설정 (선택 사항)

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

2. 의존성 설치

```bash
pip install -r requirements.dev.txt
```

3. 서비스 실행

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker로 실행

```bash
docker build -t api-gateway -f Dockerfile.dev .
docker run -p 8000:8000 api-gateway
```

## API 엔드포인트

- `/api/v1/*`: 모든 API 요청 처리
- `/health`: 서비스 상태 확인
- `/metrics`: Prometheus 메트릭
- `/docs`: API 문서 (Swagger UI)
- `/redoc`: API 문서 (ReDoc)

## 환경 변수

| 변수명                         | 설명                 | 기본값                                 |
|-----------------------------|--------------------|-------------------------------------|
| ENVIRONMENT                 | 실행 환경              | development                         |
| DEBUG                       | 디버그 모드 활성화 여부      | True                                |
| AUTH_SERVICE_URL            | 인증 서비스 URL         | http://auth-service:8001            |
| DATA_COLLECTION_SERVICE_URL | 데이터 수집 서비스 URL     | http://data-collection-service:8002 |
| DATA_STORAGE_SERVICE_URL    | 데이터 저장 서비스 URL     | http://data-storage-service:8003    |
| ANALYSIS_SERVICE_URL        | 분석 서비스 URL         | http://analysis-service:8004        |
| NOTIFICATION_SERVICE_URL    | 알림 서비스 URL         | http://notification-service:8005    |
| REDIS_HOST                  | Redis 호스트          | redis                               |
| REDIS_PORT                  | Redis 포트           | 6379                                |
| RATE_LIMIT_ENABLED          | 속도 제한 활성화 여부       | True                                |
| RATE_LIMIT_DEFAULT          | 기본 속도 제한 (분당 요청 수) | 100                                 |
| JWT_SECRET_KEY              | JWT 서명 키           | secret_key_for_development_only     |

## 테스트

```bash
pytest
```

## 코드 스타일 검사

```bash
# 코드 포맷팅
black .

# 임포트 정렬
isort .

# 린팅
flake8 .
``` 