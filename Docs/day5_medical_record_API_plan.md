# 4일차 - Record API 설계 (진료기록)

## 1. 설계 개요

진료기록(Record) API는 환자 본인의 진료기록 조회 기능과 스태프/어드민의 전체 진료기록 관리 기능을 제공합니다.

### 공통 정책

| 항목 | 정책 |
|------|------|
| Base URL | `/api/v1/records` |
| 인증 방식 | Bearer Access Token |
| 삭제 방식 | 소프트 삭제 (Soft Delete, `is_deleted` 플래그) |
| 기본 조회 범위 | `대기자` · `스태프` · `어드민` 본인 기록만 조회 가능 |
| 관리자 조회 범위 | `스태프` · `어드민` 전체 기록 조회 가능 |

---

### Record 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| id | integer | 진료기록 ID |
| user_id | integer | 진료받은 사용자 ID (FK → users.id) |
| doctor_id | integer | 담당 의사 사용자 ID (FK → users.id) |
| visit_date | date | 진료 날짜 (`YYYY-MM-DD`) |
| chief_complaint | string | 주요 증상 / 주소 |
| diagnosis | string | 진단명 |
| treatment | string | 치료 내용 |
| prescription | string | 처방 내용 (선택) |
| note | string | 비고 (선택) |
| is_deleted | boolean | 소프트 삭제 여부 (기본값: `false`) |
| created_at | datetime | 생성 일시 |
| updated_at | datetime | 수정 일시 |

---

## 2. API 명세

### REQ-RECORD-001 진료기록 목록 조회 (본인)

| 항목 | 내용 |
|------|------|
| Method | `GET` |
| Endpoint | `/api/v1/records/me` |
| 인증 | 필요 (`대기자` 이상) |
| 설명 | 현재 로그인한 사용자 본인의 진료기록 목록을 조회합니다. 소프트 삭제된 기록은 제외합니다. |

#### Query Parameters

| 이름 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| skip | integer | 0 | 건너뛸 개수 |
| limit | integer | 20 | 조회 개수 |

#### Response `200 OK`

```json
[
  {
    "id": 1,
    "user_id": 1,
    "doctor_id": 3,
    "visit_date": "2026-06-01",
    "chief_complaint": "두통 및 발열",
    "diagnosis": "급성 상기도 감염",
    "treatment": "해열제 처방 및 안정 권고",
    "prescription": "타이레놀 500mg, 3일치",
    "note": null,
    "is_deleted": false,
    "created_at": "2026-06-01T10:00:00",
    "updated_at": "2026-06-01T10:00:00"
  }
]
```

#### Error

| Status | 상황 |
|--------|------|
| 401 | 인증 실패 |

---

### REQ-RECORD-002 진료기록 단건 조회 (본인)

| 항목 | 내용 |
|------|------|
| Method | `GET` |
| Endpoint | `/api/v1/records/me/{record_id}` |
| 인증 | 필요 (`대기자` 이상) |
| 설명 | 본인의 특정 진료기록 1건을 조회합니다. 타인의 기록 조회 시 404를 반환합니다. |

#### Path Parameters

| 이름 | 타입 | 설명 |
|------|------|------|
| record_id | integer | 진료기록 ID |

#### Response `200 OK`

진료기록 응답 객체를 반환합니다.

#### Error

| Status | 상황 |
|--------|------|
| 401 | 인증 실패 |
| 404 | 기록을 찾을 수 없음 (삭제되었거나 본인 기록 아님) |

---

### REQ-RECORD-003 전체 진료기록 목록 조회 (스태프/어드민)

| 항목 | 내용 |
|------|------|
| Method | `GET` |
| Endpoint | `/api/v1/records` |
| 인증 | `스태프` 또는 `어드민` 필요 |
| 설명 | 모든 사용자의 진료기록 목록을 조회합니다. 소프트 삭제된 기록은 기본적으로 제외합니다. |

#### Query Parameters

| 이름 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| skip | integer | 0 | 건너뛸 개수 |
| limit | integer | 20 | 조회 개수 |
| user_id | integer | - | 특정 사용자 기록 필터 (선택) |
| visit_date_from | date | - | 조회 시작 날짜 필터 (선택, `YYYY-MM-DD`) |
| visit_date_to | date | - | 조회 종료 날짜 필터 (선택, `YYYY-MM-DD`) |
| include_deleted | boolean | false | 삭제된 기록 포함 여부 (선택) |

#### Response `200 OK`

```json
[
  {
    "id": 1,
    "user_id": 1,
    "doctor_id": 3,
    "visit_date": "2026-06-01",
    "chief_complaint": "두통 및 발열",
    "diagnosis": "급성 상기도 감염",
    "treatment": "해열제 처방 및 안정 권고",
    "prescription": "타이레놀 500mg, 3일치",
    "note": null,
    "is_deleted": false,
    "created_at": "2026-06-01T10:00:00",
    "updated_at": "2026-06-01T10:00:00"
  }
]
```

#### Error

| Status | 상황 |
|--------|------|
| 401 | 인증 실패 |
| 403 | 스태프 또는 어드민 권한 없음 |

---

### REQ-RECORD-004 진료기록 단건 조회 (스태프/어드민)

| 항목 | 내용 |
|------|------|
| Method | `GET` |
| Endpoint | `/api/v1/records/{record_id}` |
| 인증 | `스태프` 또는 `어드민` 필요 |
| 설명 | 특정 진료기록 1건을 조회합니다. 소프트 삭제된 기록도 조회 가능합니다. |

#### Path Parameters

| 이름 | 타입 | 설명 |
|------|------|------|
| record_id | integer | 진료기록 ID |

#### Response `200 OK`

진료기록 응답 객체를 반환합니다.

#### Error

| Status | 상황 |
|--------|------|
| 401 | 인증 실패 |
| 403 | 스태프 또는 어드민 권한 없음 |
| 404 | 기록을 찾을 수 없음 |

---

### REQ-RECORD-005 진료기록 생성 (스태프/어드민)

| 항목 | 내용 |
|------|------|
| Method | `POST` |
| Endpoint | `/api/v1/records` |
| 인증 | `스태프` 또는 `어드민` 필요 |
| 설명 | 특정 사용자의 진료기록을 생성합니다. |

#### Request Body

```json
{
  "user_id": 1,
  "visit_date": "2026-06-10",
  "chief_complaint": "복통 및 구역질",
  "diagnosis": "급성 위염",
  "treatment": "제산제 투여 및 식이 조절 권고",
  "prescription": "겔포스 현탁액, 3일치",
  "note": "스트레스성 위염 의심"
}
```

#### Response `201 Created`

```json
{
  "id": 2,
  "user_id": 1,
  "doctor_id": 3,
  "visit_date": "2026-06-10",
  "chief_complaint": "복통 및 구역질",
  "diagnosis": "급성 위염",
  "treatment": "제산제 투여 및 식이 조절 권고",
  "prescription": "겔포스 현탁액, 3일치",
  "note": "스트레스성 위염 의심",
  "is_deleted": false,
  "created_at": "2026-06-10T09:30:00",
  "updated_at": "2026-06-10T09:30:00"
}
```

#### Error

| Status | 상황 |
|--------|------|
| 401 | 인증 실패 |
| 403 | 스태프 또는 어드민 권한 없음 |
| 404 | 대상 사용자를 찾을 수 없음 |
| 422 | 요청값 검증 실패 |

---

### REQ-RECORD-006 진료기록 수정 (스태프/어드민)

| 항목 | 내용 |
|------|------|
| Method | `PATCH` |
| Endpoint | `/api/v1/records/{record_id}` |
| 인증 | `스태프` 또는 `어드민` 필요 |
| 설명 | 진료기록의 내용을 부분 수정합니다. 수정 가능한 필드는 `chief_complaint`, `diagnosis`, `treatment`, `prescription`, `note`입니다. |

#### Path Parameters

| 이름 | 타입 | 설명 |
|------|------|------|
| record_id | integer | 진료기록 ID |

#### Request Body

```json
{
  "diagnosis": "만성 위염",
  "note": "추가 검사 필요"
}
```

#### Response `200 OK`

수정된 진료기록 응답 객체를 반환합니다.

#### Error

| Status | 상황 |
|--------|------|
| 400 | 수정할 항목 없음 |
| 401 | 인증 실패 |
| 403 | 스태프 또는 어드민 권한 없음 |
| 404 | 기록을 찾을 수 없음 (삭제된 기록 포함) |

---

### REQ-RECORD-007 진료기록 삭제 (스태프/어드민)

| 항목 | 내용 |
|------|------|
| Method | `DELETE` |
| Endpoint | `/api/v1/records/{record_id}` |
| 인증 | `스태프` 또는 `어드민` 필요 |
| 설명 | 진료기록을 소프트 삭제합니다. `is_deleted` 를 `true`로 변경하며 실제 데이터는 보존됩니다. |

#### Path Parameters

| 이름 | 타입 | 설명 |
|------|------|------|
| record_id | integer | 진료기록 ID |

#### Response `200 OK`

```json
{
  "message": "진료기록이 삭제되었습니다."
}
```

#### Error

| Status | 상황 |
|--------|------|
| 401 | 인증 실패 |
| 403 | 스태프 또는 어드민 권한 없음 |
| 404 | 기록을 찾을 수 없음 또는 이미 삭제됨 |

---

## 3. 권한 매트릭스 요약

| 기능 | 대기자 | 스태프 | 어드민 |
|------|:------:|:------:|:------:|
| 본인 진료기록 목록 조회 | ✅ | ✅ | ✅ |
| 본인 진료기록 단건 조회 | ✅ | ✅ | ✅ |
| 전체 진료기록 목록 조회 | ❌ | ✅ | ✅ |
| 전체 진료기록 단건 조회 | ❌ | ✅ | ✅ |
| 진료기록 생성 | ❌ | ✅ | ✅ |
| 진료기록 수정 | ❌ | ✅ | ✅ |
| 진료기록 삭제 (소프트) | ❌ | ✅ | ✅ |

---

## 4. 설계 고려사항

- **소프트 삭제 일관성**: `is_deleted = true`인 기록은 본인 조회 API에서 자동 제외됩니다. 스태프/어드민은 `include_deleted=true` 파라미터로 삭제된 기록을 선택적으로 조회할 수 있습니다.
- **doctor_id 자동 할당**: 진료기록 생성 시 `doctor_id`는 요청 바디에 포함하지 않고, 현재 로그인된 스태프/어드민의 `user_id`로 자동 설정합니다.
- **타인 기록 보호**: 본인 조회 엔드포인트(`/me`)에서는 타인의 기록 ID를 입력해도 404를 반환하여 기록 존재 여부를 노출하지 않습니다.
- **날짜 필터**: 전체 조회 시 `visit_date_from` / `visit_date_to` 필터를 통해 기간별 조회가 가능합니다.
