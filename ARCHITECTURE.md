# System Architecture

## 1. Overview

Hệ thống được thiết kế theo kiến trúc Hybrid AI Agent cho Adaptive Cyber Deception.

Các thành phần chính:

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
Hybrid AI Agent
      ↓
Adaptive Deception Environment
```

---

## 2. Main Components

### Kali Attacker

Máy Kali được sử dụng để mô phỏng hành vi attacker:

- Nmap scan
- Brute force
- Multi-login
- SSH login
- Command execution
- Decoy/API probing

---

### Cowrie Honeypot

Cowrie cung cấp môi trường SSH honeypot và thu thập:

- Connection
- Login attempts
- Successful login
- Session
- Commands
- Session termination

Luồng:

```text
Kali
  ↓
SSH :2222
  ↓
Cowrie
  ↓
Log
```

---

### Decoy Services

Các dịch vụ giả lập được triển khai để thu thập reconnaissance và service probing.

```text
HTTP Decoy      : 8080
Database Decoy  : 3307
Redis Decoy     : 6380
Cowrie SSH      : 2222
```

Các interaction với decoy được ghi thành `decoy_events`.

---

## 3. Data Pipeline

Data Pipeline xử lý dữ liệu từ Cowrie và các decoy service.

```text
Cowrie Logs ──────┐
                  │
                  ▼
             Data Pipeline
                  │
                  ▼
                SQLite
                  ▲
                  │
Decoy Events ─────┘
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

## 4. Tool API

Tool API là lớp trung gian giữa database và AI Agent.

AI Agent không truy cập trực tiếp SQLite.

```text
SQLite
   ↓
Tool API
   ↓
AI Agent
```

### Read Operations

Agent dùng Tool API để lấy:

- Session information
- Command history
- Login attempts
- Brute-force state
- Decoy events
- Monitoring state
- Deception history

### Action Operations

Agent chỉ được phép thực hiện các action đã whitelist:

```text
observe_only
increase_monitoring
update_artifact
```

---

## 5. Hybrid AI Agent

Hybrid AI Agent gồm hai thành phần chính.

### LLM Reasoning Layer

Qwen Local LLM chịu trách nhiệm:

- Behavior analysis
- Risk assessment
- Evidence selection
- Strategy recommendation
- Artifact selection

### Deterministic Control Layer

Python chịu trách nhiệm:

- Observation building
- Derived facts
- Evidence fingerprint
- Adaptation state
- Policy enforcement
- Schema validation
- Safety validation
- Action execution

Kiến trúc:

```text
Telemetry
   ↓
Observation Builder
   ↓
Derived Facts
   ↓
Evidence Fingerprint
   ↓
Adaptation State
   ↓
Qwen
   ↓
Structured Proposal
   ↓
Policy
   ↓
Validator
   ↓
Action Executor
```

---

## 6. Observation Builder

Agent thu thập dữ liệu từ Tool API và xây dựng observation.

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

## 7. Derived Facts

Một số fact được Python xác định trước khi gửi dữ liệu cho LLM.

Ví dụ:

```text
failed SSH attempts
        ↓
bruteforce_detected
```

```text
root login success
        ↓
successful_root_login
```

```text
Nmap Scripting Engine traffic
        ↓
nmap_http_probe_detected
```

```text
SSH commands
        ↓
attacker_commands_observed
```

Điều này giúp giảm phụ thuộc vào suy luận tự do của LLM.

---

## 8. Evidence Fingerprint

Derived facts được chuẩn hóa và hash thành fingerprint.

```text
Derived Facts
     ↓
Normalize
     ↓
SHA-256
     ↓
Evidence Fingerprint
```

Fingerprint được dùng để xác định evidence hiện tại là:

```text
same evidence
```

hay:

```text
new evidence
```

---

## 9. Adaptation State

Agent kiểm tra lịch sử deception để xác định evidence hiện tại đã từng được xử lý chưa.

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

---

## 10. Decision Layer

LLM trả về structured decision.

Ví dụ:

```json
{
  "risk_level": "high",
  "behavior": "database discovery",
  "evidence": [
    "mysql-related commands observed"
  ],
  "recommended_action": "update_artifact",
  "action_params": {
    "artifact_name": "db_config"
  }
}
```

Decision này chưa được thực thi trực tiếp.

Nó phải đi qua:

```text
LLM Proposal
    ↓
Policy Layer
    ↓
Validator
    ↓
Action Executor
```

---

## 11. State Transition

Logic adaptive chính:

```text
NORMAL MONITORING
       │
       │ malicious evidence
       ▼
INCREASE MONITORING
       │
       ▼
ENHANCED MONITORING
       │
       ├── same evidence already adapted
       │          ↓
       │     OBSERVE ONLY
       │
       └── new evidence
                  ↓
            UPDATE ARTIFACT
                  ↓
          ENVIRONMENT ADAPTS
```

---

## 12. Adaptive Artifacts

Các deception artifact hiện được whitelist:

```text
backup_credentials
db_config
cloud_keys
```

Mapping behavior:

```text
Database discovery
→ db_config
```

```text
Cloud credential discovery
→ cloud_keys
```

```text
Credential / backup discovery
→ backup_credentials
```

LLM chỉ chọn `artifact_name`.

Nội dung artifact do Python tạo từ controlled template.

---

## 13. Defense-in-Depth

Hệ thống có nhiều lớp kiểm soát.

### LLM Constraint

Output được ép theo structured schema.

### Policy Layer

Policy có thể override quyết định của LLM.

### Validator

Kiểm tra:

- allowed action
- allowed artifact
- required evidence
- monitoring state
- parameter shape

### Tool API Gate

Tool API kiểm tra lại action và evidence fingerprint.

### Duplicate Protection

Cùng một evidence state không được liên tục kích hoạt cùng deception action.

---

## 14. Final Architecture

```text
┌──────────────────────┐
│    Kali Attacker     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Cowrie / Decoy Layer │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│    Data Pipeline     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│       SQLite         │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│      Tool API        │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Observation Builder  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│    Derived Facts     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Evidence Fingerprint │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Adaptation State     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   Qwen Local LLM     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Policy + Validator   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   Action Executor    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Adaptive Deception   │
│     Environment      │
└──────────┬───────────┘
           │
           └──────────────→ Observe Again
```

---

## 15. Design Goal

Mục tiêu kiến trúc là kết hợp:

```text
LLM flexibility
+
deterministic control
+
restricted actions
+
observable state transition
```

để xây dựng một AI Agent có khả năng hỗ trợ Adaptive Cyber Deception nhưng vẫn đảm bảo tính kiểm soát và khả năng giải thích trong môi trường lab.
