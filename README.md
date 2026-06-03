# ClinicalTrials.gov 쿼리-시각화 에이전트

## 개요

이 프로젝트는 ClinicalTrials.gov 데이터를 사용하여 자연어 임상시험 질문을 구조화된 시각화 명세로 변환하는 FastAPI 백엔드 서비스입니다.

이 서비스는 사용자 쿼리와 선택적 구조화 필터를 입력받고, ClinicalTrials.gov API에서 조건에 맞는 연구를 가져온 뒤, 데이터를 집계하여 프론트엔드에서 사용하기 쉬운 JSON 시각화 명세를 반환합니다.

## 실행 방법

가상환경을 생성합니다.

```bash
python -m venv .venv
```

Windows PowerShell에서 가상환경을 활성화합니다.

```bash
.\.venv\Scripts\Activate.ps1
```

macOS 또는 Linux에서 가상환경을 활성화합니다.

```bash
source .venv/bin/activate
```

의존성을 설치합니다.

```bash
pip install -r requirements.txt
```

서버를 실행합니다.

```bash
uvicorn app.main:app --reload
```

브라우저에서 대화형 API 문서를 엽니다.

```txt
http://127.0.0.1:8000/docs
```

## 선택 사항: 프론트엔드 데모

이 프로젝트에는 백엔드의 시각화 응답을 렌더링하는 간단한 브라우저 기반 데모가 포함되어 있습니다.

이 데모는 다음을 지원합니다.

* `bar_chart`
* `time_series`
* `grouped_bar_chart`
* `network_graph`
* `unsupported`

### 데모 실행 방법

먼저 FastAPI 백엔드를 실행합니다.

```bash
uvicorn app.main:app --reload
```

그다음 브라우저에서 데모 HTML 파일을 엽니다.

```txt
demo/index.html
```

Windows PowerShell에서는 다음 명령어로 열 수 있습니다.

```bash
start demo\index.html
```

macOS에서는 다음 명령어로 열 수 있습니다.

```bash
open demo\index.html
```

데모는 다음 주소로 요청을 보냅니다.

```txt
http://127.0.0.1:8000/visualize
```

데모를 사용하기 전에 백엔드 서버가 실행 중인지 확인하세요.

### 데모 참고 사항

이 데모는 의도적으로 가볍게 구성되어 있으며, CDN에서 제공되는 프론트엔드 라이브러리를 사용합니다.

* Chart.js: 막대 차트, 선 그래프, 그룹 막대 차트
* vis-network: 스폰서-약물 네트워크 그래프

## 테스트 실행

이 프로젝트에는 단위 테스트와 선택적 통합 테스트가 모두 포함되어 있습니다.

### 모든 테스트 실행

```bash
pytest
```

이 명령어는 단위 테스트와 통합 테스트를 모두 실행합니다.

### 단위 테스트만 실행

```bash
pytest -m "not integration"
```

단위 테스트는 실제 ClinicalTrials.gov API를 호출하지 않습니다. 내부 로직을 검증하기 위해 모의 연구 기록을 사용합니다.

단위 테스트는 다음을 검증합니다.

* 규칙 기반 플래너의 의도 분류
* 지원되지 않는 도메인 외부 쿼리 처리
* 임상시험 단계 분포 집계
* 중재 유형 분포 집계
* 스폰서-약물 네트워크의 엣지 가중치와 근거 일관성

### 통합 테스트만 실행

```bash
pytest -m integration
```

통합 테스트는 실제 ClinicalTrials.gov API를 호출합니다.

통합 테스트는 다음을 검증합니다.

* ClinicalTrials.gov API 연결성
* 실제 연구 기록 조회
* `protocolSection`, `nctId` 같은 필수 필드의 존재 여부
* 실제 ClinicalTrials.gov 데이터를 시각화 출력으로 변환하는 과정
* `trial_count`와 `evidence.supporting_record_count` 간의 일관성

참고: 통합 테스트는 네트워크 연결 상태와 ClinicalTrials.gov API 접근 가능 여부에 의존합니다.

## API 엔드포인트

### POST /visualize

임상시험 쿼리로부터 시각화 명세를 생성합니다.

요청 예시:

```json
{
  "query": "How has the number of trials for Pembrolizumab changed per year since 2015?",
  "drug_name": "Pembrolizumab",
  "start_year": 2015,
  "max_studies": 20
}
```

## 요청 스키마

`/visualize` 엔드포인트는 JSON 요청 본문을 받습니다.

| 필드                  | 타입      | 필수 여부 | 검증                    | 설명                                                                 |
| ------------------- | ------- | ----: | --------------------- | ------------------------------------------------------------------ |
| `query`             | string  |     예 | 최소 길이: 1, 최대 길이: 1000 | 자연어 임상시험 질문                                                        |
| `drug_name`         | string  |   아니오 | 선택 사항                 | ClinicalTrials.gov 중재 검색에 사용되는 약물 또는 중재 이름                         |
| `compare_drug_name` | string  |   아니오 | 선택 사항                 | 비교 쿼리에 사용되는 두 번째 약물 이름                                             |
| `condition`         | string  |   아니오 | 선택 사항                 | ClinicalTrials.gov 질환 검색에 사용되는 질병 또는 상태                            |
| `trial_phase`       | string  |   아니오 | 선택 사항                 | 연구 조회 후 적용되는 임상시험 단계 필터. 예: `PHASE1`, `PHASE2`, `PHASE3`, `PHASE4` |
| `sponsor`           | string  |   아니오 | 선택 사항                 | ClinicalTrials.gov 스폰서 검색에 사용되는 스폰서 이름                             |
| `country`           | string  |   아니오 | 선택 사항                 | ClinicalTrials.gov 위치 검색에 사용되는 국가 또는 지역                            |
| `start_year`        | integer |   아니오 | 선택 사항                 | 시계열 집계를 위한 시작 연도 하한                                                |
| `end_year`          | integer |   아니오 | 선택 사항                 | 시계열 집계를 위한 종료 연도 상한                                                |
| `overall_status`    | string  |   아니오 | 선택 사항                 | `RECRUITING` 같은 임상시험 상태 필터                                         |
| `max_studies`       | integer |   아니오 | 1~300, 기본값: 100       | 가져와서 집계할 최대 연구 수                                                   |
| `use_llm`           | boolean |   아니오 | 기본값: `true`           | LLM 보조 플래너를 사용할지 여부. `false`이면 백엔드는 결정론적 규칙 기반 플래너를 사용함            |

### 요청 예시

시계열 쿼리:

```json
{
  "query": "How has the number of trials for Pembrolizumab changed per year since 2015?",
  "drug_name": "Pembrolizumab",
  "start_year": 2015,
  "use_llm": false,
  "max_studies": 20
}
```

비교 쿼리:

```json
{
  "query": "Compare trial phases for Pembrolizumab versus Nivolumab.",
  "drug_name": "Pembrolizumab",
  "compare_drug_name": "Nivolumab",
  "max_studies": 20
}
```

국가별 모집 중 임상시험:

```json
{
  "query": "Which countries have the most recruiting trials for breast cancer?",
  "condition": "Breast Cancer",
  "overall_status": "RECRUITING",
  "max_studies": 20
}
```

## 응답 스키마

`/visualize` 엔드포인트는 두 개의 최상위 필드를 가진 JSON 객체를 반환합니다.

| 필드              | 타입     | 설명                                       |
| --------------- | ------ | ---------------------------------------- |
| `visualization` | object | 프론트엔드에서 렌더링 가능한 시각화 명세                   |
| `meta`          | object | 데이터 출처, 쿼리 해석, 연구 수, 인용 정책, 한계에 대한 메타데이터 |

### Visualization 객체

| 필드         | 타입              | 설명                                                                                        |
| ---------- | --------------- | ----------------------------------------------------------------------------------------- |
| `type`     | string          | `bar_chart`, `time_series`, `grouped_bar_chart`, `network_graph`, `unsupported` 같은 시각화 유형 |
| `title`    | string          | 사람이 읽기 쉬운 시각화 제목                                                                          |
| `encoding` | object          | 데이터 필드와 시각적 채널 간 매핑                                                                       |
| `data`     | array 또는 object | 차트에 바로 사용할 수 있는 데이터 포인트 또는 그래프 노드와 엣지                                                     |

### 응답 예시: 시계열

```json
{
  "visualization": {
    "type": "time_series",
    "title": "Trials for Pembrolizumab by Start Year",
    "encoding": {
      "x": {
        "field": "year",
        "type": "temporal"
      },
      "y": {
        "field": "trial_count",
        "type": "quantitative"
      }
    },
    "data": [
      {
        "year": 2015,
        "trial_count": 3,
        "citations": [
          {
            "nct_id": "NCT00000000",
            "field": "protocolSection.statusModule.startDateStruct.date",
            "excerpt": "2015"
          }
        ],
        "evidence": {
          "supporting_record_count": 3,
          "records": [
            {
              "nct_id": "NCT00000000",
              "field": "protocolSection.statusModule.startDateStruct.date",
              "value": "2015",
              "brief_title": "Example clinical trial title"
            }
          ]
        }
      }
    ]
  },
  "meta": {
    "source": "clinicaltrials.gov",
    "study_count": 20,
    "citation_policy": "각 집계 데이터에는 간결한 대표 인용과 검색된 `max_studies` 데이터셋 내의 전체 근거 기록이 포함됩니다."
  }
}
```

### Encoding 형식

표준 차트의 경우, `encoding` 객체는 차트 채널을 데이터 필드에 매핑합니다.

예시:

```json
{
  "x": {
    "field": "phase",
    "type": "nominal"
  },
  "y": {
    "field": "trial_count",
    "type": "quantitative"
  }
}
```

그룹 차트의 경우 `series` 채널도 포함됩니다.

```json
{
  "x": {
    "field": "phase",
    "type": "nominal"
  },
  "y": {
    "field": "trial_count",
    "type": "quantitative"
  },
  "series": {
    "field": "series",
    "type": "nominal"
  }
}
```

네트워크 그래프의 경우 응답은 `nodes`와 `edges`를 사용합니다.

```json
{
  "nodes": {
    "id": "id",
    "label": "label",
    "group": "type"
  },
  "edges": {
    "source": "source",
    "target": "target",
    "weight": "weight"
  }
}
```

## 시각화 유형별 데이터 형태

각 집계 데이터 항목에는 추적 가능성을 위해 간결한 `citations`와 전체 `evidence`가 모두 포함됩니다.

### 시계열

```json
{
  "year": 2015,
  "trial_count": 3,
  "citations": [],
  "evidence": {
    "supporting_record_count": 3,
    "records": []
  }
}
```

### 임상시험 단계 분포

```json
{
  "phase": "PHASE3",
  "trial_count": 12,
  "citations": [],
  "evidence": {
    "supporting_record_count": 12,
    "records": []
  }
}
```

### 중재 유형 분포

```json
{
  "intervention_type": "DRUG",
  "trial_count": 15,
  "citations": [],
  "evidence": {
    "supporting_record_count": 15,
    "records": []
  }
}
```

### 국가 분포

```json
{
  "country": "United States",
  "trial_count": 20,
  "citations": [],
  "evidence": {
    "supporting_record_count": 20,
    "records": []
  }
}
```

### 그룹 막대 차트 비교

```json
{
  "phase": "PHASE3",
  "series": "Pembrolizumab",
  "trial_count": 8,
  "citations": [],
  "evidence": {
    "supporting_record_count": 8,
    "records": []
  }
}
```

### 네트워크 그래프

```json
{
  "nodes": [
    {
      "id": "sponsor::Example Sponsor",
      "label": "Example Sponsor",
      "type": "sponsor"
    }
  ],
  "edges": [
    {
      "source": "sponsor::Example Sponsor",
      "target": "drug::Example Drug",
      "weight": 3,
      "citations": [],
      "evidence": {
        "supporting_record_count": 3,
        "records": []
      }
    }
  ]
}
```

표준 차트의 경우 `trial_count`는 `evidence.supporting_record_count`와 일치해야 합니다.

네트워크 그래프의 경우 엣지의 `weight`는 `evidence.supporting_record_count`와 일치해야 합니다.

## 지원하는 쿼리 유형과 시각화 유형

현재 시스템은 6가지 쿼리 카테고리를 지원합니다. 각 카테고리는 시각화 의도에 매핑됩니다.

| 쿼리 유형       | 예시 쿼리                                                                       | 필수 / 유용한 필드                                     | 시각화 유형              |
| ----------- | --------------------------------------------------------------------------- | ----------------------------------------------- | ------------------- |
| 시간 추세       | How has the number of trials for Pembrolizumab changed per year since 2015? | `drug_name`, `start_year`, `end_year`           | `time_series`       |
| 단계 분포       | How are lung cancer trials distributed across phases?                       | `condition` 또는 `drug_name`                      | `bar_chart`         |
| 중재 유형 분포    | What are the most common intervention types in lung cancer trials?          | `condition` 또는 `drug_name`                      | `bar_chart`         |
| 국가 분포       | Which countries have the most recruiting trials for breast cancer?          | `condition`, `overall_status`, `trial_phase`    | `bar_chart`         |
| 스폰서-약물 네트워크 | Show a sponsor drug network for melanoma trials.                            | `condition`                                     | `network_graph`     |
| 약물 단계 비교    | Compare trial phases for Pembrolizumab versus Nivolumab.                    | `drug_name`, `compare_drug_name`, `trial_phase` | `grouped_bar_chart` |

단계 필터가 적용된 국가 분포 예시:

```json
{
  "query": "Show Phase 3 lung cancer trials by country.",
  "condition": "Lung Cancer",
  "trial_phase": "PHASE3",
  "max_studies": 100
}
```

이 요청은 조회된 연구를 Phase 3 임상시험으로 필터링한 뒤, 국가별 막대 차트를 반환합니다.

도메인 외부 쿼리 예시:

```json
{
  "query": "Show me the population statistics of South Korea.",
  "max_studies": 10
}
```

이 요청은 임상시험 도메인 밖의 질문이기 때문에 ClinicalTrials.gov를 호출하지 않고 `unsupported` 응답을 반환합니다.

### 1. 시계열

시간에 따른 변화에 관한 질문에 사용됩니다.

예시:

```json
{
  "query": "How has the number of trials for Pembrolizumab changed per year since 2015?",
  "drug_name": "Pembrolizumab",
  "start_year": 2015,
  "max_studies": 20
}
```

반환값:

```txt
type = time_series
```

### 2. 임상시험 단계 분포

연구가 임상시험 단계별로 어떻게 분포되어 있는지에 대한 질문에 사용됩니다.

예시:

```json
{
  "query": "How are lung cancer trials distributed across phases?",
  "condition": "Lung Cancer",
  "max_studies": 20
}
```

반환값:

```txt
type = bar_chart
```

### 3. 중재 유형 분포

조건에 맞는 임상시험에서 가장 흔한 중재 유형을 묻는 질문에 사용됩니다.

예시:

```json
{
  "query": "What are the most common intervention types in lung cancer trials?",
  "condition": "Lung Cancer",
  "max_studies": 20
}
```

반환값:

```txt
type = bar_chart
```

응답은 다음 형식을 사용합니다.

```json
{
  "x": {
    "field": "intervention_type",
    "type": "nominal"
  },
  "y": {
    "field": "trial_count",
    "type": "quantitative"
  }
}
```

### 4. 국가 분포

위치 기반 질문, 특히 국가별 모집 중 임상시험에 관한 질문에 사용됩니다.

예시:

```json
{
  "query": "Which countries have the most recruiting trials for breast cancer?",
  "condition": "Breast Cancer",
  "overall_status": "RECRUITING",
  "max_studies": 20
}
```

반환값:

```txt
type = bar_chart
```

### 5. 스폰서-약물 네트워크

스폰서와 약물 또는 생물학적 중재 간의 관계 질문에 사용됩니다.

예시:

```json
{
  "query": "Show a sponsor drug network for melanoma trials.",
  "condition": "Melanoma",
  "max_studies": 20
}
```

반환값:

```txt
type = network_graph
```

네트워크 그래프 응답에는 다음이 포함됩니다.

* `nodes`: 스폰서와 약물
* `edges`: 스폰서에서 약물로 이어지는 관계
* `weight`: 해당 관계를 뒷받침하는 일치 연구 수

### 6. 약물 단계 비교

두 약물을 임상시험 단계별로 비교할 때 사용됩니다.

예시:

```json
{
  "query": "Compare trial phases for Pembrolizumab versus Nivolumab.",
  "drug_name": "Pembrolizumab",
  "compare_drug_name": "Nivolumab",
  "max_studies": 20
}
```

반환값:

```txt
type = grouped_bar_chart
```

## 설계 결정

### 1. 규칙 기반 대체 기능을 갖춘 LLM 보조 쿼리 플래너

이 시스템은 자연어 임상시험 질문을 구조화된 쿼리 계획으로 변환하기 위해 LLM 보조 쿼리 플래너를 사용합니다.

LLM은 다음 작업에만 사용됩니다.

* 의도 분류
* 시각화 유형 선택
* 약물명, 질환, 국가, 상태, 연도 범위 같은 구조화 필터 추출

LLM은 차트 값, 임상시험 수, 인용, 근거 기록을 생성하지 않습니다.

모든 시각화 값은 ClinicalTrials.gov API 응답으로부터 결정론적으로 계산됩니다.

LLM API 키가 없거나 LLM 응답이 유효하지 않은 경우, 시스템은 자동으로 규칙 기반 플래너로 대체됩니다. 이를 통해 LLM 키가 없어도 백엔드를 사용할 수 있습니다.

LLM 계획 예시:

```json
{
  "intent": "time_trend",
  "visualization_type": "time_series",
  "filters": {
    "drug_name": "Pembrolizumab",
    "condition": null,
    "start_year": 2015
  },
  "planner": "llm"
}
```

### 2. 도메인 외부 쿼리 차단

백엔드는 관련 없는 질문이 ClinicalTrials.gov API로 전송되는 것을 방지하기 위해 범위 검사 기능을 포함합니다.

LLM 플래너를 사용하기 전에, 시스템은 요청이 임상시험, 약물, 질병, 연구 단계, 스폰서, 중재, 모집 상태 또는 ClinicalTrials.gov 데이터와 관련되어 보이는지 확인하기 위해 가벼운 규칙 기반 검사를 수행합니다.

쿼리가 지원 도메인 밖에 있는 경우, 백엔드는 ClinicalTrials.gov를 호출하지 않고 `unsupported` 시각화 응답을 반환합니다.

지원되지 않는 요청 예시:

```json
{
  "query": "Show me the population statistics of South Korea.",
  "max_studies": 10
}
```

응답 형태 예시:

```json
{
  "visualization": {
    "type": "unsupported",
    "title": "Unsupported query",
    "encoding": {},
    "data": []
  },
  "meta": {
    "source": "clinicaltrials.gov",
    "study_count": 0,
    "reason": "This service only supports visualization queries based on ClinicalTrials.gov clinical trial data."
  }
}
```

### 3. 구조화 필드 우선

API는 `drug_name`, `condition`, `sponsor`, `country`, `overall_status`, `start_year` 같은 선택적 구조화 필드를 받습니다.

이 필드들은 자동 자연어 엔티티 추출보다 우선됩니다. 검증하기 쉽고 모호성이 적기 때문입니다.

예를 들어, 다음 요청은 자유 텍스트에서만 약물명을 추출하는 것보다 더 신뢰할 수 있습니다.

```json
{
  "query": "How has the number of trials for this drug changed over time?",
  "drug_name": "Pembrolizumab"
}
```

### 4. 프론트엔드 친화적 시각화 명세

응답은 추가 해석 없이 프론트엔드 렌더러가 사용할 수 있도록 설계되었습니다.

각 시각화에는 다음이 포함됩니다.

* `type`: 차트 유형
* `title`: 사람이 읽기 쉬운 제목
* `encoding`: 데이터 필드와 시각적 채널 간 매핑
* `data`: 차트에 바로 사용할 수 있는 데이터 포인트 또는 그래프 노드와 엣지

이 구조는 백엔드가 쿼리 해석과 집계를 담당하고, 프론트엔드는 렌더링에만 집중할 수 있게 합니다.

### 5. 원본 기록 기반 집계

백엔드는 AI를 사용해 차트 값을 생성하지 않습니다.

대신 ClinicalTrials.gov에서 연구 기록을 가져와 Python으로 다음과 같은 집계를 계산합니다.

* 시작 연도별 임상시험 수
* 임상시험 단계별 임상시험 수
* 국가별 임상시험 수
* 스폰서-약물 관계 가중치
* 두 약물 비교를 위한 단계별 수
* 중재 유형별 연구 수

### 6. 전체 근거 및 인용 전략

각 집계 시각화 데이터는 이를 계산하는 데 사용된 원본 ClinicalTrials.gov 기록으로 추적 가능하도록 구성됩니다.

각 데이터 항목의 응답에는 다음이 포함됩니다.

* `citations`: 간결한 표시를 위한 최대 3개의 대표 인용
* `evidence`: 조회된 데이터셋 내의 전체 지원 기록 목록

`evidence` 객체는 다음을 포함합니다.

```json
{
  "supporting_record_count": 3,
  "records": [
    {
      "nct_id": "NCT00000000",
      "field": "protocolSection.designModule.phases",
      "value": "PHASE3",
      "brief_title": "Example clinical trial title"
    }
  ]
}
```

막대 차트와 시계열의 경우 `evidence.supporting_record_count`는 `trial_count` 값과 일치합니다.

네트워크 그래프의 경우 `evidence.supporting_record_count`는 엣지 `weight`와 일치합니다.

이를 통해 시각화된 각 값이 집계에 사용된 원본 기록으로 추적될 수 있습니다.

응답을 읽기 쉽게 유지하기 위해 `citations`는 3개의 대표 기록으로 제한되며, `evidence.records`에는 조회된 `max_studies` 데이터셋 내의 전체 지원 기록 목록이 포함됩니다.

### 7. 실용적인 API 접근 처리

개발 중 로컬 환경에서 표준 HTTP 요청을 보냈을 때 ClinicalTrials.gov에서 `403 Forbidden` 응답이 반환되었습니다. 백엔드가 공식 API에 계속 연결되도록 하면서 로컬 요청 차단을 피하기 위해, 이 프로젝트는 API 요청에 브라우저 가장 기능이 있는 `curl_cffi`를 사용합니다.

데이터 출처는 여전히 공식 ClinicalTrials.gov API v2입니다.

### 8. 짧은 수명의 인메모리 API 캐시

ClinicalTrials.gov 클라이언트에는 반복적인 외부 API 호출을 줄이기 위한 짧은 수명의 인메모리 캐시가 포함되어 있습니다.

동일한 쿼리 파라미터와 `max_studies` 값이 캐시 TTL 내에 다시 요청되면, 백엔드는 ClinicalTrials.gov를 다시 호출하는 대신 캐시된 연구 기록을 재사용합니다.

현재 캐시 동작은 다음과 같습니다.

* 캐시 유형: 인메모리 딕셔너리
* 캐시 TTL: 300초
* 캐시 키: 정규화된 ClinicalTrials.gov 쿼리 파라미터와 `max_studies`

이는 로컬 데모 성능을 개선하고 외부 API에 대한 불필요한 부하를 줄입니다.

프로덕션 시스템에서는 Redis 같은 공유 캐시로 대체할 수 있습니다.

## 한계

### 1. LLM 플랜은 스키마로 제한되지만 완벽하지는 않음

기본 플래너는 LLM을 사용하여 쿼리 의도를 분류하고 약물명, 질환, 비교 약물, 연도 범위, 상태, 임상시험 단계 같은 구조화 필터를 추출합니다.

LLM은 차트 값, 임상시험 수, 인용, 근거 기록을 생성하지 않습니다.

그러나 LLM 기반 쿼리 해석은 모호하거나 매우 복잡한 질문에서 여전히 완벽하지 않을 수 있습니다. 이 위험을 줄이기 위해 백엔드는 LLM 출력을 검증하고 정규화하며, 결정론적 규칙 기반 플래너로 대체될 수 있습니다.

클라이언트는 다음 설정으로 LLM 플랜을 비활성화할 수도 있습니다.

```json
{
  "use_llm": false
}
```

### 2. 규칙 기반 플랜은 자연어 처리 범위가 제한적임

`use_llm`이 `false`로 설정되면 백엔드는 결정론적 키워드 기반 플랜을 사용합니다.

이 모드는 예측 가능하고 LLM API 키가 필요하지 않지만, `trend`, `phase`, `country`, `network`, `compare`, `intervention type` 같은 키워드를 포함하는 일반적인 쿼리 패턴만 지원합니다.

더 복잡하거나 간접적인 자연어 질문은 LLM 플래너 또는 추가 파싱 로직이 필요할 수 있습니다.

### 3. 조회된 데이터셋 범위

수치는 ClinicalTrials.gov에서 조회된 연구를 기반으로 계산되며, `max_studies`에 의해 제한됩니다.

따라서 이 값은 조회된 데이터셋 내의 수치로 해석해야 하며, 조건에 맞는 모든 ClinicalTrials.gov 기록 전체에 대한 완전한 전 세계 수치라고 볼 수는 없습니다.

응답을 관리 가능한 수준으로 유지하기 위해 `max_studies`는 300으로 제한됩니다.

### 4. 응답 크기와 근거 기록

각 집계 데이터 항목에는 다음이 포함됩니다.

* 최대 3개의 간결한 대표 `citations`
* 조회된 데이터셋 내의 전체 `evidence.records`

이는 추적 가능성을 높이지만, 하나의 차트 항목에 많은 연구가 기여하는 경우 응답 크기를 증가시킬 수 있습니다.

예를 들어, 조회된 연구 200개가 하나의 막대에 기여한다면, 해당 막대에는 200개의 근거 기록이 포함될 수 있습니다.

### 5. 조회 후 임상시험 단계 필터링

`trial_phase` 필터는 연구 조회 후에 적용됩니다.

예를 들어, 백엔드는 먼저 폐암 연구를 조회한 뒤 `PHASE3`에 해당하는 연구만 남길 수 있습니다.

이는 단계 필터가 적용된 결과가 조회된 `max_studies` 데이터셋으로 제한되며, ClinicalTrials.gov의 모든 일치 연구를 대표하지 않을 수 있음을 의미합니다.

### 6. 중재 유형 수치는 연구 단위 기준임

중재 유형 분포는 각 중재 유형이 등장하는 연구 수를 계산합니다.

개별 중재 항목의 총개수를 세는 것은 아닙니다.

예를 들어, 하나의 연구에 여러 개의 `DRUG` 중재가 있더라도, 해당 연구는 `DRUG` 중재 유형 수에 한 번만 기여합니다.

### 7. 스폰서-약물 네트워크 범위

네트워크 그래프는 현재 주요 스폰서와 약물 간 관계에 초점을 맞춥니다.

엣지의 `weight`는 스폰서-약물 관계를 뒷받침하는 조회된 연구 수를 나타냅니다.

아직 다음과 같은 더 복잡한 그래프는 지원하지 않습니다.

* 약물-약물 동시 출현 네트워크
* 연구자-기관 네트워크
* 스폰서-질환 네트워크
* 다중 홉 임상시험 관계 그래프

### 8. 제한적인 시각화 유형

현재 구현은 다음 시각화 유형을 지원합니다.

* `time_series`
* `bar_chart`
* `grouped_bar_chart`
* `network_graph`
* `unsupported`

산점도, 히스토그램, 타임라인, 더 풍부한 네트워크 레이아웃 같은 추가 시각화 유형은 나중에 추가할 수 있습니다.

### 9. 로컬 데모와 CORS 설정

로컬 브라우저 기반 데모를 지원하기 위해 CORS가 개방되어 있습니다.

이는 개발과 평가에는 편리하지만, 프로덕션 배포에서는 허용 origin을 신뢰할 수 있는 프론트엔드 도메인으로 제한해야 합니다.

### 10. 외부 API와 네트워크 의존성

백엔드는 ClinicalTrials.gov API에 의존합니다.

외부 API를 사용할 수 없거나, 느리거나, 속도 제한이 걸리거나, 응답 구조가 변경되면 백엔드는 오류 또는 불완전한 결과를 반환할 수 있습니다.

현재 API 연결과 응답 구조가 예상대로 작동하는지 검증하기 위해 통합 테스트가 포함되어 있습니다.

### 11. 인메모리 캐시 범위

API 캐시는 로컬 프로세스 메모리에 저장됩니다.

이는 로컬 개발과 평가에는 충분하지만, 여러 서버 프로세스나 배포 환경 간에 공유되지는 않습니다.

또한 서버가 재시작될 때마다 캐시는 초기화됩니다.

## 데이터 출처

이 프로젝트는 공식 ClinicalTrials.gov Data API v2를 사용합니다.

기본 엔드포인트:

```txt
https://clinicaltrials.gov/api/v2/studies
```

백엔드는 연구 기록을 가져오고 ClinicalTrials.gov 연구 구조의 필드를 사용합니다. 여기에는 다음이 포함됩니다.

* `protocolSection.identificationModule.nctId`
* `protocolSection.identificationModule.briefTitle`
* `protocolSection.statusModule.startDateStruct.date`
* `protocolSection.designModule.phases`
* `protocolSection.armsInterventionsModule.interventions`
* `protocolSection.sponsorCollaboratorsModule.leadSponsor.name`
* `protocolSection.contactsLocationsModule.locations`

## 출력 예시

`examples/` 디렉터리에는 실행 중인 백엔드에서 생성된 JSON 출력이 포함되어 있습니다.

포함된 예시:

| 파일                                                       | 쿼리 유형                       | 플래너 모드   | 시각화                 |
| -------------------------------------------------------- | --------------------------- | -------- | ------------------- |
| `examples/example_1_time_series.json`                    | 구조화된 약물 필드를 사용한 시간에 따른 임상시험 | 규칙 기반 강제 | `time_series`       |
| `examples/example_2_phase_distribution.json`             | 구조화된 질환 필드를 사용한 임상시험 단계 분포  | 규칙 기반 강제 | `bar_chart`         |
| `examples/example_3_country_distribution.json`           | 국가별 모집 중 임상시험               | 규칙 기반 강제 | `bar_chart`         |
| `examples/example_4_network.json`                        | 스폰서-약물 관계 네트워크              | 규칙 기반 강제 | `network_graph`     |
| `examples/example_5_comparison.json`                     | 구조화된 필드를 사용한 약물 단계 비교       | 규칙 기반 강제 | `grouped_bar_chart` |
| `examples/example_6_llm_time_series_query_only.json`     | LLM이 필터를 추출한 쿼리 전용 시간 추세    | LLM      | `time_series`       |
| `examples/example_7_llm_comparison_query_only.json`      | LLM이 필터를 추출한 쿼리 전용 약물 비교    | LLM      | `grouped_bar_chart` |
| `examples/example_8_intervention_type_distribution.json` | 중재 유형 분포                    | LLM      | `bar_chart`         |
| `examples/example_9_unsupported_query.json`              | 지원되지 않는 도메인 외부 쿼리           | 범위 검사    | `unsupported`       |

## AI / LLM 사용

이 프로젝트는 두 가지 플래너 모드를 지원합니다.

| 모드         | 사용 방법                                | 설명                              |
| ---------- | ------------------------------------ | ------------------------------- |
| LLM 보조 플래너 | `use_llm`을 생략하거나 `use_llm: true`로 설정 | LLM을 사용하여 자연어 쿼리에서 의도와 필터를 추출   |
| 규칙 기반 플래너  | `use_llm: false`로 설정                 | LLM을 호출하지 않고 결정론적 키워드 기반 계획을 사용 |

기본적으로 `use_llm`은 `true`입니다.

LLM은 쿼리 계획에만 사용됩니다. 자연어 임상시험 질문을 의도, 시각화 유형, 필터를 포함하는 구조화된 계획으로 변환합니다. 그런 다음 백엔드는 ClinicalTrials.gov에 쿼리하기 전에 이 계획을 검증하고 정규화합니다.

환경 변수:

```txt
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

`OPENAI_API_KEY`가 제공되지 않거나 LLM 응답이 유효하지 않은 경우, 백엔드는 규칙 기반 플래너로 대체됩니다.

### LLM 플래너 예시

백엔드는 자연어만 포함된 요청을 받을 수 있으며, LLM 플래너를 사용해 구조화 필터를 추출할 수 있습니다.

요청 예시:

```json
{
  "query": "Compare trial phases for Pembrolizumab versus Nivolumab.",
  "max_studies": 10
}
```

쿼리 해석 예시:

```json
{
  "intent": "comparison",
  "visualization_type": "grouped_bar_chart",
  "filters": {
    "drug_name": "Pembrolizumab",
    "compare_drug_name": "Nivolumab",
    "condition": null,
    "trial_phase": null,
    "sponsor": null,
    "country": null,
    "start_year": null,
    "end_year": null,
    "overall_status": null,
    "max_studies": 10
  },
  "planner": "llm"
}
```

그런 다음 백엔드는 이 검증된 필터를 사용해 ClinicalTrials.gov에 쿼리하고 차트 데이터를 생성합니다.

### 규칙 기반 플래너 예시

클라이언트는 `use_llm`을 `false`로 설정하여 LLM 계획을 비활성화할 수 있습니다.

```json
{
  "query": "How are lung cancer trials distributed across phases?",
  "condition": "Lung Cancer",
  "use_llm": false,
  "max_studies": 10
}
```

이 모드에서 백엔드는 다음을 반환합니다.

```json
{
  "planner": "rule_based_forced"
}
```

### 개발 참고 사항

AI 도구는 백엔드 아키텍처 계획, 문서 초안 작성, 트레이드오프 검토에도 사용되었습니다. 구현은 AI가 시각화 값을 직접 생성하지 않도록 검토되고 조정되었습니다.