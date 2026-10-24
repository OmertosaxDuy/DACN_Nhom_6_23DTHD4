# System & AI Agent Workflow

## 1. Workflow tổng quan

Hệ thống hướng tới kiến trúc **AI-driven Adaptive Cyber Deception**, trong đó attacker đi qua lớp AI Deception Agent trước khi được điều phối tới Honeypot hoặc các decoy service.

Luồng mục tiêu:

```text
Kali Attacker
      ↓
AI Deception Agent / Decision Gateway
      ↓
Honeypot / Decoy Environment
      ↓
Telemetry / Logs
      ↓
Data Pipeline
      ↓
SQLite Database
      ↓
Tool API
      ↓
Observation / Feedback
      └──────────────→ AI Deception Agent
```

Vòng lặp chính:

```text
Observe → Analyze → Decide → Route/Act → Adapt → Observe Again
```

---

## 2. Attacker Workflow

Kali Linux được sử dụng để mô phỏng attacker.

Các hành vi kiểm thử gồm:

- Nmap scan
- SSH brute force
- Multi-login
- SSH login
- Command execution
- File / configuration discovery
- HTTP probing
- Database probing
- Redis probing
- API testing

Luồng mục tiêu:

```text
Kali Attacker
      ↓
AI Decision Gateway
      ↓
Deception Strategy
      ↓
Cowrie / HTTP Decoy / DB Decoy / Redis Decoy
```

AI Agent đóng vai trò control layer để lựa chọn hoặc điều chỉnh deception strategy trước và trong quá trình attacker tương tác với môi trường.

---

## 3. AI Deception Agent

AI Agent gồm hai phần chính:

```text
LLM Reasoning
+
Deterministic Control
```

Pipeline nội bộ:

```text
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
Action Executor
```

Qwen chịu trách nhiệm:

- Behavior analysis
- Risk assessment
- Evidence interpretation
- Strategy recommendation
- Artifact selection

Python deterministic layer chịu trách nhiệm:

- Observation building
- Derived facts
- Evidence fingerprint
- Adaptation state
- Policy enforcement
- Validation
- Duplicate protection
- Controlled execution

---

## 4. Decision Gateway

Trong kiến trúc mục tiêu, AI Agent nằm trước Honeypot / Decoy Environment.

Luồng:

```text
Attacker Request
      ↓
AI observes current state
      ↓
AI analyzes attacker context
      ↓
Decision / deception strategy
      ↓
Route or configure deception environment
      ↓
Attacker interaction
```

Các decision hiện tại:

```text
observe_only
increase_monitoring
update_artifact
```

Trong hướng phát triển inline gateway có thể bổ sung:

```text
route_to_decoy
select_deception_profile
redirect_service
```

Các action mới chỉ được triển khai khi có validation và routing layer tương ứng.

---

## 5. Honeypot / Decoy Environment

Môi trường deception hiện gồm:

```text
Cowrie SSH      : 2222
HTTP Decoy      : 8080
Database Decoy  : 3307
Redis Decoy     : 6380
```

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

Các decoy service ghi nhận:

```text
service probing
protocol interaction
HTTP request
database probe
Redis interaction
payload preview
```

---

## 6. Telemetry Feedback

Sau khi attacker tương tác với Honeypot hoặc Decoy Environment:

```text
Honeypot / Decoy
      ↓
Telemetry / Logs
      ↓
Data Pipeline
      ↓
SQLite
```

Telemetry trở thành feedback cho Agent ở cycle tiếp theo.

---

## 7. Data Pipeline

Data Pipeline chịu trách nhiệm:

- Parse logs
- Normalize data
- Extract structured events
- Store data
- Maintain attacker interaction history

Luồng:

```text
Cowrie Logs ───────┐
                   │
                   ▼
              Data Pipeline
                   │
                   ▼
                 SQLite
                   ▲
                   │
Decoy Events ──────┘
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

---

## 8. Tool API

Tool API là lớp trung gian giữa persistent state, AI Agent và các environment-changing action.

```text
SQLite
   ↓
Tool API
   ↕
AI Agent
```

Agent không truy cập trực tiếp SQLite.

### Read Operations

Tool API cung cấp:

- Session information
- Recent commands
- Recent events
- Login attempts
- Brute-force state
- Decoy events
- Monitoring state
- Deception history

### Environment-Changing Actions

Hiện tại:

```text
increase_monitoring
update_artifact
```

`observe_only` là decision không làm thay đổi môi trường.

---

## 9. Observation Builder

Agent xây dựng observation từ Tool API.

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

Observation là context chính để AI Agent ra quyết định.

---

## 10. Derived Facts

Python tạo các fact deterministic từ telemetry.

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

Các fact hiện tại gồm:

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

## 11. Evidence Fingerprint

`derived_facts` được chuẩn hóa và hash bằng SHA-256.

```text
Derived Facts
     ↓
Normalize JSON
     ↓
SHA-256
     ↓
Evidence Fingerprint
```

Fingerprint giúp phân biệt:

```text
same evidence
```

và:

```text
new evidence
```

---

## 12. Adaptation State

Agent kết hợp evidence fingerprint với deception history.

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

Nếu evidence đã được xử lý:

```text
true
```

Nếu attacker tạo trạng thái evidence mới:

```text
false
```

---

## 13. Qwen Analysis

Observation được gửi tới Qwen Local LLM thông qua Ollama.

Qwen trả về structured proposal.

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

Qwen không trực tiếp thực thi action.

---

## 14. Deterministic Policy

Sau LLM proposal, Python kiểm tra monitoring state và adaptation state.

Logic hiện tại:

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

Qwen có thể đề xuất:

```text
observe_only
```

hoặc:

```text
update_artifact
```

---

## 15. Validator

Decision phải qua validator trước khi thực thi.

Validator kiểm tra:

- Allowed action
- Allowed artifact
- Required evidence
- Parameter shape
- Monitoring state
- Action compatibility

Allowed decision space:

```text
observe_only
increase_monitoring
update_artifact
```

---

## 16. Action Executor

### Observe Only

```text
observe_only
```

Không thay đổi environment.

### Increase Monitoring

```text
normal
  ↓
enhanced
```

Enhanced monitoring thu thập nhiều telemetry hơn.

### Update Artifact

Agent gửi:

```text
session_id
artifact_name
controlled content
evidence_fingerprint
```

đến Tool API.

---

## 17. Adaptive Artifacts

Các artifact hiện được whitelist:

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
Cloud / AWS discovery
→ prefer cloud_keys
```

```text
Credential / backup discovery
→ prefer backup_credentials
```

Qwen chỉ chọn artifact.

Nội dung deception được Python tạo từ controlled template.

---

## 18. Duplicate Protection

Agent layer:

```text
enhanced
+
same_evidence_already_adapted = true
↓
observe_only
```

Tool API layer kiểm tra:

```text
session_id
artifact_name
evidence_fingerprint
```

Nếu đã tồn tại:

```text
already_applied
```

---

## 19. Full Adaptive Workflow

```text
KALI ATTACKER
      ↓
AI DECEPTION AGENT / DECISION GATEWAY
      ↓
DECEPTION STRATEGY
      ↓
HONEYPOT / DECOY ENVIRONMENT
      ↓
ATTACKER INTERACTION
      ↓
TELEMETRY / LOGS
      ↓
DATA PIPELINE
      ↓
SQLITE
      ↓
TOOL API
      ↓
OBSERVATION / FEEDBACK
      ↓
AI AGENT
      ↓
NEXT DECEPTION DECISION
      ↓
HONEYPOT / DECOY ENVIRONMENT
      ↓
OBSERVE AGAIN
```

---

## 20. Current Prototype vs Target Architecture

### Current Prototype

Phiên bản hiện tại đã triển khai:

```text
Attacker
   ↓
Cowrie / Decoy
   ↓
Telemetry
   ↓
AI Agent
   ↓
Adaptive Action
   ↓
Environment Updated
```

Đã hoạt động:

- observation
- derived facts
- evidence fingerprint
- adaptation state
- Qwen reasoning
- deterministic policy
- validator
- increase monitoring
- update artifact
- duplicate protection

### Target Architecture

Mục tiêu tiếp theo:

```text
Attacker
   ↓
AI Decision Gateway
   ↓
Honeypot / Decoy Environment
```

Tức mọi attacker interaction sẽ được AI deception control layer điều phối trước khi đi vào environment.

Đây là bước phát triển tiếp theo để chuyển prototype hiện tại thành inline adaptive deception architecture.
