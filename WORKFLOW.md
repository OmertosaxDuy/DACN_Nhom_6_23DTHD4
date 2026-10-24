# System & AI Agent Workflow

## 1. Workflow tổng quan

Hệ thống hoạt động theo vòng lặp Adaptive Cyber Deception:

```text
Observe → Analyze → Decide → Act → Adapt → Observe Again
```

Luồng tổng thể:

```text
Kali Attacker
      ↓
Cowrie Honeypot / Decoy Services
      ↓
Data Pipeline
      ↓
SQLite Database
      ↓
Tool API
      ↓
Observation Builder
      ↓
Derived Facts
      ↓
Evidence Fingerprint
      ↓
Adaptation State
      ↓
Qwen Local LLM
      ↓
Deterministic Policy
      ↓
Validator
      ↓
Controlled Action Executor
      ↓
Adaptive Deception Environment
      ↓
Observe Again
```

---

## 2. Attacker Workflow

Máy Kali được sử dụng để mô phỏng các hành vi attacker như:

- Nmap scan
- SSH brute force
- Multi-login
- SSH login
- Command execution
- File / configuration discovery
- HTTP / decoy probing
- API testing

Ví dụ:

```text
Kali
  ↓
SSH :2222
  ↓
Cowrie
  ↓
Login / Command / Session Events
```

Hoặc:

```text
Kali
  ↓
Nmap / Service Probe
  ↓
HTTP / Database / Redis Decoy
  ↓
Decoy Events
```

---

## 3. Telemetry Collection

Hệ thống thu thập telemetry từ hai nguồn chính.

### Cowrie

Cowrie ghi nhận:

```text
connection
login attempt
login success / failure
session
command
session end
```

### Decoy Services

Các service giả lập hiện tại:

```text
Cowrie SSH      : 2222
HTTP Decoy      : 8080
Database Decoy  : 3307
Redis Decoy     : 6380
```

Interaction với các service này được lưu thành `decoy_events`.

---

## 4. Data Pipeline

Data Pipeline xử lý dữ liệu từ Cowrie và các decoy service.

```text
Cowrie Logs ─────┐
                 │
                 ▼
            Data Pipeline
                 │
                 ▼
               SQLite
                 ▲
                 │
Decoy Events ────┘
```

Các bảng chính:

```text
sessions
events
commands
login_attempts
deception_events
decoy_events
security_events
monitoring_state
```

Data Pipeline chuẩn hóa telemetry trước khi Agent sử dụng.

---

## 5. Tool API

AI Agent không đọc SQLite trực tiếp.

Luồng truy cập:

```text
SQLite
   ↓
Tool API
   ↓
AI Agent
```

Tool API cung cấp:

### Read Operations

- Session information
- Recent commands
- Recent events
- Login attempts
- Brute-force status
- Decoy events
- Monitoring state
- Deception history

### Environment-Changing Actions

```text
increase_monitoring
update_artifact
```

Ngoài ra Agent có decision:

```text
observe_only
```

Decision này không thay đổi môi trường.

---

## 6. Observation Builder

Mỗi Agent cycle bắt đầu bằng việc lấy dữ liệu qua Tool API.

Observation gồm:

```text
source_ip
monitoring
collection_mode
collection_limits
bruteforce
sessions
latest_root_session_activity
decoy_activity
derived_facts
evidence_fingerprint
adaptation_state
```

---

## 7. Monitoring Mode

Hệ thống có hai mức monitoring:

```text
normal
enhanced
```

### Normal

Agent thu thập ít telemetry hơn.

### Enhanced

Agent tăng giới hạn thu thập:

```text
sessions
commands
events
decoy_events
```

Luồng:

```text
normal
  ↓
strong malicious evidence
  ↓
increase_monitoring
  ↓
enhanced
```

---

## 8. Derived Facts

Python tạo deterministic facts từ telemetry trước khi gửi dữ liệu cho LLM.

Ví dụ:

```text
37 failed SSH attempts
        ↓
bruteforce_detected = true
```

```text
successful root login
        ↓
successful_root_login = true
```

```text
Nmap Scripting Engine traffic
        ↓
nmap_http_probe_detected = true
```

```text
cat /etc/mysql/my.cnf
        ↓
attacker_commands_observed = true
```

Derived facts hiện gồm:

```text
bruteforce_detected
failed_ssh_attempts
successful_root_login
successful_root_login_session
nmap_http_probe_detected
nmap_http_probe_port
attacker_commands_observed
attacker_command_count
recent_attacker_commands
```

---

## 9. Evidence Fingerprint

`derived_facts` được chuẩn hóa và hash thành evidence fingerprint.

```text
Derived Facts
     ↓
Normalize JSON
     ↓
SHA-256
     ↓
Evidence Fingerprint
```

Fingerprint dùng để phân biệt:

```text
same evidence
```

và:

```text
new evidence
```

Nếu attacker tạo hành vi mới, derived facts thay đổi và fingerprint mới được sinh.

---

## 10. Adaptation State

Agent kiểm tra deception history để xác định evidence hiện tại đã từng được xử lý hay chưa.

```text
Evidence Fingerprint
        +
Deception History
        ↓
Adaptation State
```

Kết quả:

```text
same_evidence_already_adapted = true / false
```

Nếu cùng fingerprint đã từng kích hoạt deception adaptation:

```text
same_evidence_already_adapted = true
```

Nếu đây là evidence mới:

```text
same_evidence_already_adapted = false
```

---

## 11. Qwen Analysis

Observation được gửi tới Qwen Local LLM thông qua Ollama.

Qwen chịu trách nhiệm:

- Behavior analysis
- Risk assessment
- Evidence interpretation
- Strategy recommendation
- Artifact selection

Qwen trả về structured decision.

Ví dụ:

```json
{
  "risk_level": "high",
  "behavior": "database discovery",
  "evidence": [
    "mysql-related attacker commands observed"
  ],
  "recommended_action": "update_artifact",
  "action_params": {
    "artifact_name": "db_config"
  }
}
```

LLM không trực tiếp thực thi action.

---

## 12. Deterministic Policy

Sau khi Qwen trả proposal, Python kiểm tra monitoring state và adaptation state.

Logic chính:

```text
NORMAL MONITORING
       │
       │ strong malicious evidence
       ▼
INCREASE MONITORING
       │
       ▼
ENHANCED MONITORING
```

Khi monitoring đang enhanced:

```text
ENHANCED MONITORING
       │
       ├── same evidence already adapted
       │          ↓
       │     OBSERVE ONLY
       │
       └── new evidence
                  ↓
            QWEN ANALYSIS
```

Policy có thể override đề xuất của Qwen.

Ví dụ:

```text
Qwen:
update_artifact

Adaptation State:
same_evidence_already_adapted = true

Final Decision:
observe_only
```

---

## 13. Validator

Decision sau policy phải qua validator.

Validator kiểm tra:

```text
allowed risk level
allowed action
evidence format
parameter shape
artifact whitelist
monitoring state
action compatibility
```

Allowed decisions:

```text
observe_only
increase_monitoring
update_artifact
```

Allowed artifacts:

```text
backup_credentials
db_config
cloud_keys
```

---

## 14. Controlled Action Executor

Chỉ decision hợp lệ mới được thực thi.

### observe_only

```text
No environment-changing action
```

Agent tiếp tục quan sát.

### increase_monitoring

```text
normal
  ↓
enhanced
```

### update_artifact

Agent gửi tới Tool API:

```text
session_id
artifact_name
controlled content
evidence_fingerprint
```

---

## 15. Adaptive Artifact Workflow

LLM chỉ chọn loại artifact.

Các artifact được whitelist:

```text
backup_credentials
db_config
cloud_keys
```

Artifact selection guidance:

```text
Database discovery
→ prefer db_config
```

```text
Cloud / AWS credential discovery
→ prefer cloud_keys
```

```text
Credential / backup discovery
→ prefer backup_credentials
```

Nội dung deception artifact được Python tạo từ controlled template.

```text
Qwen
 ↓
artifact_name
 ↓
Python Template Generator
 ↓
Fake Deception Content
 ↓
Tool API
 ↓
Adaptive Artifact
```

---

## 16. Duplicate Protection

Hệ thống có hai lớp chống duplicate.

### Agent Layer

```text
enhanced monitoring
+
same_evidence_already_adapted = true
↓
observe_only
```

### Tool API Layer

Tool API kiểm tra:

```text
session_id
artifact_name
evidence_fingerprint
```

Nếu cùng action đã tồn tại:

```text
status = already_applied
```

và không ghi thêm deception event trùng.

---

## 17. Main Adaptive Scenarios

### Scenario 1

```text
Normal monitoring
+
strong malicious evidence
↓
increase_monitoring
```

### Scenario 2

```text
Enhanced monitoring
+
same evidence already adapted
↓
observe_only
```

### Scenario 3

```text
Enhanced monitoring
+
new evidence
↓
Qwen analysis
↓
observe_only hoặc update_artifact
```

Trong database discovery scenario đã kiểm thử:

```text
cat /etc/mysql/my.cnf
find / -iname "*mysql*"
        ↓
new evidence fingerprint
        ↓
Qwen analysis
        ↓
update_artifact
        ↓
db_config
```

---

## 18. Full Workflow

```text
ATTACKER
   ↓
Kali
   ↓
Cowrie / Decoy Services
   ↓
Telemetry
   ↓
Data Pipeline
   ↓
SQLite
   ↓
Tool API
   ↓
Observation Builder
   ↓
Derived Facts
   ↓
Evidence Fingerprint
   ↓
Adaptation State
   ↓
Qwen Local LLM
   ↓
Structured Proposal
   ↓
Deterministic Policy
   ↓
Validator
   ↓
Controlled Action Executor
   ↓
Tool API
   ↓
Monitoring / Deception Environment Updated
   ↓
New Attacker Interaction
   ↓
OBSERVE AGAIN
```

---

## 19. State Transition

```text
              ┌─────────────────────┐
              │  NORMAL MONITORING  │
              └──────────┬──────────┘
                         │
               strong malicious evidence
                         │
                         ▼
              ┌─────────────────────┐
              │ INCREASE MONITORING │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ ENHANCED MONITORING │
              └──────────┬──────────┘
                         │
              ┌──────────┴───────────┐
              │                      │
      Same evidence             New evidence
      already adapted                │
              │                      ▼
              ▼                QWEN ANALYSIS
     ┌────────────────┐              │
     │  OBSERVE ONLY  │       ┌──────┴──────┐
     └────────────────┘       │             │
                              ▼             ▼
                       OBSERVE ONLY   UPDATE ARTIFACT
                                           │
                                           ▼
                                  ENVIRONMENT ADAPTS
                                           │
                                           ▼
                                      OBSERVE AGAIN
```

---

## 20. Design Principle

Hệ thống không sử dụng:

```text
LLM → unrestricted command execution
```

Mà sử dụng:

```text
LLM
 ↓
Structured Recommendation
 ↓
Deterministic Policy
 ↓
Validation
 ↓
Whitelisted Action
 ↓
Controlled Environment Change
```

Thiết kế này kết hợp:

```text
LLM flexibility
+
deterministic control
+
evidence-aware adaptation
+
restricted action space
+
observable state transitions
```

Mục tiêu là xây dựng AI Agent hỗ trợ Adaptive Cyber Deception nhưng vẫn đảm bảo tính kiểm soát, khả năng giải thích và khả năng kiểm thử trong môi trường lab.
