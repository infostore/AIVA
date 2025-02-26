# 분석 서비스

금융 데이터 분석을 위한 마이크로서비스입니다. 이 서비스는 주식 데이터에 대한 다양한 분석 기능을 제공하여 투자 의사결정을 지원합니다.

## 주요 기능

- **기술적 분석 (Technical Analysis)**: 주가 차트 패턴, 이동평균선, RSI, MACD 등 기술적 지표 분석
- **기본적 분석 (Fundamental Analysis)**: 재무제표, PER, PBR 등 기업 가치 평가 지표 분석
- **예측 분석 (Prediction Analysis)**: 머신러닝 기반 주가 예측 모델
- **텍스트 분석 (Text Analysis)**: 뉴스 및 공시정보에 대한 자연어 처리 기반 분석

## 텍스트 분석 기능

LangChain과 Llama 모델을 활용하여 뉴스 및 공시정보에 대한 다양한 분석을 제공합니다:

- **감성 분석 (Sentiment Analysis)**: 텍스트의 긍정/부정/중립 감성 분석
- **개체명 인식 (Named Entity Recognition)**: 텍스트에서 기업명, 인물, 제품 등 주요 개체 추출
- **핵심 문구 추출 (Key Phrase Extraction)**: 중요 문구 및 키워드 추출
- **텍스트 요약 (Text Summarization)**: 긴 텍스트의 핵심 내용 요약
- **주가 영향 분석 (Stock Price Impact Analysis)**: 뉴스가 주가에 미칠 영향 예측
- **관련 주제 추출 (Related Topics Extraction)**: 연관된 주제 및 산업 분야 추출

## 기술 스택

- **웹 프레임워크**: FastAPI
- **데이터 처리**: Pandas, NumPy
- **머신러닝**: Scikit-learn, StatsModels, PyTorch
- **자연어 처리**: LangChain, Transformers, NLTK, Sentence-Transformers
- **LLM 모델**: Llama, OpenAI (백업)
- **벡터 검색**: FAISS
- **캐싱**: Redis

## 설치 및 실행

### 환경 설정

1. 필요한 패키지 설치:

```bash
pip install -r requirements.txt
```

2. Llama 모델 다운로드:

Llama 모델을 다운로드하고 `models` 디렉토리에 저장합니다.

```bash
mkdir -p models
# Hugging Face에서 모델 다운로드 예시
huggingface-cli download TheBloke/Llama-2-7B-Chat-GGUF llama-2-7b-chat-q4_0.gguf --local-dir models
```

3. 환경 변수 설정:

`.env.example` 파일을 `.env`로 복사하고 필요한 값을 설정합니다.

```bash
cp .env.example .env
```

주요 환경 변수:

```
# 기본 설정
PROJECT_NAME="분석 서비스"
API_V1_STR="/api/v1"
DEBUG=False

# 서버 설정
HOST="0.0.0.0"
PORT=8002

# 데이터 스토리지 서비스 설정
DATA_STORAGE_SERVICE_URL="http://localhost:8001"

# 캐시 설정
REDIS_HOST="localhost"
REDIS_PORT=6379

# Llama 모델 설정
LLAMA_MODEL_PATH="models/llama-2-7b-chat-q4_0.gguf"

# OpenAI API 키 (백업용)
OPENAI_API_KEY="your-openai-api-key-here"
```

### 서버 실행

#### 로컬 개발 환경

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

#### Docker 컨테이너

```bash
# 이미지 빌드
docker build -t analysis-service .

# 컨테이너 실행
docker run -d -p 8002:8002 --name analysis-service \
  --env-file .env \
  -v $(pwd)/models:/app/models \
  analysis-service
```

## API 엔드포인트

### 상태 확인 API

- `GET /api/v1/health`: 서비스 상태 확인

### 기술적 분석 API

- `GET /api/v1/technical/indicators/{stock_code}`: 기술적 지표 분석
- `GET /api/v1/technical/patterns/{stock_code}`: 차트 패턴 분석
- `GET /api/v1/technical/trends/{stock_code}`: 추세 분석

### 기본적 분석 API

- `GET /api/v1/fundamental/metrics/{stock_code}`: 기본적 지표 분석
- `GET /api/v1/fundamental/valuation/{stock_code}`: 기업 가치 평가
- `GET /api/v1/fundamental/comparison`: 기업 간 비교 분석

### 예측 분석 API

- `GET /api/v1/prediction/price/{stock_code}`: 주가 예측
- `GET /api/v1/prediction/trend/{stock_code}`: 추세 예측
- `GET /api/v1/prediction/volatility/{stock_code}`: 변동성 예측

### 텍스트 분석 API

- `POST /api/v1/text/news`: 뉴스 분석
- `POST /api/v1/text/disclosure`: 공시정보 분석
- `GET /api/v1/text/sentiment`: 텍스트 감성 분석
- `GET /api/v1/text/summary`: 텍스트 요약
- `GET /api/v1/text/entities`: 개체명 인식
- `GET /api/v1/text/impact`: 주가 영향 분석

## 사용 예시

### 뉴스 분석 요청

```python
import requests
import json

url = "http://localhost:8002/api/v1/text/news"
payload = {
    "news_ids": ["news_id_1", "news_id_2"],
    "stock_code": "005930",  # 삼성전자
    "max_items": 10
}
headers = {"Content-Type": "application/json"}

response = requests.post(url, json=payload, headers=headers)
result = response.json()
print(json.dumps(result, indent=2, ensure_ascii=False))
```

### 텍스트 감성 분석 요청

```python
import requests

url = "http://localhost:8002/api/v1/text/sentiment"
params = {
    "text": "삼성전자가 신제품 출시로 매출 증가가 예상됩니다.",
    "model": "llama"  # 'llama' 또는 'openai'
}

response = requests.get(url, params=params)
result = response.json()
print(result)
# 출력 예시: {"sentiment": "positive", "score": 0.87, "details": {...}}
```

## 프로젝트 구조

```
analysis-service/
├── app/                        # 애플리케이션 코드
│   ├── api/                    # API 관련 코드
│   │   ├── api_v1/             # API v1 버전
│   │   │   ├── endpoints/      # API 엔드포인트
│   │   │   │   ├── health.py   # 상태 확인 API
│   │   │   │   ├── technical.py # 기술적 분석 API
│   │   │   │   ├── fundamental.py # 기본적 분석 API
│   │   │   │   ├── prediction.py # 예측 분석 API
│   │   │   │   └── text_analysis.py # 텍스트 분석 API
│   │   │   └── api.py          # API 라우터
│   │   └── __init__.py
│   ├── schemas/                # Pydantic 모델
│   ├── config.py               # 설정
│   ├── main.py                 # 애플리케이션 진입점
│   └── __init__.py
├── models/                     # LLM 모델 저장 디렉토리
├── .env.example                # 환경 변수 예시
├── Dockerfile                  # Docker 설정
├── main.py                     # 서비스 진입점
├── requirements.txt            # 의존성 패키지
└── README.md                   # 문서
```

## 개발 가이드

### 새로운 분석 기능 추가

1. 적절한 엔드포인트 파일에 새 라우터 함수 추가
2. 필요한 스키마 정의 (app/schemas/)
3. 분석 로직 구현
4. API 라우터에 등록 (app/api/api_v1/api.py)

### 코드 스타일

이 프로젝트는 PEP 8 코드 스타일 가이드를 따릅니다.

## 라이센스

MIT 