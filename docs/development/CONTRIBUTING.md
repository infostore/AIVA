# 기여 가이드

New Data Collector 프로젝트에 기여해 주셔서 감사합니다. 이 문서는 프로젝트에 기여하는 방법에 대한 가이드라인을 제공합니다.

## 개발 환경 설정

### 요구 사항

- Python 3.11 이상
- Docker 및 Docker Compose
- Git

### 로컬 개발 환경 설정

1. 저장소 클론

```bash
git clone https://github.com/your-username/new-data-collector.git
cd new-data-collector
```

2. 가상 환경 설정 (선택 사항)

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. Docker Compose로 개발 환경 실행

```bash
docker-compose -f infrastructure/docker/docker-compose.dev.yml up
```

## 코드 스타일 가이드

이 프로젝트는 다음과 같은 코드 스타일 가이드를 따릅니다:

- [Black](https://black.readthedocs.io/en/stable/) 코드 포맷터
- [isort](https://pycqa.github.io/isort/) 임포트 정렬
- [Flake8](https://flake8.pycqa.org/en/latest/) 린터

각 서비스 디렉토리에서 다음 명령을 실행하여 코드 스타일을 검사하고 수정할 수 있습니다:

```bash
# 코드 포맷팅
black .

# 임포트 정렬
isort .

# 린팅
flake8 .
```

## 브랜치 전략

이 프로젝트는 Git Flow 브랜치 전략을 따릅니다:

- `main`: 프로덕션 릴리스
- `develop`: 개발 브랜치
- `feature/*`: 새로운 기능 개발
- `bugfix/*`: 버그 수정
- `release/*`: 릴리스 준비
- `hotfix/*`: 긴급 수정

새로운 기능을 개발하거나 버그를 수정할 때는 `develop` 브랜치에서 새로운 브랜치를 생성하세요:

```bash
git checkout develop
git pull
git checkout -b feature/your-feature-name
```

## 커밋 메시지 가이드라인

커밋 메시지는 다음과 같은 형식을 따라주세요:

```
<type>(<scope>): <subject>

<body>

<footer>
```

- `type`: 커밋 유형 (feat, fix, docs, style, refactor, test, chore)
- `scope`: 변경 범위 (선택 사항)
- `subject`: 변경 내용 요약
- `body`: 상세 변경 내용 (선택 사항)
- `footer`: 이슈 참조 등 (선택 사항)

예시:

```
feat(auth): 2단계 인증 기능 추가

- TOTP 기반 2단계 인증 구현
- QR 코드 생성 기능 추가
- 백업 코드 생성 및 관리 기능 추가

Closes #123
```

## 풀 리퀘스트 프로세스

1. 작업이 완료되면 원격 저장소에 브랜치를 푸시합니다:

```bash
git push origin feature/your-feature-name
```

2. GitHub에서 `develop` 브랜치로 풀 리퀘스트를 생성합니다.

3. 풀 리퀘스트 템플릿을 작성하고 관련 이슈를 참조합니다.

4. 코드 리뷰를 기다립니다. 리뷰어의 피드백에 따라 필요한 변경을 수행합니다.

5. 모든 CI 테스트가 통과하고 리뷰어의 승인을 받으면 풀 리퀘스트가 병합됩니다.

## 테스트 가이드라인

모든 새로운 기능과 버그 수정에는 테스트가 포함되어야 합니다. 이 프로젝트는 pytest를 사용합니다:

```bash
# 테스트 실행
pytest

# 커버리지 보고서 생성
pytest --cov=.
```

## 문서화 가이드라인

- 모든 공개 API에는 문서 문자열(docstring)이 포함되어야 합니다.
- 복잡한 기능이나 알고리즘에는 인라인 주석을 추가하세요.
- API 변경 시 관련 문서를 업데이트하세요.

## 이슈 보고

버그를 발견하거나 새로운 기능을 제안하려면 GitHub 이슈를 생성해주세요. 이슈 템플릿을 사용하여 필요한 정보를 제공해주세요.

## 라이센스

이 프로젝트에 기여함으로써, 귀하는 귀하의 기여가 프로젝트의 라이센스 하에 배포된다는 것에 동의합니다. 