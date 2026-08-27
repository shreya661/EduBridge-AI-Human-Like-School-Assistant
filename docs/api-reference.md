# 📡 XYZ AI — API Reference & Integration Guide

Comprehensive guide for all REST endpoints provided by the XYZ AI School Assistant platform.

## Base URLs
- **Production (Vercel)**: `https://xyz-ai-one.vercel.app`
- **Local Development**: `http://localhost:8000`
- **Interactive Swagger UI**: `/docs`
- **ReDoc UI**: `/redoc`

---

## 1. System & Diagnostic Endpoints

### `GET /health`
Probe service availability, database connectivity, and runtime metrics.

**Response `200 OK`**:
```json
{
  "status": "ok",
  "service": "XYZ AI",
  "database": "connected",
  "environment": "production"
}
```

---

## 2. Authentication & Session Management

### `POST /api/v1/auth/login`
Authenticates user credentials and sets an `HttpOnly` cryptographic session cookie.

**Request Body**:
```json
{
  "user_id": "STU10A88F2",
  "password": "Password@123"
}
```

**Response `200 OK`**:
```json
{
  "status": "authenticated",
  "user_id": "STU10A88F2",
  "name": "Aarav Patel",
  "role": "STUDENT"
}
```

### `GET /api/v1/auth/me`
Retrieves authenticated user session information.

### `POST /api/v1/auth/logout`
Invalidates active session token and clears auth cookie.

---

## 3. Conversational NLU & Tool Execution

### `POST /api/v1/nlu/analyze`
Parses raw user query into structured intent and resolved parameters.

**Request Body**:
```json
{
  "query": "Check my attendance for yesterday"
}
```

### `POST /api/v1/nlu/execute`
End-to-end execution: NLU $\rightarrow$ Zero-Trust Authorization Gate $\rightarrow$ Tool Dispatch.

**Headers**:
- `X-Session-ID`: `<active-session-id>` (or session cookie)

---

## 4. Academic Calendar & Timetables

### `GET /api/v1/calendar/events`
Query upcoming examinations, holidays, and school activities.

**Query Parameters**:
- `category` (optional): `exam`, `holiday`, `event`, `meeting`

### `GET /api/v1/calendar/timetable/{class_id}`
Get weekly schedule for a specific class section (e.g. `10-A`, `10-B`, `9-A`).

---

## 5. Attendance & Analytics

### `GET /api/v1/attendance/student/{student_id}`
Returns date-wise attendance records and percentage for authorized requester.

### `GET /api/v1/analytics/overview`
*(Principal only)* Returns institutional KPI metrics, attendance distribution, and class comparisons.

### `GET /api/v1/analytics/flagged-students`
*(Principal only)* Identifies students with attendance falling below the 75% threshold.

---

## 6. AI Tutor & Interactive Quizzes

### `POST /api/v1/chatbot/message`
Direct conversation with the AI Tutor assistant with subject context.

### `GET /api/v1/chatbot/quiz-topics`
Lists all supported mini-quiz curriculum modules.

### `GET /api/v1/chatbot/quiz/{topic}`
Returns 5 multiple-choice questions with answer choices and explanations.
