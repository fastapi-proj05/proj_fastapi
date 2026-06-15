
# 7일차 앱 실행화면

FastAPI 앱을 실행(`fastapi run app/main.py`) 후 `http://0.0.0.0:8000/` 에서 확인한 각 엔드포인트별 동작 화면입니다.

---

## DB 테이블 구조

### users 테이블

| # | Column Name | Data Type | Not Null | Auto Increment | Key | Extra |
|---|-------------|-----------|----------|----------------|-----|-------|
| 1 | id | int | ✅ | ✅ | PRI | auto_increment |
| 2 | email | varchar(100) | ✅ | | UNI | |
| 3 | password | varchar(255) | ✅ | | | |
| 4 | name | varchar(50) | ✅ | | | |
| 5 | department | enum('RESEARCH','MEDICAL','DEV') | ✅ | | | |
| 6 | gender | enum('M','F') | ✅ | | | |
| 7 | phone | varchar(20) | ✅ | | | |
| 8 | role | enum('PENDING','STAFF','ADMIN') | ✅ | | | |
| 9 | created_at | datetime | ✅ | | | |
| 10 | updated_at | datetime | ✅ | | | |

### patients 테이블

| Column | Type |
|--------|------|
| id | BIGINT (PK) |
| name | VARCHAR(30) |
| age | SMALLINT |
| phone | VARCHAR(11) |
| gender | ENUM(...) |
| uuid | CHAR(36) (UNI) |
| created_at | DATETIME |
| updated_at | DATETIME |

### medical_records 테이블

| Column | Type |
|--------|------|
| patient_uuid | CHAR(36) |
| diagnosis | VARCHAR(255) |
| treatment | VARCHAR(255) |
| uuid | CHAR(36) (PK) |
| created_at | DATETIME |
| updated_at | DATETIME |

---

## 사용자(Users) API

### 1. POST `/api/v1/users/` — 회원가입

**응답 코드:** `201 Created`

**Response Body 예시:**
```json
{
  "id": 0,
  "email": "string",
  "name": "string",
  "department": "연구",
  "gender": "M",
  "phone": "string",
  "role": "대기자",
  "created_at": "2026-06-12T07:44:51.540Z",
  "updated_at": "2026-06-12T07:44:51.540Z"
}
```

- 회원가입 성공 시 201 코드와 함께 생성된 유저 정보를 반환합니다.
- `role`은 기본값 `"대기자"(PENDING)`로 설정됩니다.

---

### 2. POST `/api/v1/users/login` — 로그인

**응답 코드:** `200 OK`

**Request Body:**
```json
{
  "email": "test@example.com",
  "password": "Test1234!"
}
```

**Response Body:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 2,
    "email": "test@example.com",
    "name": "테스트",
    "department": "연구",
    "gender": "M",
    "phone": "010-1234-5678",
    "role": "대기자",
    "created_at": "2026-06-12T07:44:52",
    "updated_at": "2026-06-12T07:44:52"
  }
}
```

- 로그인 성공 시 JWT `access_token`과 유저 정보를 반환합니다.
- 이후 요청에는 `Authorization: Bearer <access_token>` 헤더를 포함해야 합니다.

---

### 3. GET `/api/v1/users/me` — 내 정보 조회

**응답 코드:** `200 OK`

**Response Body:**
```json
{
  "id": 2,
  "email": "test@example.com",
  "name": "테스트",
  "department": "연구",
  "gender": "M",
  "phone": "010-1234-5678",
  "role": "대기자",
  "created_at": "2026-06-12T07:44:52",
  "updated_at": "2026-06-12T07:44:52"
}
```

- 인증된 사용자의 정보를 반환합니다.

---

### 4. PATCH `/api/v1/users/me` — 내 정보 수정

**응답 코드:** `200 OK`

**Response Body (수정 후):**
```json
{
  "id": 2,
  "email": "test@example.com",
  "name": "테스트",
  "department": "개발",
  "gender": "M",
  "phone": "010-9999-8888",
  "role": "대기자",
  "created_at": "2026-06-12T07:44:52",
  "updated_at": "2026-06-12T07:50:47"
}
```

- `department`가 `"연구"` → `"개발"`, `phone`이 `"010-9999-8888"`로 변경된 것을 확인할 수 있습니다.
- `updated_at` 타임스탬프가 갱신됩니다.

---

### 5. PATCH `/api/v1/users/me/password` — 비밀번호 변경

**응답 코드:** `200 OK`

**Response Body:**
```json
{
  "message": "비밀번호가 변경되었습니다."
}
```

---

### 6. POST `/api/v1/users/logout` — 로그아웃

**응답 코드:** `200 OK`

**Response Body:**
```json
{
  "message": "로그아웃되었습니다."
}
```

---

### 7. DELETE `/api/v1/users/me` — 회원 탈퇴

**응답 코드:** `200 OK`

**Response Body:**
```json
{
  "message": "회원 탈퇴가 완료되었습니다."
}
```

---

### 8. 관리자 전용 엔드포인트 — 권한 없음 시 오류

**응답 코드:** `403 Forbidden`

**Response Body:**
```json
{
  "detail": "관리자 권한이 필요합니다."
}
```

- `role`이 `ADMIN`이 아닌 사용자가 관리자 전용 API를 호출할 경우 반환됩니다.

---

## 환자(Patients) API

### 1. POST `/api/v1/patients/` — 환자 등록

**응답 코드:** `201 Created`

**Response Body:**
```json
{
  "name": "박지은",
  "gender": "FEMALE",
  "phone": "01055551111",
  "age": 30
}
```

- 환자 등록 성공 시 등록된 환자 정보를 반환합니다.

---

### 2. GET `/api/v1/patients/{uuid}` — 환자 조회

**응답 코드:** `200 OK`

**Response Body:**
```json
{
  "name": "박지은",
  "gender": "FEMALE",
  "phone": "01055551111",
  "age": 30
}
```

---

### 3. PATCH `/api/v1/patients/{uuid}` — 환자 정보 수정

**응답 코드:** `200 OK`

**Response Body (수정 후):**
```json
{
  "name": "박지은2",
  "gender": "FEMALE",
  "phone": "stringstri",
  "age": 30
}
```

- 수정된 환자 정보를 반환합니다.

---

### 4. 서버 오류 — Internal Server Error

**응답 코드:** `500 Internal Server Error`

**Response Body:**
```
Internal Server Error
```

- 잘못된 요청(예: 유효하지 않은 UUID 형식 등)으로 인해 서버 오류가 발생하는 경우입니다.
- `content-type: text/plain` 으로 반환됩니다.
- 해당 엔드포인트는 문서화되지 않은(Undocumented) 오류 케이스입니다.

---

## 정리

| 엔드포인트 | 메서드 | 설명 | 응답 코드 |
|-----------|--------|------|-----------|
| `/api/v1/users/` | POST | 회원가입 | 201 |
| `/api/v1/users/login` | POST | 로그인 (JWT 발급) | 200 |
| `/api/v1/users/me` | GET | 내 정보 조회 | 200 |
| `/api/v1/users/me` | PATCH | 내 정보 수정 | 200 |
| `/api/v1/users/me/password` | PATCH | 비밀번호 변경 | 200 |
| `/api/v1/users/logout` | POST | 로그아웃 | 200 |
| `/api/v1/users/me` | DELETE | 회원 탈퇴 | 200 |
| `/api/v1/patients/` | POST | 환자 등록 | 201 |
| `/api/v1/patients/{uuid}` | GET | 환자 조회 | 200 |
| `/api/v1/patients/{uuid}` | PATCH | 환자 정보 수정 | 200 |
