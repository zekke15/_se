# CampusMate Docker｜校園作業與生活管理微服務系統

> 現代軟體工程 Docker 實作作業｜使用 Nginx + Python FastAPI + PostgreSQL + Docker Compose。**這是獨立的本機 Docker 系統，不是 GitHub Pages 靜態網站**。

## 1. 專案動機與使用價值

大學生的待辦作業和日常支出常常分散記錄。CampusMate Docker 讓使用者透過同一個網頁管理「作業截止日、完成狀態及生活記帳」。前端透過 API 讀寫資料，PostgreSQL 永久保存紀錄，即使重新建立容器也能保留（前提是沒有刪掉 Volume）。

- 使用價值：課業與生活支出一站式管理，適合學生自行使用。
- 技術價值：實際練習 Dockerfile、Compose、反向代理、資料庫、容器網路、Volume、健康檢查、REST API。
- 潛在商業模式：日後加上多使用者登入、帳務統計、雲端服務，可探索訂閱或校園客製化；目前只是示範，不宣稱已驗證市場。

## 2. Docker 學習重點與操作紀錄

| 概念／指令 | 用途 | 本專案示範 |
|---|---|---|
| Image 映像檔 | 程式和環境的打包模板 | `python:3.12-slim`、`nginx:1.27-alpine`、`postgres:16-alpine` |
| Container 容器 | 執行中的隔離服務 | `nginx`、`api`、`db` |
| Dockerfile | 定義 Python API 如何建置 | `backend/Dockerfile` |
| Docker Compose | 宣告多容器服務與網路 | `docker-compose.yml` |
| Port mapping | 將主機 8080 導到 Nginx 80 | `${WEB_PORT:-8080}:80` |
| Reverse Proxy | Nginx 轉送 `/api/*` 給 API | `nginx/default.conf` |
| Volume | 保存資料庫檔案 | `postgres_data` |
| Healthcheck | 等 PostgreSQL 可以接受連線 | `pg_isready` |
| Environment | 使用 `.env` 注入資料庫設定 | `.env.example` |

### 實作學習紀錄（供作業整理）

1. **規劃服務**：前端以 HTML/CSS/JS 完成，不需額外 Node.js；後端選擇 Python FastAPI；資料庫使用 PostgreSQL。
2. **撰寫 Dockerfile**：以 Python slim 為基底，安裝 `requirements.txt`，複製程式，並用 Uvicorn 監聽 `0.0.0.0:8000`。
3. **撰寫 Compose**：定義 `nginx`、`api`、`db`，由 Compose 建立內部網路；資料庫不直接對外公開。
4. **設定反向代理**：Nginx 對外提供網站，將 `/api/` 請求傳至 `http://api:8000`；前端以相對路徑 `/api/...` 呼叫。
5. **保存資料**：PostgreSQL 資料放在 named volume，`docker compose down` 不會刪除，`down -v` 才會刪除。
6. **驗證功能**：可透過網站新增／勾選／刪除任務、記錄／刪除支出，並查詢 API 健康狀態。

**測試紀錄的真實範圍**：專案生成環境沒有 Docker Engine，所以沒有宣稱已在容器內成功啟動。交作業前請在自己的 Docker Desktop 實際操作第 6 節的指令，並把結果和截圖附在報告。Python 的單元／API 測試與靜態設定檢查可獨立執行。

## 3. 技術架構

| 層級 | 技術 | 職責 |
|---|---|---|
| Web server / Proxy | Nginx | 網頁、CSS、JS 靜態檔案與反向代理 |
| 後端 API | Python 3.12 + FastAPI + Uvicorn | 任務／支出 CRUD、統計 API |
| ORM | SQLAlchemy 2.x | 操作資料庫 |
| Database | PostgreSQL 16 | 儲存任務與生活費資料 |
| Orchestration | Docker Compose | 管理服務、健康檢查及網路 |
| Test | pytest + FastAPI TestClient | API 行為驗證 |

### 資料流

```text
瀏覽器 http://localhost:8080
          |
          v
   [nginx :80]  ← 前端 HTML/CSS/JS
          |
          |  /api/* 反向代理
          v
  [api FastAPI :8000]
          |
          |  PostgreSQL 協定，內部主機名稱 db
          v
 [db PostgreSQL :5432]
          |
          v
 [postgres_data Volume]
```

只有 Nginx 的 8080 埠暴露給主機，API 和 PostgreSQL 僅在 Compose 內部網路互通。

## 4. 專案目錄

```text
campusmate-docker/
├── docker-compose.yml       # 多容器建置與運行
├── .env.example             # 資料庫設定範例
├── .gitignore               # 避免上傳本機密碼與資料
├── README.md                # 本文件
├── nginx/
│   └── default.conf         # Nginx 靜態網站 + /api/ 代理
├── frontend/
│   ├── index.html           # 網頁介面
│   ├── style.css            # 網頁樣式
│   └── app.js               # Fetch API 互動
└── backend/
    ├── Dockerfile           # API 映像檔定義
    ├── .dockerignore
    ├── requirements.txt
    ├── requirements-dev.txt
    ├── app/
    │   ├── __init__.py
    │   └── main.py          # ORM、資料模型及 REST API
    └── tests/
        └── test_api.py      # API 測試
```

## 5. 安裝前置條件（Windows 11 / VS Code）

1. 安裝 [Docker Desktop](https://www.docker.com/products/docker-desktop/) 並啟動 Docker Engine。Windows 使用 WSL2 後端。
2. 在 PowerShell 或 VS Code Terminal 確認：

```powershell
docker --version
docker compose version
docker info
```

3. 將專案 ZIP 解壓縮，VS Code 開啟 `campusmate-docker` 資料夾。
4. 在專案根目錄建立 `.env`（不要上傳真實密碼到 GitHub）：

```powershell
Copy-Item .env.example .env
```

打開 `.env`，把 `POSTGRES_PASSWORD` 換成自己設定的長隨機密碼；示範範例密碼不可用於公開部署。

## 6. Docker 實際操作紀錄（依序執行）

### 6.1 檢查 Compose 設定

```powershell
docker compose config
```

如果顯示合併後的服務設定而沒有錯誤，就表示 Compose 格式已成功解析。

### 6.2 建置並啟動全部容器

```powershell
docker compose up --build -d
```

指令說明：`up` 建立並啟動服務、`--build` 重建 API image、`-d` 背景執行。

### 6.3 查詢容器狀態與日誌

```powershell
docker compose ps
docker compose logs --tail=50 api
docker compose logs --tail=50 db
docker compose logs --tail=50 nginx
```

預期 `nginx`、`api`、`db` 均為 running；資料庫健康檢查應顯示 healthy。

### 6.4 開啟簡易 Web 介面

- **首頁**：http://localhost:8080/
- **API 健康檢查**：http://localhost:8080/api/health
- **API 文件**：`/docs` 並未經 Nginx 代理；可用 `docker compose exec api ...` 或自行新增代理設定（本作業優先展示 Web）。

健康檢查回應預期：

```json
{"status":"ok","service":"api","database":"connected"}
```

### 6.5 實際測試資料保存

1. 網站「作業待辦」輸入標題、課程、日期並新增。
2. 勾選「已完成」，確認儀表板待辦數減少。
3. 網站「生活記帳」新增 NT$120 午餐。
4. 執行 `docker compose down`，再 `docker compose up -d`，確認紀錄仍存在。

### 6.6 進入容器查 PostgreSQL

```powershell
docker compose exec db psql -U campususer -d campusmate -c "SELECT id, title, completed FROM tasks;"
docker compose exec db psql -U campususer -d campusmate -c "SELECT id, description, amount FROM expenses;"
```

如果自行修改了 `.env` 中的使用者和資料庫名稱，請同步調整以上 `psql` 指令。

### 6.7 停止／刪除

```powershell
docker compose stop       # 暫停服務，保留容器
docker compose start      # 重新啟動
docker compose down       # 刪除容器與預設網路，保留資料 volume
# 警告：下面指令會永久清空本專案的資料庫 volume！
docker compose down -v
```

### 6.8 可貼入作業報告的實際紀錄欄位

| 操作 | 指令 | 我的結果（請執行後填入） |
|---|---|---|
| 查看 Docker 版本 | `docker --version` | 待填 |
| 確認 Compose | `docker compose config` | 待填 |
| 啟動服務 | `docker compose up --build -d` | 待填 |
| 查看容器 | `docker compose ps` | 待填 |
| API 健康檢查 | 開 `/api/health` | 待填 |
| 任務 CRUD | 用網頁操作 | 待填 |
| Volume 持久化 | `down` 後 `up -d` | 待填 |

## 7. API 說明

| Method | Endpoint | 用途 |
|---|---|---|
| GET | `/api/health` | 檢查 API 與資料庫 |
| GET | `/api/stats` | 儀表板統計 |
| GET | `/api/tasks` | 查詢任務 |
| POST | `/api/tasks` | 新增任務 |
| PATCH | `/api/tasks/{id}` | 修改完成狀態 |
| DELETE | `/api/tasks/{id}` | 刪除任務 |
| GET | `/api/expenses` | 查詢支出 |
| POST | `/api/expenses` | 新增支出 |
| DELETE | `/api/expenses/{id}` | 刪除支出 |

新增任務請求：

```json
{"title":"完成 Docker 作業","course":"現代軟體工程","due_date":"2026-11-15","priority":"high"}
```

`priority` 只能是 `low` / `medium` / `high`。新增支出：

```json
{"description":"午餐","category":"餐飲","amount":120,"spent_on":"2026-11-07"}
```

## 8. PostgreSQL 資料表

`tasks`：`id` 主鍵、`title`、`course`、`due_date`、`priority`、`completed`。

`expenses`：`id` 主鍵、`description`、`category`、`amount`（整數新臺幣）、`spent_on`。

後端啟動時以 SQLAlchemy `create_all()` 初始化缺少的表。這是示範用途，不是正式的資料庫版本遷移（正式環境建議 Alembic）。

## 9. 三種測試：單元 / 系統 Web API / Playwright E2E

本專案針對老師要求實作三層測試。三種測試不可混為一談：

| 測試層級 | 程式 | 測試方式 | 是否需要 Docker | 
|---|---|---|---|
| 單元測試（server 必測） | `backend/tests/test_unit.py`、`backend/tests/test_api.py` | FastAPI TestClient + 獨立記憶體 SQLite | 否 |
| 系統測試（Web API） | `tests/test_system.py` | `httpx` 對正在執行的 Nginx / FastAPI / PostgreSQL 發真實 HTTP 請求 | 是 |
| E2E 測試（無頭瀏覽器） | `tests/test_e2e.py` | Playwright + headless Chromium 實際操作前端表單並檢查資料庫經 API 回讀 | 是 |

> 單元測試只使用獨立 SQLite 記憶體資料庫，不會更改 PostgreSQL；系統與 E2E 測試會在正在執行的資料庫建立帶有 `SYSTEM-` 或 `E2E-` 前綴的唯一測試資料，並在測試後刪除。**強烈建議只對自己專用的測試環境執行**，不對有真實使用者的正式網站執行。

### 9.1 Windows PowerShell 安裝測試工具

在 `campusmate-docker` **根目錄** 執行：

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-test.txt
python -m playwright install chromium
```

若 Windows 不允許執行啟動腳本，可以改用 `.venv\Scripts\python.exe -m pytest ...`，不需要調整 PowerShell 安全設定。

### 9.2 執行後端單元測試

```powershell
cd backend
python -m pytest tests -v
cd ..
```

單元測試涵蓋：健康檢查、CRUD、完成／未完成切換、資料驗證（空標題、非法日期／優先級、負數／零金額）、404、逾期統計，以及原有 API 流程。這些測試沒有經過 Nginx 或 PostgreSQL，**不能當成完整的系統測試**。

### 9.3 啟動真正的微服務

在專案根目錄：

```powershell
Copy-Item .env.example .env
# 請先編輯 .env 的 POSTGRES_PASSWORD
# 如已建立 .env，切勿覆寫原本的設定
docker compose up --build -d
docker compose ps
```

確認 `nginx`、`api`、`db` 正常，並開啟 `http://127.0.0.1:8080/`。如果 `.env` 中的 `WEB_PORT` 是 `127.0.0.1:8080`，本機也可正常測試。

### 9.4 執行系統測試（真實 Web API）

```powershell
python -m pytest tests/test_system.py -v
```

這項測試會經過：HTTP → Nginx Reverse Proxy → FastAPI → PostgreSQL。包含健康檢查、任務新增／查詢／修改、生活支出新增／查詢、統計、錯誤請求驗證，以及清理測試資料。

### 9.5 執行 E2E 測試（Playwright 無頭 Chromium）

```powershell
python -m pytest tests/test_e2e.py --browser chromium -v
```

Playwright 預設為 **headless 無頭模式**，不會彈出瀏覽器視窗。兩個 E2E 案例：

1. 在網頁新增作業 → 等待任務顯示 → 勾選完成 → 經 API 確認已完成 → 刪除。
2. 在網頁新增生活支出 → 等待列表顯示 → 經 API 確認寫入 → 刪除。

如需目視除錯，可額外使用 `--headed`，但繳交時仍應證明無頭模式可執行。

### 9.6 一次執行系統測試和 E2E

```powershell
python -m pytest tests -v --browser chromium
```

> 上述根目錄 pytest 設定只收集 `tests/`（系統＋E2E）。後端單元測試請依 9.2 另行執行。

### 9.7 測試另一個網址（例如測試 VPS）

預設的 `TEST_BASE_URL=http://127.0.0.1:8080`。遠端系統具有真實寫入及刪除功能，預設為安全起見**跳過**遠端測試。如確認該網址是自己控制的、無真實使用者資料的**專用測試環境**，才明確允許：

```powershell
$env:TEST_BASE_URL="https://你自己的測試網域"
$env:TEST_ALLOW_REMOTE="1"
python -m pytest tests/test_system.py -v
```

E2E 如有 Caddy Basic Auth 或其他登入保護，需先在測試環境安排測試帳號與驗證流程；目前測試套件預設假設沒有額外登入畫面，**不建議在正式公開的 VPS 執行**。

### 9.8 GitHub Actions 自動測試

`.github/workflows/test.yml` 內含兩個 Job：

- **unit**：安裝 Python 測試依賴，執行後端單元測試。
- **integration**：在 GitHub Actions Ubuntu 主機執行 Docker Compose 啟動 Nginx + API + PostgreSQL，等候健康檢查，執行 HTTP 系統測試、Playwright Chromium E2E，最後清除測試容器和 Volume。

只要把整個資料夾（含 `.github`）推送到 GitHub，即可到 **Actions** 查看工作流程結果。GitHub Actions 尚未在此環境實際執行，不能預先宣稱 CI 通過。

### 9.9 本次驗證結果與繳交截圖

- **已驗證**：在本次程式製作環境執行 `python -m pytest tests -v -q`，共 **15 項後端測試通過**（原有 1 項 + 新增 14 項）。
- **待於有 Docker 的環境驗證**：`tests/test_system.py`、`tests/test_e2e.py`、GitHub Actions 工作流程（本環境沒有 Docker Engine，不能宣稱已通過）。
- **建議截圖**：① 後端 pytest 綠色 passed ② `docker compose ps` 三個服務 ③ 系統測試 passed ④ Playwright E2E passed ⑤ GitHub Actions 成功執行畫面。

## 10. 常見問題

| 問題 | 建議排查 |
|---|---|
| `docker` 指令找不到 | 確認 Docker Desktop 已安裝並啟動；重新開終端機 |
| 無法連上 `localhost:8080` | `docker compose ps`、`docker compose logs nginx`；檢查 8080 是否被占用 |
| `POSTGRES_PASSWORD` 缺少 | 複製 `.env.example` 為 `.env` 並設定密碼 |
| `api` 啟動失敗 | 查看 `docker compose logs api`、`docker compose logs db` |
| 修改 `.env` 密碼後仍認證失敗 | 既有 Postgres volume 初始化後不會自動更換帳密；需在資料庫中修改使用者密碼或先備份資料後重建 volume |
| CSS 不見 | 確認 `frontend/style.css` 存在，Nginx volumes 路徑未更動 |
| 資料重開消失 | 檢查是否用過 `docker compose down -v` |
| GitHub Pages 不支援此系統 | GitHub Pages 只提供靜態檔；此專案需有 Docker 主機執行 nginx + API + DB |

## 11. 安全性與限制

**這是本機教學示範，沒有登入、個人帳號或權限隔離。不要直接對公開網際網路開放。** 正式上線需加入帳號認證、HTTPS、存取控制、備份、資料庫遷移與更嚴格的部署安全設定。此專案的 `.env` 已加入 `.gitignore`；不要在 Repo 或截圖中洩漏真實密碼。

## 12. 作業繳交清單

- [x] `README.md`：Docker 概念及操作指令紀錄
- [x] `backend/Dockerfile`：Python API 容器映像檔
- [x] `docker-compose.yml`：三個服務的 Compose 系統
- [x] `nginx/default.conf`：反向代理
- [x] `frontend/*`：簡易 Web 介面
- [x] `backend/app/main.py`：REST API + PostgreSQL ORM
- [ ] **請自行補上** Docker Desktop 三個容器執行截圖
- [ ] **請自行補上** localhost 網頁操作截圖
- [ ] **請自行補上** `docker compose ps` 與 `/api/health` 成功結果
- [x] **單元測試**：15 項本地測試通過
- [x] **系統測試與 E2E 腳本**：已實作
- [ ] **請在 Docker 環境執行** 系統測試和 Playwright E2E，附上實際結果

## 13. 參考文件

- [Docker Compose Quickstart](https://docs.docker.com/compose/gettingstarted/)
- [Docker Python Guide](https://docs.docker.com/guides/python/)
- [Docker Compose file reference](https://docs.docker.com/reference/compose-file/)
- [Nginx reverse proxy](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/)
