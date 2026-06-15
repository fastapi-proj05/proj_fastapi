# Medical Record API Documentation

## CREATE - 진료기록 등록

### Endpoint
`POST /patients/{patient_id}/records`

### Swagger UI 테스트

1. `POST /patients/{patient_id}/records` 엔드포인트를 클릭하여 확장합니다.
2. **Try it out** 버튼을 클릭합니다.
3. `patient_id`에 조회할 환자 ID를 입력합니다. (예: `1`)
4. Form Data 항목을 아래와 같이 입력합니다.

```
visit_date       : 2025-06-15
department       : 내과
doctor_name      : 이의사
chief_complaint  : 기침, 발열, 인후통
diagnosis        : 급성 상기도 감염
treatment        : 해열제 처방 및 충분한 휴식 권고
prescription     : 타이레놀 500mg 3일분
next_visit_date  : 2025-06-22
notes            : (선택사항)
attachments      : (파일 첨부 선택사항)
```

5. **Execute** 버튼 클릭 후 응답을 확인합니다.

### 예상 응답 (201 Created)

```json
{
  "status": "success",
  "message": "진료기록이 등록되었습니다.",
  "data": {
    "record_id": 101,
    "patient_id": 1,
    "visit_date": "2025-06-15",
    "department": "내과",
    "doctor_name": "이의사",
    "chief_complaint": "기침, 발열, 인후통",
    "diagnosis": "급성 상기도 감염",
    "treatment": "해열제 처방 및 충분한 휴식 권고",
    "prescription": "타이레놀 500mg 3일분",
    "next_visit_date": "2025-06-22",
    "notes": "",
    "attachments": [],
    "created_at": "2025-06-15T11:00:00"
  }
}
```

> ✅ `record_id`가 반환되면 정상 등록된 것입니다.

---

## GET - 진료기록 목록 조회

### Endpoint
`GET /patients/{patient_id}/records`

### Swagger UI 테스트

1. `GET /patients/{patient_id}/records` 엔드포인트를 클릭하여 확장합니다.
2. **Try it out** 버튼을 클릭합니다.
3. `patient_id`에 조회할 환자 ID를 입력합니다. (예: `1`)
4. 선택적으로 Query Parameter를 입력합니다.

```
department  : 내과        (선택 - 진료과 필터)
start_date  : 2025-01-01  (선택 - 조회 시작일)
end_date    : 2025-06-30  (선택 - 조회 종료일)
page        : 1           (선택 - 페이지 번호)
size        : 20          (선택 - 페이지당 항목 수)
```

5. **Execute** 버튼 클릭 후 응답을 확인합니다.

### 예상 응답 (200 OK)

```json
{
  "status": "success",
  "message": "진료기록 목록 조회 성공",
  "data": {
    "total": 2,
    "page": 1,
    "size": 20,
    "records": [
      {
        "record_id": 101,
        "visit_date": "2025-06-15",
        "department": "내과",
        "doctor_name": "이의사",
        "diagnosis": "급성 상기도 감염"
      },
      {
        "record_id": 95,
        "visit_date": "2025-05-20",
        "department": "내과",
        "doctor_name": "박의사",
        "diagnosis": "만성 위염"
      }
    ]
  }
}
```

> ✅ `total` 값과 `records` 배열의 길이가 일치하는지 확인합니다.

---

## GET DETAIL - 진료기록 상세 조회

### Endpoint
`GET /patients/{patient_id}/records/{record_id}`

### Swagger UI 테스트

1. `GET /patients/{patient_id}/records/{record_id}` 엔드포인트를 클릭하여 확장합니다.
2. **Try it out** 버튼을 클릭합니다.
3. Path Parameter를 입력합니다.

```
patient_id  : 1    (환자 ID)
record_id   : 101  (진료기록 ID)
```

4. **Execute** 버튼 클릭 후 응답을 확인합니다.

### 예상 응답 (200 OK)

```json
{
  "status": "success",
  "message": "진료기록 상세 조회 성공",
  "data": {
    "record_id": 101,
    "patient_id": 1,
    "patient_name": "홍길동",
    "visit_date": "2025-06-15",
    "department": "내과",
    "doctor_name": "이의사",
    "chief_complaint": "기침, 발열, 인후통",
    "diagnosis": "급성 상기도 감염",
    "treatment": "해열제 처방 및 충분한 휴식 권고",
    "prescription": "타이레놀 500mg 3일분",
    "next_visit_date": "2025-06-22",
    "notes": "",
    "attachments": [],
    "created_at": "2025-06-15T11:00:00",
    "updated_at": "2025-06-15T11:00:00"
  }
}
```

### 에러 케이스 테스트

존재하지 않는 `record_id` (예: `9999`) 입력 시 아래 응답을 확인합니다.

```json
{
  "status": "error",
  "message": "진료기록을 찾을 수 없습니다.",
  "data": null
}
```

> ✅ `404 Not Found` 상태 코드와 에러 메시지가 반환되면 정상입니다.

---

## UPDATE MEDICAL RECORD - 진료기록 수정

### Endpoint
`PATCH /patients/{patient_id}/records/{record_id}`

### Swagger UI 테스트

1. `PATCH /patients/{patient_id}/records/{record_id}` 엔드포인트를 클릭하여 확장합니다.
2. **Try it out** 버튼을 클릭합니다.
3. Path Parameter를 입력합니다.

```
patient_id  : 1    (환자 ID)
record_id   : 101  (수정할 진료기록 ID)
```

4. Request Body에 수정할 내용을 입력합니다. (변경할 필드만 포함)

```json
{
  "treatment": "해열제 처방, 항생제 추가 처방 및 충분한 휴식 권고",
  "prescription": "타이레놀 500mg 3일분, 아목시실린 250mg 5일분",
  "notes": "항생제 알레르기 여부 확인 완료"
}
```

5. **Execute** 버튼 클릭 후 응답을 확인합니다.

### 예상 응답 (200 OK)

```json
{
  "status": "success",
  "message": "진료기록이 수정되었습니다.",
  "data": {
    "record_id": 101,
    "patient_id": 1,
    "visit_date": "2025-06-15",
    "department": "내과",
    "doctor_name": "이의사",
    "chief_complaint": "기침, 발열, 인후통",
    "diagnosis": "급성 상기도 감염",
    "treatment": "해열제 처방, 항생제 추가 처방 및 충분한 휴식 권고",
    "prescription": "타이레놀 500mg 3일분, 아목시실린 250mg 5일분",
    "next_visit_date": "2025-06-22",
    "notes": "항생제 알레르기 여부 확인 완료",
    "updated_at": "2025-06-15T13:00:00"
  }
}
```

> ✅ `updated_at` 값이 수정 시간으로 갱신되었는지 확인합니다.

---

## DELETE MEDICAL RECORD - 진료기록 삭제 >> WORKING

### Endpoint
`DELETE /patients/{patient_id}/records/{record_id}`

### Swagger UI 테스트

1. `DELETE /patients/{patient_id}/records/{record_id}` 엔드포인트를 클릭하여 확장합니다.
2. **Try it out** 버튼을 클릭합니다.
3. Path Parameter를 입력합니다.

```
patient_id  : 1    (환자 ID)
record_id   : 101  (삭제할 진료기록 ID)
```

4. **Execute** 버튼 클릭 후 응답을 확인합니다.

### 예상 응답 (200 OK)

```json
{
  "status": "success",
  "message": "진료기록이 삭제되었습니다.",
  "data": null
}
```

### 삭제 확인

삭제 후 동일한 `record_id`로 GET 상세 조회를 시도하면 아래 응답이 반환되어야 합니다.

```json
{
  "status": "error",
  "message": "진료기록을 찾을 수 없습니다.",
  "data": null
}
```

> ✅ 삭제 후 `404 Not Found`가 반환되면 정상적으로 삭제된 것입니다.

---

## 테스트 시나리오 순서

원활한 테스트를 위해 아래 순서로 진행하는 것을 권장합니다.

```
1. 환자 등록       POST /patients
   ↓
2. 진료기록 등록   POST /patients/{patient_id}/records
   ↓
3. 목록 조회       GET  /patients/{patient_id}/records
   ↓
4. 상세 조회       GET  /patients/{patient_id}/records/{record_id}
   ↓
5. 정보 수정       PATCH /patients/{patient_id}/records/{record_id}
   ↓
6. 삭제            DELETE /patients/{patient_id}/records/{record_id}
   ↓
7. 삭제 확인       GET  /patients/{patient_id}/records/{record_id}  → 404 확인
```
