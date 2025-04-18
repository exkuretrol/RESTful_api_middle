``` mermaid
---
config:
  theme: forest
---

erDiagram
    User {
        bigint id PK "主鍵，使用者 ID"
        bigint department_id FK "所屬部門"
        bigint role_id FK "所屬職級 / 角色"
    }
    Department {
        bigint id PK "主鍵，部門 ID"
        varchar(32) name "部門名稱"
    }
    Role {
        bigint id PK "主鍵，職級 ID"
        varchar(32) name "職級名稱"
        bool is_supervisor "是否為主管"
    }
    LeaveCategory {
        bigint id PK "主鍵，假別 ID"
        varchar(32) name "假別名稱"
        enum reset_policy "重置規則：none / monthly / yearly"
        date effective_start_date "生效日期（起）"
        date effective_end_date "生效日期（止）"
    }
    RoleLeavePolicy {
        bigint id PK "主鍵"
        bigint role_id FK "職級"
        bigint category_id FK "假別"
        int default_amount "預設可請時數"
    }
    UserLeaveBalance {
        bigint id PK "主鍵"
        bigint user_id FK "使用者"
        bigint category_id FK "假別"
        int remaining_amount "剩餘時數"
    }
    LeaveRequest {
        uuid uuid PK "主鍵，請假單號"
        datetime submitted_at "送出時間"
        datetime effective_start_datetime "生效起始時間"
        datetime effective_end_datetime "生效結束時間"
        bigint category_id FK "請假類別"
        int status "狀態：0送出、1鎖定、2同意、3拒絕"
        text comment "申請附言"
        bigint request_user_id FK "申請人"
        bigint process_user_id FK "審核主管"
        datetime processed_at "審核時間"
    }
    LeaveRequestPerDay {
        bigint id PK "主鍵"
        uuid request_id FK "對應的請假單"
        date date "哪一天"
        time start_time "開始時間"
        time end_time "結束時間"
    }
    Department ||--|{ User : "一個部門擁有多位使用者"
    Role ||--|{ User : "一個職級可分派給多位使用者"
    LeaveRequest }|--|| User : "申請人（使用者）"
    LeaveRequest }|--|| User : "審核主管（使用者）"
    LeaveRequest }|--|| LeaveCategory : "請假所屬類別"
    LeaveRequest ||--|{ LeaveRequestPerDay : "一張請假單包含多天記錄"
    RoleLeavePolicy }|--|| Role : "職級對應規則"
    RoleLeavePolicy }|--|| LeaveCategory : "假別對應規則"
    UserLeaveBalance }|--|| User : "使用者剩餘假期"
    UserLeaveBalance }|--|| LeaveCategory : "假別對應剩餘"

```