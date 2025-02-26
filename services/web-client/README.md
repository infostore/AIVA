# Web Client

New Data Collector 프로젝트의 웹 클라이언트 서비스입니다. Next.js를 기반으로 구현되었으며, API Gateway와 통신하여 주식 데이터를 시각화합니다.

## 기능

- 주식 데이터 대시보드
- 개별 주식 상세 정보 조회
- 주식 분석 데이터 시각화
- 사용자 인증 및 계정 관리

## 기술 스택

- **프레임워크**: Next.js
- **언어**: TypeScript
- **스타일링**: Tailwind CSS
- **상태 관리**: React Query, SWR
- **HTTP 클라이언트**: Axios
- **차트**: Chart.js, React-Chartjs-2

## 개발 환경 설정

### 요구 사항

- Node.js 18.0.0 이상
- npm 또는 yarn

### 설치 및 실행

```bash
# 의존성 설치
npm install
# 또는
yarn install

# 개발 서버 실행
npm run dev
# 또는
yarn dev
```

개발 서버는 기본적으로 http://localhost:3000 에서 실행됩니다.

### 빌드

```bash
# 프로덕션 빌드
npm run build
# 또는
yarn build

# 프로덕션 서버 실행
npm run start
# 또는
yarn start
```

## 프로젝트 구조

```
web-client/
├── src/                      # 소스 코드
│   ├── app/                  # Next.js App Router
│   │   ├── stocks/           # 주식 관련 페이지
│   │   │   └── [id]/         # 주식 상세 페이지
│   │   ├── auth/             # 인증 관련 페이지
│   │   ├── globals.css       # 전역 스타일
│   │   ├── layout.tsx        # 루트 레이아웃
│   │   └── page.tsx          # 메인 페이지
│   ├── components/           # 재사용 가능한 컴포넌트
│   ├── lib/                  # 유틸리티 함수
│   └── services/             # API 서비스
│       └── api.ts            # API 클라이언트
├── public/                   # 정적 파일
├── next.config.js            # Next.js 설정
├── tailwind.config.js        # Tailwind CSS 설정
├── postcss.config.js         # PostCSS 설정
├── tsconfig.json             # TypeScript 설정
└── package.json              # 프로젝트 메타데이터 및 의존성
```

## API Gateway 연결

이 클라이언트는 `/api` 경로로 들어오는 모든 요청을 API Gateway로 프록시합니다. API Gateway의 주소는 `next.config.js` 파일에서 설정할 수 있습니다.

```javascript
// next.config.js
module.exports = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*', // API Gateway 주소
      },
    ];
  },
};
```

## 배포

이 서비스는 Docker를 통해 배포할 수 있습니다. 자세한 내용은 프로젝트 루트의 `infrastructure/docker` 디렉토리를 참조하세요.
