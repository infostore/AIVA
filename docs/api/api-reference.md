# API 참조 문서

이 문서는 New Data Collector의 API 엔드포인트에 대한 참조 정보를 제공합니다.

## 기본 URL

모든 API 요청은 다음 기본 URL에서 시작합니다:

```
https://api.new-data-collector.com/api/v1
```

## 인증

대부분의 API 엔드포인트는 인증이 필요합니다. 인증은 JWT 토큰을 사용하여 수행됩니다.

### 인증 헤더

```
Authorization: Bearer {token}
```

## 응답 형식

모든 응답은 JSON 형식으로 반환됩니다. 성공적인 응답은 다음과 같은 구조를 가집니다:

```json
{
  "status": "success",
  "data": { ... }
}
```

오류 응답은 다음과 같은 구조를 가집니다:

```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "오류 메시지"
  }
}
```

## 인증 API

### 회원가입

```
POST /auth/register
```

**요청 본문**:

```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "사용자 이름"
}
```

**응답**:

```json
{
  "status": "success",
  "data": {
    "user_id": "user-uuid",
    "email": "user@example.com",
    "name": "사용자 이름"
  }
}
```

### 로그인

```
POST /auth/login
```

**요청 본문**:

```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**응답**:

```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 3600
  }
}
```

### 토큰 갱신

```
POST /auth/refresh
```

**요청 헤더**:

```
Authorization: Bearer {refresh_token}
```

**응답**:

```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 3600
  }
}
```

## 주식 데이터 API

### 주식 목록 조회

```
GET /stocks
```

**쿼리 파라미터**:

- `market` (선택): 시장 유형 (KOSPI, KOSDAQ, NASDAQ, NYSE, AMEX)
- `sector` (선택): 섹터
- `page` (선택): 페이지 번호 (기본값: 1)
- `limit` (선택): 페이지당 항목 수 (기본값: 20)

**응답**:

```json
{
  "status": "success",
  "data": {
    "items": [
      {
        "symbol": "005930",
        "name": "삼성전자",
        "market": "KOSPI",
        "sector": "전기전자",
        "industry": "반도체"
      },
      ...
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 100,
      "pages": 5
    }
  }
}
```

### 주식 상세 정보 조회

```
GET /stocks/{symbol}
```

**응답**:

```json
{
  "status": "success",
  "data": {
    "symbol": "005930",
    "name": "삼성전자",
    "market": "KOSPI",
    "sector": "전기전자",
    "industry": "반도체",
    "latest_price": {
      "date": "2023-05-15",
      "open": 65000,
      "high": 66000,
      "low": 64500,
      "close": 65500,
      "volume": 12345678,
      "change": 0.77
    }
  }
}
```

### 주가 데이터 조회

```
GET /stocks/{symbol}/prices
```

**쿼리 파라미터**:

- `start_date` (필수): 시작 날짜 (YYYY-MM-DD)
- `end_date` (필수): 종료 날짜 (YYYY-MM-DD)
- `interval` (선택): 데이터 간격 (daily, weekly, monthly, 기본값: daily)

**응답**:

```json
{
  "status": "success",
  "data": {
    "symbol": "005930",
    "name": "삼성전자",
    "prices": [
      {
        "date": "2023-05-15",
        "open": 65000,
        "high": 66000,
        "low": 64500,
        "close": 65500,
        "volume": 12345678,
        "change": 0.77
      },
      ...
    ]
  }
}
```

## 매매동향 API

### 매매동향 조회

```
GET /stocks/{symbol}/trading-trends
```

**쿼리 파라미터**:

- `start_date` (필수): 시작 날짜 (YYYY-MM-DD)
- `end_date` (필수): 종료 날짜 (YYYY-MM-DD)
- `investor_type` (선택): 투자자 유형 (INDIVIDUAL, FOREIGN, INSTITUTION, ...)

**응답**:

```json
{
  "status": "success",
  "data": {
    "symbol": "005930",
    "name": "삼성전자",
    "trading_trends": [
      {
        "date": "2023-05-15",
        "investor_type": "INDIVIDUAL",
        "buy_volume": 1000000,
        "sell_volume": 900000,
        "net_volume": 100000,
        "buy_amount": 65000000000,
        "sell_amount": 58500000000,
        "net_amount": 6500000000
      },
      ...
    ]
  }
}
```

## 분석 API

### 기술적 분석 지표 조회

```
GET /analysis/technical/{symbol}
```

**쿼리 파라미터**:

- `start_date` (필수): 시작 날짜 (YYYY-MM-DD)
- `end_date` (필수): 종료 날짜 (YYYY-MM-DD)
- `indicators` (필수): 지표 목록 (쉼표로 구분, 예: ma,rsi,bollinger)

**응답**:

```json
{
  "status": "success",
  "data": {
    "symbol": "005930",
    "name": "삼성전자",
    "indicators": {
      "ma": {
        "ma5": [65100, 65200, 65300, ...],
        "ma20": [64500, 64600, 64700, ...],
        "ma60": [63000, 63100, 63200, ...]
      },
      "rsi": {
        "rsi14": [65.5, 66.2, 64.8, ...]
      },
      "bollinger": {
        "upper": [67000, 67100, 67200, ...],
        "middle": [65000, 65100, 65200, ...],
        "lower": [63000, 63100, 63200, ...]
      }
    }
  }
}
```

## 알림 API

### 알림 생성

```
POST /notifications
```

**요청 본문**:

```json
{
  "type": "PRICE_ALERT",
  "symbol": "005930",
  "condition": {
    "operator": "gte",
    "value": 70000
  },
  "channels": ["email", "webhook"]
}
```

**응답**:

```json
{
  "status": "success",
  "data": {
    "notification_id": "notification-uuid",
    "type": "PRICE_ALERT",
    "symbol": "005930",
    "condition": {
      "operator": "gte",
      "value": 70000
    },
    "channels": ["email", "webhook"],
    "created_at": "2023-05-15T12:00:00Z"
  }
}
```

### 알림 목록 조회

```
GET /notifications
```

**쿼리 파라미터**:

- `type` (선택): 알림 유형 (PRICE_ALERT, VOLUME_ALERT, ...)
- `symbol` (선택): 주식 심볼
- `page` (선택): 페이지 번호 (기본값: 1)
- `limit` (선택): 페이지당 항목 수 (기본값: 20)

**응답**:

```json
{
  "status": "success",
  "data": {
    "items": [
      {
        "notification_id": "notification-uuid",
        "type": "PRICE_ALERT",
        "symbol": "005930",
        "condition": {
          "operator": "gte",
          "value": 70000
        },
        "channels": ["email", "webhook"],
        "created_at": "2023-05-15T12:00:00Z"
      },
      ...
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 5,
      "pages": 1
    }
  }
}
```

## 오류 코드

| 코드                      | 설명               |
|-------------------------|------------------|
| `AUTHENTICATION_ERROR`  | 인증 오류            |
| `AUTHORIZATION_ERROR`   | 권한 오류            |
| `VALIDATION_ERROR`      | 요청 데이터 유효성 검사 오류 |
| `RESOURCE_NOT_FOUND`    | 요청한 리소스를 찾을 수 없음 |
| `RATE_LIMIT_EXCEEDED`   | API 요청 제한 초과     |
| `INTERNAL_SERVER_ERROR` | 서버 내부 오류         |