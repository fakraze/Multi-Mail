# Multi Mail

Multi Mail 是在本機執行的 Gmail 郵件介面。前端使用 React、TypeScript 與 Vite；後端使用 FastAPI 呼叫 Gmail API，並以 SQLAlchemy 將連線帳號與郵件列表快取存入 SQLite。

目前的連線流程使用一個 Gmail 帳號。首頁直接開啟時顯示範例郵件；完成 Google 授權後，前端會顯示該帳號的真實郵件。

## 功能

- 透過 Google OAuth 連接 Gmail，讀取 Inbox、Starred、Important 與使用者建立的標籤。
- 以每頁最多 50 封郵件顯示列表，並使用 Gmail 的分頁 token 切換頁面。
- 使用 Gmail 查詢語法搜尋郵件，開啟郵件並閱讀純文字內容。
- 對 Inbox 郵件加星號、取消星號，以及新增或移除 Important 或使用者標籤；操作完成後向 Gmail 讀回確認。
- 建立或刪除 Gmail 使用者標籤。
- 將已請求的郵件列表頁面快取到本機 SQLite。

## 專案結構

| 路徑 | 用途 |
| --- | --- |
| `frontend/src/pages/` | 範例頁、登入頁與已連線郵件頁 |
| `frontend/src/services/mailbox.ts` | 前端呼叫後端 API 與回應資料驗證 |
| `frontend/src/types/mail.ts` | 前端郵件與標籤型別 |
| `backend/app/api/` | OAuth 與郵件 API 路由 |
| `backend/app/services/` | Gmail、OAuth 與快取邏輯 |
| `backend/app/schemas/mailbox.py` | API 的 Pydantic 資料模型 |
| `backend/app/models/database.py` | SQLAlchemy 資料表與 SQLite 設定 |
| `backend/tests/` | 後端測試 |

## 本機啟動

1. 在 Google Cloud 啟用 Gmail API，設定 OAuth 同意畫面，建立 **Web application** 類型的 OAuth 用戶端。授權重新導向 URI 設為 `http://127.0.0.1:8000/auth/google/callback`。若應用程式仍在測試模式，請將要連接的 Google 帳號加入測試使用者。
2. 複製 `backend/.env.example` 為 `backend/.env`，填入 `GOOGLE_CLIENT_ID` 與 `GOOGLE_CLIENT_SECRET`。
3. 在兩個終端機分別執行：

   ```powershell
   cd backend
   python -m pip install -r requirements.txt
   python run.py
   ```

   ```powershell
   cd frontend
   npm install
   npm run dev
   ```

4. 開啟 `http://localhost:5173/`，按 **Connect Gmail**，再按 **Continue with Google** 完成授權。

後端預設位址是 `http://127.0.0.1:8000`。若變更後端位址，將前端的 `VITE_BACKEND_URL` 設為對應的本機 origin；若變更前端位址，設定後端的 `FRONTEND_URL`。`GOOGLE_REDIRECT_URI` 必須與 Google Cloud 中登記的 URI 完全一致，且路徑為 `/auth/google/callback`。後端會先讀取環境變數，再使用 `backend/.env` 的值。

`python run.py` 會關閉 HTTP access log，避免 OAuth callback URL 中的授權碼進入日誌。需要自動重載時，請在 `backend/` 執行 `uvicorn app.main:app --reload --no-access-log`。

## 前後端資料流

1. 前端的連線按鈕導向 `GET /auth/google/start`；後端建立 state cookie 並重新導向 Google。
2. Google 呼叫 `GET /auth/google/callback`；後端驗證 state、交換 OAuth token、查詢 Gmail 帳號地址，並將帳號與 token 存入 SQLite。
3. 後端以 `303` 重新導向到前端首頁，附上非機密的 `?gmail=connected`。前端據此進入已連線郵件頁。
4. 前端只向本機後端請求郵件資料。OAuth token 不會進入前端 API 回應。直接開啟沒有 `gmail=connected` 的首頁會顯示範例郵件。

## 後端 API 規格

以下路徑以預設後端 origin `http://127.0.0.1:8000` 為基準。郵件 API 的 `account` 欄位是 Gmail 地址，可由 `GET /api/mailbox` 的回應取得。

| 方法與路徑 | 請求 | 成功回應 |
| --- | --- | --- |
| `GET /` | 無 | `200 {"status":"ok"}` |
| `GET /auth/google/start` | 無 | 重新導向 Google；設定短效、HTTP-only、SameSite=Lax 的 state cookie |
| `GET /auth/google/callback` | Google 提供的 `code`、`state`，或 `error` | 成功時 `303` 導回前端 `?gmail=connected`；失敗時回傳不含 token 的 HTML 錯誤頁 |
| `GET /api/mailbox` | 可選 `label_id`、`q`、`page_token` | `200 Mailbox` |
| `GET /api/messages/{message_id}` | Gmail message ID | `200 MessageDetail` |
| `PATCH /api/messages/{message_id}/labels` | JSON `LabelChange`；星號也透過此路由設定 `STARRED` | `200 MessageLabels` |
| `POST /api/labels` | JSON `CreateLabel` | `200 MailLabel` |
| `DELETE /api/labels/{label_id}` | 必填 query `account` | `204`，無回應內容 |

### `GET /api/mailbox`

- 不帶 `label_id` 或 `q` 時，讀取 Inbox。
- `label_id=STARRED`、`label_id=IMPORTANT` 或回應中使用者標籤的 ID，會篩選 Inbox 郵件。
- `q` 是傳給 Gmail 的搜尋字串；搜尋不加 Inbox 篩選。`q` 與 `label_id` 不可同時使用，也不可傳空白查詢。
- `page_token` 是上一頁回傳的 `next_page_token`；每頁最多 50 封。沒有下一頁時為 `null`。
- `labels` 只包含 Important 與使用者標籤。Important 的 `kind` 為 `system`，可加到郵件但不可刪除；使用者標籤的 `kind` 為 `user`，可加到郵件也可刪除。

回應結構：

```json
{
  "account": "me@example.com",
  "labels": [
    {
      "id": "IMPORTANT",
      "name": "Important",
      "kind": "system",
      "modifiable": true,
      "deletable": false
    }
  ],
  "messages": [
    {
      "id": "gmail-message-id",
      "account": "me@example.com",
      "sender": "Alice",
      "subject": "Hello",
      "snippet": "Message preview",
      "received_at": "2026-10-12T00:00:00+00:00",
      "starred": false,
      "label_ids": ["INBOX"]
    }
  ],
  "next_page_token": null
}
```

`received_at` 是 ISO 8601 UTC 時間字串。每封郵件都帶有來源 `account`。Gmail thread ID 只存在後端快取，不在目前的列表 API 回應中。

### `GET /api/messages/{message_id}`

回傳與列表郵件相同的欄位，另外包含 `body: string`。後端即時向 Gmail 讀取郵件，將內容轉為純文字；這個 API 不使用 SQLite 內的郵件本文快取。搜尋結果中的非 Inbox 郵件也可以閱讀。

### `PATCH /api/messages/{message_id}/labels`

目前沒有獨立的 `/star` API。Gmail 的星號是 `STARRED` 標籤：前端點擊郵件列表或郵件內容中的星號時，會呼叫 `setMessageLabel()`，送出這個 `PATCH` 請求。後端將 `label_id=STARRED` 與 `present=true` 轉成加星號；`present=false` 轉成取消星號，再透過 Gmail `users.messages.modify` 執行。

加星號請求範例：

```json
{
  "account": "me@example.com",
  "label_id": "STARRED",
  "present": true
}
```

取消星號時使用同一路徑和 `label_id`，只需將 `present` 改為 `false`。其他標籤也是以 `present=true` 加入、`false` 移除。`label_id` 可用 `STARRED`、`IMPORTANT` 或目前 Gmail 帳號的使用者標籤 ID。後端會檢查 `account` 與已連線帳號相同、目標郵件仍在 Inbox，並在修改 Gmail 後讀回確認。成功回應如下：

```json
{
  "id": "gmail-message-id",
  "account": "me@example.com",
  "label_ids": ["INBOX", "STARRED"],
  "starred": true
}
```

### 標籤 API

`POST /api/labels` 的請求為 `{"account":"me@example.com","name":"Work"}`，成功時回傳 `{ "id", "name", "kind": "user", "modifiable": true, "deletable": true }`。名稱不可為空、不可超過 225 個字元，且不可與帳號中既有的 Gmail 標籤同名。

`DELETE /api/labels/{label_id}?account=me%40example.com` 只接受使用者標籤 ID。後端向 Gmail 刪除並確認標籤已不存在；刪除標籤不會刪除郵件。

郵件 API 的可預期錯誤會以 JSON `{"detail":"..."}` 回傳：無可用授權通常為 `401`、無效查詢或 ID 為 `400`、帳號變更或郵件不在 Inbox 等衝突為 `409`、Gmail 請求失敗為 `502`。FastAPI 的參數驗證錯誤使用 `422`。

## SQLite 資料庫規格

資料庫位置：`backend/mail.db`。後端第一次需要存取資料庫時會建立檔案與資料表。資料庫只由後端讀寫，已列入 `.gitignore`。

| 資料表 | 欄位 | 用途 |
| --- | --- | --- |
| `accounts` | `id` (PK)、`email_address` (unique)、`access_token`、`refresh_token` (nullable) | 儲存目前連線的一個 Gmail 帳號及 OAuth 憑證 |
| `cached_messages` | `account_id` + `gmail_id` (複合 PK)、`thread_id`、`sender`、`subject`、`snippet`、`received_at`、`starred`、`label_ids_json` | 儲存郵件列表需要的摘要；`account_id` 是指向 `accounts.id` 的外鍵 |
| `cached_pages` | `account_id` + `cache_key` (複合 PK)、`message_ids_json`、`labels_json`、`next_page_token` (nullable) | 儲存某次列表請求的郵件順序、側欄標籤與下一頁 token；`account_id` 是指向 `accounts.id` 的外鍵 |

`cache_key` 是 `[label_id, q, page_token]` 的 JSON 字串，區分 Inbox、標籤、搜尋和分頁。讀取列表時，後端先查找對應頁面；命中時直接組合 `cached_pages` 與 `cached_messages` 回應，未命中時才向 Gmail 取資料並寫入 SQLite。空頁面也會快取。

星號或標籤操作經 Gmail 確認成功後，後端會清除 `cached_pages`，讓後續列表請求重新讀取 Gmail。重新授權會替換目前帳號並清除郵件與頁面快取；同一帳號重新授權而 Google 未回傳 refresh token 時，保留原有的 refresh token。舊版 `backend/oauth_tokens.json` 若存在，首次讀取授權時會驗證帳號、遷移到 SQLite，然後移除舊檔。郵件本文不寫入資料庫。

`mail.db` 包含明文 OAuth 憑證與郵件摘要，請只保留在自己的本機環境，不要提交、分享或記錄其內容。

## 檢查與測試

在 `backend/` 執行：

```powershell
python -m unittest discover -s tests
python check_gmail_access.py
```

第一個命令執行後端測試；第二個命令使用已儲存的授權驗證 Gmail 帳號連線。前端檢查在 `frontend/` 執行：

```powershell
npm run lint
npm run build
```
