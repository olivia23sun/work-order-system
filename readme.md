# 工單管理系統 Task Management System

以 Python + FastAPI 建立的內部工單管理後端系統，模擬製造業工單流程，支援任務建立、狀態更新與操作紀錄追蹤。

此專案重點在於「資料流程設計」與「後端系統思維」，而非 UI。

---

## 技術架構

| 項目 | 技術 |
|------|------|
| 語言 | Python 3.10+ |
| 後端框架 | FastAPI |
| 資料庫 | MySQL |
| ORM | SQLAlchemy |
| 資料驗證 | Pydantic |

---

## 系統架構

```
Client (Swagger / Postman)
        ↓
FastAPI (main.py)
        ↓
Database Session (Depends)
        ↓
Models (Task, TaskLog, User)
        ↓
Database
```

---

## 功能說明

- 建立工單（Task）
- 查詢所有工單 / 單一工單
- 更新工單狀態（pending → in_progress → done）
- 刪除工單
- 查詢工單操作紀錄（TaskLog）
- 每次狀態變更自動寫入 log

---

## 資料表設計

```
users        → 操作人員（id, name, role）
tasks        → 工單主體（id, title, description, status, user_id, created_at）
task_logs    → 操作紀錄（id, task_id, action, created_at）
```

**為什麼 task_logs 要獨立成一張表？**
- 工單狀態會被多次修改，每次修改都需要被記錄
- 避免把歷史資料塞在 tasks 裡，保持主表乾淨
- 符合實務系統的「可追蹤性」需求

---

## 本地啟動方式

**1. 建立 .env 設定**
```bash
DATABASE_URL=mysql+pymysql://root:root@localhost/work_order
```

**2. 安裝套件**
```bash
pip install -r requirements.txt
```

**3. 啟動伺服器**
```bash
uvicorn main:app --reload
```

**4. 開啟 API 文件**
```
http://localhost:8000/docs
```

---

## API 列表

| Method | 路徑 | 說明 |
|--------|------|------|
| POST | `/users` | 建立使用者（員工） |
| POST | `/tasks` | 建立新工單 |
| GET | `/tasks` | 查詢所有工單 |
| GET | `/tasks/{task_id}` | 查詢單一工單 |
| PUT | `/tasks/{task_id}` | 更新工單狀態 |
| DELETE | `/tasks/{task_id}` | 刪除工單 |
| GET | `/tasks/{task_id}/logs` | 查詢工單操作紀錄 |

---

## 錯誤處理

| 狀況 | HTTP 狀態碼 |
|------|------------|
| title 為空 | 422 |
| 找不到 task | 404 |
| 資料庫錯誤 | 500（rollback） |

---

## 設計說明

- 使用 `Depends(get_db)` 統一管理 DB Session 生命週期，避免連線洩漏
- 所有錯誤統一使用 `HTTPException` 回傳，格式一致
- 狀態變更時自動寫入 `task_logs`，保留完整操作歷程
- 資料驗證透過 Pydantic Schema 處理，與 API 層解耦

**資料流程**
```
Client 發 request
    → FastAPI 接收並驗證參數
    → 寫入資料庫
    → commit / rollback
    → 回傳結果
```

---

## 未來可擴充

- 狀態流程控管（pending → in_progress → done）
- 分頁查詢（大量資料）
- 常用欄位加上 index（task_id、status）
