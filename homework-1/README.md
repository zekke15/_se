# CurlLab｜Python + HTML 網頁版 HTTP 測試工具

> 習題 1：製作一個類似 curl 的專案程式

CurlLab 是一個以 **HTML / CSS / JavaScript + Python Flask** 製作的簡易 API 測試工具，功能類似 curl / Postman 的入門版本。使用者不需要記複雜指令，只需在網頁輸入網址即可觀察 HTTP 請求與回應。

## 主要功能

- 選擇 GET、POST、PUT、PATCH、DELETE、HEAD 方法
- 輸入 HTTP URL
- 用 JSON 物件自訂請求 Headers
- 傳送文字或 JSON Body（GET / HEAD 除外）
- 查看狀態碼、回應耗時、回應大小
- 查看回應 Body（JSON 自動排版）及 Headers
- 快速範例、複製回應、錯誤提示
- 基本安全保護：禁止內網/本機位址、關閉重新導向、限制回應 1 MB

## 專案結構

```text
CurlLab_Web/
├── app.py                 # Flask 後端與 HTTP 請求處理
├── requirements.txt       # Python 依賴套件
├── templates/
│   └── index.html         # 網頁介面
├── static/
│   ├── style.css          # 深色版排版與響應式設計
│   └── app.js             # 網頁互動與呼叫後端
├── tests/
│   └── test_app.py        # 自動化測試
└── README.md              # 中文說明
```

## Windows / VS Code 執行教學

1. 安裝 Python 3.10 或更新版。
2. 解壓縮專案，使用 VS Code 開啟 `CurlLab_Web` 資料夾。
3. 開啟終端機，安裝套件：

```bash
py -m pip install -r requirements.txt
```

4. 啟動 Python 後端：

```bash
py app.py
```

5. 在瀏覽器開啟：**http://127.0.0.1:5000**

> macOS / Linux 可將 `py` 改成 `python3`。

## 使用範例

### GET 請求

- Method：`GET`
- URL：`https://jsonplaceholder.typicode.com/todos/1`
- Headers：`{"Accept":"application/json"}`
- 點擊「送出請求」，檢視回應狀態碼與 JSON。

### POST 請求

- Method：`POST`
- URL：`https://jsonplaceholder.typicode.com/posts`
- Body：

```json
{
  "title": "CurlLab 測試",
  "body": "Hello from Python!",
  "userId": 1
}
```

- 勾選「JSON 格式」，點擊「送出請求」。

> 以上使用第三方公開測試 API，須有網路且測試服務可用。請不要放入密碼、API 密鑰或私人資料。

## 自動化測試

在專案根目錄執行：

```bash
py -m unittest discover -s tests -v
```

測試使用 mock 模擬外部 HTTP 回應，不依賴真實外部 API。

## 專案原理

```text
使用者輸入 URL / Method / Headers / Body
            ↓
HTML + JavaScript 透過 fetch() 傳給 Flask
            ↓
Python Flask 驗證請求，使用 requests 向目標網站發送 HTTP 請求
            ↓
Flask 整理回應狀態、內容、標頭與時間
            ↓
JavaScript 在網頁右側展示結果
```

## 安全與限制

這是 **限定教學 API 網域的公開展示版**，不是通用 HTTP 代理。只允許 `jsonplaceholder.typicode.com` 與 `httpbin.org` 的 HTTPS (443) 請求，禁止內網位址、禁用自動轉址，並提供單程序的簡單請求頻率限制。仍不適合做為無限制的生產環境 HTTP 代理。只支援 HTTP/HTTPS；二進位回應可能以 Base64 顯示且不支援下載；最多讀取回應前 1 MB，請求最多 100 KB。部分網站會限制機器人連線或要求驗證。

## 可繳交的學習成果說明

本作業以 curl 的 HTTP 請求概念為基礎，改成圖形化網頁介面。與直接使用終端機 curl 不同，能以選單切換 HTTP 方法、輸入 Headers / Body，並在同一畫面觀察回應狀態碼、時間與內容。透過此次實作理解了前端 `fetch()`、Flask API、Python `requests` 和 HTTP 回應的關係。

開發過程可註明：使用 ChatGPT 協助產生程式架構、前後端程式碼、測試與文件，再自行執行、驗證、修正和截圖。


## 部署到 Render（公開網址）

1. 將此資料夾**內的所有檔案放在 GitHub 專案根目錄**（app.py 與 requirements.txt 必須位於根目錄）。
2. 打開 https://dashboard.render.com/ ，按 **New → Web Service**。
3. 連接剛建立的 GitHub repository，Language 選 **Python 3**，Instance Type 選 **Free**。
4. Build Command：`pip install -r requirements.txt`
5. Start Command：`gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 30`
6. 按 **Deploy Web Service**，完成後取得 `https://...onrender.com` 公開網址。

也可以選 Blueprint 使用隨附的 `render.yaml`。此專案不能用 GitHub Pages 單獨運行（因為包含 Flask 後端）。

**安全提醒**：公開展示版只能連線到白名單中的教學 API。不要加入任何內部服務、私有網域、IP 或包含秘密的 API。單程序限流不等於平台級防濫用保護。如果要做一般使用者都能輸入任意網址的公開 curl 服務，需要更完整的出口網路控管、驗證與資源限制。
