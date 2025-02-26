# 분석 서비스

금융 데이터 분석을 위한 마이크로서비스입니다.

## 기능

- 기술적 분석 (Technical Analysis)
- 기본적 분석 (Fundamental Analysis)
- 예측 분석 (Prediction Analysis)
- 텍스트 분석 (Text Analysis) - 뉴스 및 공시정보 분석

## 텍스트 분석 기능

LangChain과 Llama를 활용하여 뉴스 및 공시정보에 대한 다양한 분석을 제공합니다:

- 감성 분석 (Sentiment Analysis)
- 개체명 인식 (Named Entity Recognition)
- 핵심 문구 추출 (Key Phrase Extraction)
- 텍스트 요약 (Text Summarization)
- 주가 영향 분석 (Stock Price Impact Analysis)
- 관련 주제 추출 (Related Topics Extraction)

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

Llama 모델 경로를 설정합니다:

```
LLAMA_MODEL_PATH="models/llama-2-7b-chat-q4_0.gguf"
```

OpenAI API 키도 백업용으로 설정할 수 있습니다:

```
OPENAI_API_KEY="your-openai-api-key-here"
```

### 서버 실행

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

## API 엔드포인트

### 텍스트 분석 API

- `POST /api/v1/text/news`: 뉴스 분석
- `POST /api/v1/text/disclosure`: 공시정보 분석
- `GET /api/v1/text/sentiment`: 텍스트 감성 분석
- `GET /api/v1/text/summary`: 텍스트 요약

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

## 라이센스

MIT 