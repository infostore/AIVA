# New Data Collector

개선된 주식 데이터 수집 및 관리 백엔드 서비스입니다. 기존 Data Collector 프로젝트를 개선하여 성능, 확장성, 보안성을 강화했습니다.

## 주요 개선 사항

- **마이크로서비스 아키텍처** 도입으로 확장성 및 유지보수성 향상
- **비동기 처리** 강화로 성능 개선
- **데이터 소스 추상화** 레이어 구현으로 다양한 데이터 소스 지원
- **보안 강화** 및 인증 시스템 개선
- **모니터링 및 로깅 시스템** 도입
- **CI/CD 파이프라인** 구축
- **Next.js 기반 웹 클라이언트** 추가로 사용자 인터페이스 제공

## 기술 스택

- **언어**: Python 3.11
- **웹 프레임워크**: FastAPI
- **ORM**: SQLAlchemy
- **데이터베이스**: PostgreSQL (시계열 데이터 파티셔닝 적용)
- **캐싱**: Redis
- **메시지 큐**: RabbitMQ
- **태스크 큐**: Celery
- **컨테이너화**: Docker, Kubernetes
- **모니터링**: Prometheus, Grafana
- **로깅**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **CI/CD**: GitHub Actions
- **프론트엔드**: Next.js, TypeScript, Tailwind CSS

## 아키텍처 개요

New Data Collector는 다음과 같은 마이크로서비스로 구성되어 있습니다:

1. **API Gateway Service**: 클라이언트 요청을 적절한 서비스로 라우팅
2. **Auth Service**: 사용자 인증 및 권한 관리
3. **Data Collection Service**: 다양한 소스에서 데이터 수집
4. **Data Storage Service**: 데이터 저장 및 관리
5. **Analysis Service**: 데이터 분석 및 지표 계산
6. **Notification Service**: 사용자 알림 관리
7. **Web Client**: Next.js 기반의 웹 클라이언트 인터페이스

각 서비스는 독립적으로 배포 가능하며, 서비스 간 통신은 REST API 또는 메시지 큐를 통해 이루어집니다.

## 시스템 아키텍처 다이어그램

```mermaid
graph TD
    Client[사용자 브라우저] --> WebClient[Web Client<br/>Next.js]
    WebClient --> APIGateway[API Gateway<br/>FastAPI]
    
    subgraph "마이크로서비스"
        APIGateway --> AuthService[Auth Service<br/>FastAPI]
        APIGateway --> DataCollectionService[Data Collection Service<br/>FastAPI]
        APIGateway --> DataStorageService[Data Storage Service<br/>FastAPI]
        APIGateway --> AnalysisService[Analysis Service<br/>FastAPI]
        APIGateway --> NotificationService[Notification Service<br/>FastAPI]
        
        DataCollectionService --> MessageQueue[Message Queue<br/>RabbitMQ]
        MessageQueue --> DataStorageService
        MessageQueue --> AnalysisService
        AnalysisService --> MessageQueue
        MessageQueue --> NotificationService
    end
    
    subgraph "데이터 저장소"
        AuthService --> AuthDB[(Auth DB<br/>PostgreSQL)]
        DataStorageService --> TimeSeriesDB[(Time Series DB<br/>PostgreSQL)]
        DataStorageService --> Cache[(Cache<br/>Redis)]
        AnalysisService --> AnalyticsDB[(Analytics DB<br/>PostgreSQL)]
        NotificationService --> NotificationDB[(Notification DB<br/>PostgreSQL)]
    end
    
    subgraph "외부 데이터 소스"
        DataSources[외부 데이터 소스<br/>API/웹스크래핑] --> DataCollectionService
    end
    
    subgraph "모니터링 및 로깅"
        AllServices[모든 서비스] --> Prometheus[Prometheus]
        Prometheus --> Grafana[Grafana]
        AllServices --> ELK[ELK Stack]
    end
    
    subgraph "CI/CD"
        GitHubRepo[GitHub Repository] --> GitHubActions[GitHub Actions]
        GitHubActions --> DockerHub[Docker Hub]
        DockerHub --> K8s[Kubernetes Cluster]
    end
    
    style Client fill:#f9f9f9,stroke:#333,stroke-width:1px
    style WebClient fill:#bbdefb,stroke:#333,stroke-width:1px
    style APIGateway fill:#c8e6c9,stroke:#333,stroke-width:1px
    style AuthService fill:#dcedc8,stroke:#333,stroke-width:1px
    style DataCollectionService fill:#dcedc8,stroke:#333,stroke-width:1px
    style DataStorageService fill:#dcedc8,stroke:#333,stroke-width:1px
    style AnalysisService fill:#dcedc8,stroke:#333,stroke-width:1px
    style NotificationService fill:#dcedc8,stroke:#333,stroke-width:1px
    style MessageQueue fill:#ffe0b2,stroke:#333,stroke-width:1px
    style AuthDB fill:#e1bee7,stroke:#333,stroke-width:1px
    style TimeSeriesDB fill:#e1bee7,stroke:#333,stroke-width:1px
    style Cache fill:#e1bee7,stroke:#333,stroke-width:1px
    style AnalyticsDB fill:#e1bee7,stroke:#333,stroke-width:1px
    style NotificationDB fill:#e1bee7,stroke:#333,stroke-width:1px
    style DataSources fill:#ffccbc,stroke:#333,stroke-width:1px
    style Prometheus fill:#d1c4e9,stroke:#333,stroke-width:1px
    style Grafana fill:#d1c4e9,stroke:#333,stroke-width:1px
    style ELK fill:#d1c4e9,stroke:#333,stroke-width:1px
    style GitHubRepo fill:#f5f5f5,stroke:#333,stroke-width:1px
    style GitHubActions fill:#f5f5f5,stroke:#333,stroke-width:1px
    style DockerHub fill:#f5f5f5,stroke:#333,stroke-width:1px
    style K8s fill:#f5f5f5,stroke:#333,stroke-width:1px
```

### 데이터 수집 및 처리 흐름

```mermaid
sequenceDiagram
    participant 외부API as 외부 데이터 소스
    participant 수집서비스 as Data Collection Service
    participant 메시지큐 as RabbitMQ
    participant 저장서비스 as Data Storage Service
    participant 분석서비스 as Analysis Service
    participant 알림서비스 as Notification Service
    participant 사용자 as 사용자 (Web Client)

    rect rgb(240, 248, 255)
    Note over 수집서비스: 스케줄러에 의해 주기적으로 실행
    수집서비스->>외부API: 주식 데이터 요청
    외부API-->>수집서비스: 주식 데이터 응답
    수집서비스->>수집서비스: 데이터 정제 및 변환
    수집서비스->>메시지큐: 수집된 데이터 발행
    end

    rect rgb(255, 248, 240)
    메시지큐-->>저장서비스: 데이터 저장 메시지 전달
    저장서비스->>저장서비스: 데이터 검증
    저장서비스->>DB: 시계열 데이터 저장
    저장서비스->>Cache: 자주 접근하는 데이터 캐싱
    end

    rect rgb(240, 255, 240)
    메시지큐-->>분석서비스: 분석 작업 메시지 전달
    분석서비스->>분석서비스: 기술적/기본적 분석 수행
    분석서비스->>DB: 분석 결과 저장
    분석서비스->>메시지큐: 분석 완료 이벤트 발행
    end

    rect rgb(255, 240, 245)
    메시지큐-->>알림서비스: 알림 트리거 메시지 전달
    알림서비스->>알림서비스: 알림 조건 확인
    alt 알림 조건 충족
        알림서비스->>사용자: 이메일/푸시 알림 전송
    end
    end

    rect rgb(245, 245, 255)
    사용자->>저장서비스: 주식 데이터 요청
    저장서비스->>Cache: 캐시된 데이터 확인
    alt 캐시 히트
        Cache-->>저장서비스: 캐시된 데이터 반환
    else 캐시 미스
        저장서비스->>DB: 데이터베이스 조회
        DB-->>저장서비스: 데이터 반환
        저장서비스->>Cache: 데이터 캐싱
    end
    저장서비스-->>사용자: 데이터 응답
    end
```

### 주요 데이터 모델 구조

```mermaid
classDiagram
    class User {
        +UUID id
        +String username
        +String email
        +String password_hash
        +DateTime created_at
        +DateTime updated_at
        +Boolean is_active
        +List~Role~ roles
        +authenticate(password) Boolean
    }

    class Role {
        +UUID id
        +String name
        +String description
        +List~Permission~ permissions
    }

    class Permission {
        +UUID id
        +String name
        +String description
    }

    class Stock {
        +UUID id
        +String symbol
        +String name
        +String exchange
        +String sector
        +String industry
        +String description
        +DateTime created_at
        +DateTime updated_at
        +List~StockPrice~ prices
        +List~StockAnalysis~ analyses
    }

    class StockPrice {
        +UUID id
        +UUID stock_id
        +DateTime timestamp
        +Float open
        +Float high
        +Float low
        +Float close
        +Integer volume
        +String source
    }

    class StockAnalysis {
        +UUID id
        +UUID stock_id
        +DateTime timestamp
        +String recommendation
        +Float target_price
        +String risk_level
        +JSON technical_indicators
        +JSON fundamental_metrics
    }

    class Notification {
        +UUID id
        +UUID user_id
        +String title
        +String message
        +String type
        +Boolean is_read
        +DateTime created_at
        +DateTime read_at
    }

    class NotificationSetting {
        +UUID id
        +UUID user_id
        +Boolean email_notifications
        +Boolean push_notifications
        +Boolean price_alerts
        +Boolean news_alerts
        +Boolean report_alerts
        +Boolean market_summary
    }

    class PriceAlert {
        +UUID id
        +UUID user_id
        +UUID stock_id
        +String condition
        +Float target_price
        +Boolean is_active
        +DateTime created_at
        +DateTime triggered_at
    }

    User "1" -- "n" Role : has
    Role "1" -- "n" Permission : contains
    User "1" -- "n" Notification : receives
    User "1" -- "1" NotificationSetting : configures
    User "1" -- "n" PriceAlert : creates
    Stock "1" -- "n" StockPrice : has
    Stock "1" -- "n" StockAnalysis : has
    Stock "1" -- "n" PriceAlert : targets
```

## 프로젝트 구조

```
new-data-collector/
├── docs/                       # 프로젝트 문서
│   ├── architecture/           # 아키텍처 문서
│   ├── api/                    # API 문서
│   └── development/            # 개발 가이드
├── services/                   # 마이크로서비스
│   ├── api-gateway/            # API Gateway 서비스
│   ├── auth-service/           # 인증 서비스
│   ├── data-collection-service/ # 데이터 수집 서비스
│   ├── data-storage-service/   # 데이터 저장 서비스
│   ├── analysis-service/       # 데이터 분석 서비스
│   ├── notification-service/   # 알림 서비스
│   └── web-client/             # Next.js 기반 웹 클라이언트
├── infrastructure/             # 인프라 설정
│   ├── docker/                 # Docker 설정
│   ├── kubernetes/             # Kubernetes 설정
│   ├── monitoring/             # 모니터링 설정
│   └── ci-cd/                  # CI/CD 파이프라인 설정
├── common/                     # 공통 라이브러리
│   ├── models/                 # 공통 모델
│   ├── utils/                  # 유틸리티 함수
│   └── clients/                # 외부 서비스 클라이언트
├── scripts/                    # 유틸리티 스크립트
├── .gitignore                  # Git 무시 파일 설정
└── .markdownlint.json          # 마크다운 린트 설정
```

## 설치 및 실행

### 요구 사항

- Docker 및 Docker Compose
- Kubernetes (선택 사항)
- Python 3.11 이상
- Node.js 18.0.0 이상 (웹 클라이언트용)

### 개발 환경 설정

```bash
# 저장소 클론
git clone https://github.com/your-username/new-data-collector.git
cd new-data-collector

# 가상 환경 설정 (선택 사항)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate  # Windows

# 의존성 설치 (로컬 개발 시)
pip install -r requirements.txt

# Docker Compose로 개발 환경 실행
docker-compose -f infrastructure/docker/docker-compose.dev.yml up

# 웹 클라이언트 실행 (별도 터미널에서)
cd services/web-client
npm install
npm run dev
```

### 프로덕션 배포

```bash
# Kubernetes 배포
kubectl apply -f infrastructure/kubernetes/
```

## 개발 가이드

각 마이크로서비스는 독립적으로 개발 및 테스트할 수 있습니다. 서비스별 개발 가이드는 해당 서비스 디렉토리의 README.md 파일을 참조하세요.

### 코드 스타일

이 프로젝트는 다음과 같은 코드 스타일 가이드를 따릅니다:
- Python: PEP 8
- JavaScript/TypeScript: ESLint, Prettier
- 문서: Markdown 린트 규칙 (.markdownlint.json)

## 기여 가이드

프로젝트에 기여하기 위한 자세한 내용은 [CONTRIBUTING.md](docs/development/CONTRIBUTING.md)를 참조하세요.

## 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요. 