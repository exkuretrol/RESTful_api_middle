# 題目：RESTful API 專案

>請盡可能達成以下文件需求，並請假設自己現在是以實際工作環境進行開發，請自身習慣修改專案結構，可視自身能力盡可能展現技術．

請開發一個請假管理系統，使用 Django + RESTful API 開發，系統包含以下要點：

- 支援員工提出請假申請
- 管理者進行審核
- 審核紀錄查詢功能

開發完成時須包含以下：

1. Web API server / DB
2. Test(pytest / unittest)( Test coverage is not mandatory. )
    - e.g.
      - 員工請假成功 / 拒絕請假權限
      - 管理員審核通過與拒絕
      - 員工只能查到自己的假單
3. Swagger
4. Doc ( README is mandatory )
5. API Server Dockerfile. (Option)

## 開發環境

- Python 3.X
- conda / pyenv
- 請依照個人習慣使用程式碼風格規範

## API 規格

- RESTful + Json
- ORM
- Swagger

  ``` bash
  pip install drf-yasg
  ```

## API 功能說明

- 一般員工功能

  |Method|Endpoint|說明|
  |-----|----------|----------|
  |POST|api/leaves|建立請假申請|
  |GET|api/leaves|查看自己的請假紀錄|

- Admin 功能

  |Method|Endpoint|說明|
  |------|--------|---|
  |GET |/api/manage/leaves/|查看所有 pending 的申請|
  |POST|/api/manage/leaves/<leave_id>/approve/ |核准請假|
  |POST|/api/manage/leaves/<leave_id>/reject/|駁回請假，可附加 comment 欄位|

- 權限邏輯
  - API 不需登入認證，請在後端以簡化邏輯判斷「是否為管理者」
  - 員工只能看到自己申請的假單
  - 僅 is_manager=True 的員工能執行審核操作

## 專案結構參考

``` bash
leave-management-system/
│
├── README.md                       # 專案說明文件
├── manage.py                       # Django 管理工具
├── .gitignore                      # Git 忽略設定
│
├── requirements/                  # 套件需求設定
│   └── ...                         # 其他說明文件
│
├── docs/                          # 文件資料夾
│   └── ...                         # 其他說明文件
│
├── src/                           # 主程式碼
│   ├── config/                     # Django 設定（settings, urls, wsgi, asgi）
│   │   ├── __init__.py
│   │   └── ...                     
│   │
│   ├── leave/                      # 請假模組（App）
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py      
│   │   ├── views.py      
│   │   ├── urls.py                
│   │   └── ...                         
│   │
│   └── templates/                  # HTML 模板（若使用 Django Template）
│       └── ...                         
│
├── tests/                         # 測試程式
│   └── ...                         
│
└── .env 
```

## Data & Database

- 自行建立 Local DB (DB類型不限)，根據上述需求產生schema跟table
- 自行產生測試資料提供API開發與測試（如預設員工帳號）

## 啟動參考

- 安裝

  ``` bash
  pip install -r requirements.txt
  ```

- 建立資料庫，建立預設使用者資料（可用 fixture 或 admin 手動）

  ``` bash
  python manage.py migrate

  python manage.py shell
  
  >>> from leave.models import User
  >>> User.objects.create(name='Alice', is_manager=False)
  >>> User.objects.create(name='Bob', is_manager=True)

- 啟動伺服器

  ``` bash
  python manage.py runserver
  ```

## 其他說明

- 若有其他需要 reviewer 留意的地方，也請補充於此
