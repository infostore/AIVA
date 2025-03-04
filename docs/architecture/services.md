# 마이크로서비스 상세 설계

이 문서는 New Data Collector의 각 마이크로서비스에 대한 상세 설계 정보를 제공합니다.

## 1. API Gateway Service

### 1.1 책임
- 모든 클라이언트 요청의 단일 진입점 제공
- 요청 라우팅 및 로드 밸런싱
- 인증 토큰 검증
- 속도 제한(Rate Limiting) 적용
- API 문서화 및 통합

### 1.2 주요 컴포넌트
- **라우터**: 요청을 적절한 마이크로서비스로 라우팅
- **인증 미들웨어**: JWT 토큰 검증
- **속도 제한 미들웨어**: API 요청 제한
- **로깅 미들웨어**: 요청/응답 로깅
- **서비스 디스커버리 통합**: 서비스 위치 자동 감지

### 1.3 API 엔드포인트
- `/api/v1/*`: 모든 API 요청 처리
- `/docs`: API 문서 (Swagger/ReDoc)
- `/health`: 서비스 상태 확인

### 1.4 기술 스택
- FastAPI
- Traefik (API 게이트웨이)
- Redis (속도 제한 구현)

## 2. Auth Service

### 2.1 책임
- 사용자 인증 및 권한 관리
- 토큰 발급 및 관리
- 사용자 프로필 관리
- 보안 정책 적용

### 2.2 주요 컴포넌트
- **인증 컨트롤러**: 로그인, 회원가입, 토큰 갱신 처리
- **토큰 관리자**: JWT 토큰 생성 및 검증
- **사용자 관리자**: 사용자 정보 관리
- **권한 관리자**: 역할 기반 접근 제어(RBAC) 구현
- **2FA 관리자**: 2단계 인증 처리

### 2.3 API 엔드포인트
- `/auth/register`: 사용자 등록
- `/auth/login`: 로그인 및 토큰 발급
- `/auth/refresh`: 토큰 갱신
- `/auth/profile`: 사용자 프로필 관리
- `/auth/2fa`: 2단계 인증 관리

### 2.4 데이터 모델
- **User**: 사용자 정보
- **Role**: 사용자 역할
- **Permission**: 권한 정보
- **Token**: 토큰 정보

### 2.5 기술 스택
- FastAPI
- PostgreSQL (사용자 데이터 저장)
- Redis (토큰 캐싱)
- PyJWT (JWT 처리)

## 3. Data Collection Service

### 3.1 책임
- 다양한 소스에서 주식 데이터 수집
- 데이터 수집 작업 스케줄링
- 데이터 소스 관리
- 수집된 데이터의 초기 처리

### 3.2 주요 컴포넌트
- **데이터 소스 추상화 레이어**: 다양한 데이터 소스에 대한 통합 인터페이스
- **수집기 관리자**: 데이터 수집 작업 관리
- **스케줄러**: 주기적 데이터 수집 작업 예약
- **데이터 변환기**: 수집된 데이터 정규화

### 3.3 데이터 소스 어댑터
- **Yahoo Finance 어댑터**: Yahoo Finance API 연동
- **KRX 어댑터**: 한국거래소 데이터 연동
- **Alpha Vantage 어댑터**: Alpha Vantage API 연동
- **Finnhub 어댑터**: Finnhub API 연동

### 3.4 API 엔드포인트
- `/collectors`: 데이터 수집기 관리
- `/collectors/{id}/run`: 수집기 실행
- `/sources`: 데이터 소스 관리
- `/schedules`: 수집 스케줄 관리

### 3.5 기술 스택
- FastAPI
- Celery (비동기 작업 처리)
- RabbitMQ (메시지 큐)
- APScheduler (작업 스케줄링)

## 4. Data Storage Service

### 4.1 책임
- 수집된 데이터 저장 및 관리
- 데이터 정규화 및 검증
- 데이터 버전 관리
- 데이터 접근 API 제공

### 4.2 주요 컴포넌트
- **데이터 저장소 관리자**: 데이터 저장 및 검색
- **데이터 검증기**: 데이터 무결성 검증
- **버전 관리자**: 데이터 버전 관리
- **캐시 관리자**: 자주 접근하는 데이터 캐싱

### 4.3 데이터 모델
- **StockPrice**: 주가 데이터
- **TradingTrend**: 매매동향 데이터
- **QuarterlyRevenue**: 분기별 수익 데이터
- **DataVersion**: 데이터 버전 정보

### 4.4 API 엔드포인트
- `/stocks`: 주식 데이터 관리
- `/trends`: 매매동향 데이터 관리
- `/revenues`: 수익 데이터 관리
- `/versions`: 데이터 버전 관리

### 4.5 기술 스택
- FastAPI
- PostgreSQL (시계열 파티셔닝 적용)
- SQLAlchemy (ORM)
- Redis (데이터 캐싱)

## 5. Analysis Service

### 5.1 책임
- 주식 데이터 분석
- 기술적 분석 지표 계산
- 데이터 시각화 API 제공
- 분석 결과 캐싱

### 5.2 주요 컴포넌트
- **분석 엔진**: 다양한 분석 알고리즘 구현
- **지표 계산기**: 기술적 분석 지표 계산
- **시각화 생성기**: 차트 및 그래프 데이터 생성
- **결과 캐시 관리자**: 분석 결과 캐싱

### 5.3 지원 분석 지표
- 이동평균선 (MA, EMA)
- 상대강도지수 (RSI)
- 볼린저 밴드
- MACD (이동평균수렴확산)
- 스토캐스틱 오실레이터

### 5.4 API 엔드포인트
- `/analysis/technical`: 기술적 분석 지표
- `/analysis/visualization`: 데이터 시각화
- `/analysis/custom`: 사용자 정의 분석

### 5.5 기술 스택
- FastAPI
- NumPy, Pandas (데이터 분석)
- Matplotlib, Plotly (데이터 시각화)
- Redis (결과 캐싱)

## 6. Notification Service

### 6.1 책임
- 사용자 알림 관리
- 알림 전송 (이메일, 웹훅, 푸시)
- 알림 템플릿 관리
- 알림 구독 관리

### 6.2 주요 컴포넌트
- **알림 관리자**: 알림 생성 및 관리
- **전송 엔진**: 다양한 채널을 통한 알림 전송
- **템플릿 엔진**: 알림 템플릿 렌더링
- **구독 관리자**: 사용자 알림 구독 관리

### 6.3 알림 유형
- 가격 알림 (목표가 도달, 급등/급락)
- 거래량 알림 (비정상적 거래량 증가)
- 시스템 알림 (데이터 수집 완료, 오류 등)
- 사용자 정의 알림

### 6.4 API 엔드포인트
- `/notifications`: 알림 관리
- `/subscriptions`: 알림 구독 관리
- `/templates`: 알림 템플릿 관리
- `/channels`: 알림 채널 관리

### 6.5 기술 스택
- FastAPI
- RabbitMQ (알림 메시지 큐)
- Redis (알림 상태 관리)
- Jinja2 (템플릿 엔진) 