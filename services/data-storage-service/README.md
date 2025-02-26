# 데이터 스토리지 서비스

주식 데이터를 저장하고 관리하는 마이크로서비스입니다.

## 기능

- 주식 정보 관리 (생성, 조회, 업데이트, 삭제)
- 주식 가격 데이터 관리 (일별, 주별, 월별 등)
- 재무 데이터 관리 (분기별, 연간 등)
- RESTful API 제공
- 비동기 데이터베이스 작업 지원

## 기술 스택

- **언어**: Python 3.11
- **웹 프레임워크**: FastAPI
- **ORM**: SQLAlchemy 2.0 (비동기 지원)
- **데이터베이스**: PostgreSQL
- **마이그레이션**: Alembic
- **컨테이너화**: Docker

## 설치 및 실행

### 로컬 개발 환경

1. 가상 환경 생성 및 활성화:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

2. 의존성 설치:

```bash
pip install -r requirements.txt
```

3. 환경 변수 설정:

`.env` 파일을 생성하고 다음과 같이 설정합니다:

```
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=data_storage_service
POSTGRES_PORT=5432
DEBUG=True
```

4. 데이터베이스 마이그레이션:

```bash
alembic upgrade head
```

5. 서비스 실행:

```bash
uvicorn app.main:app --reload
```

### Docker를 사용한 실행

1. Docker 이미지 빌드:

```bash
docker build -t data-storage-service .
```

2. Docker 컨테이너 실행:

```bash
docker run -d -p 8000:8000 --name data-storage-service \
  -e POSTGRES_SERVER=host.docker.internal \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=data_storage_service \
  -e POSTGRES_PORT=5432 \
  data-storage-service
```

## API 문서

서비스가 실행되면 다음 URL에서 API 문서를 확인할 수 있습니다:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 데이터베이스 스키마

주요 데이터베이스 모델:

- **Stock**: 주식 기본 정보 (심볼, 이름, 거래소 등)
- **StockPrice**: 주식 가격 데이터 (일자, 시가, 고가, 저가, 종가, 거래량 등)
- **FinancialData**: 재무 데이터 (기간, 매출, 영업이익, 순이익 등)

## 개발 가이드

### 새로운 엔드포인트 추가

1. `app/api/api_v1/endpoints/` 디렉토리에 새 파일 생성
2. 라우터 정의 및 엔드포인트 구현
3. `app/api/api_v1/api.py`에 라우터 등록

### 새로운 모델 추가

1. `app/models/` 디렉토리에 모델 정의
2. `app/schemas/` 디렉토리에 Pydantic 스키마 정의
3. `app/crud/` 디렉토리에 CRUD 작업 구현
4. Alembic을 사용하여 마이그레이션 생성: `alembic revision --autogenerate -m "Add new model"`

## 라이센스

MIT 