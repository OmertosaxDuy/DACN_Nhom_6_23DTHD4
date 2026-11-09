# System Architecture

## 1. Overview

Kiến trúc mục tiêu của hệ thống là **AI-controlled Adaptive Cyber Deception**, trong đó AI Deception Agent nằm giữa attacker và Honeypot / Decoy Environment.

```text
Kali Attacker
      ↓
AI Deception Agent / Decision Gateway
      ↓
Honeypot / Decoy Environment
      ↓
Telemetry
      ↓
Data Pipeline
      ↓
SQLite
      ↓
Tool API
      ↓
Feedback
      └──────────────→ AI Agent
```

AI Agent vừa đóng vai trò:

- **Decision Gateway** trước deception environment.
- **Adaptive Control Plane** nhận feedback để thay đổi strategy ở cycle tiếp theo.

---

## 2. Architectural Layers

Hệ thống được chia thành bốn lớp chính.

```text
1. Attacker Layer
2. AI Deception Control Layer
3. Deception Data Plane
4. Telemetry & State Layer
```

---

## 3. Attacker Layer

Kali Linux đóng vai trò attacker.

Các hành vi kiểm thử:

- Nmap scan
- Brute force
- Multi-login
- SSH login
- Command execution
- File discovery
- Configuration discovery
- HTTP probing
- Database probing
- API testing

Attacker không phải thành phần ra quyết định trong hệ thống mà là nguồn tạo interaction và evidence.

---

## 4. AI Deception Control Layer

Đây là lớp trung tâm của kiến trúc.

```text
Kali Attacker
      ↓
AI Deception Agent
      ↓
Honeypot / Decoy Environment
```

AI Agent có nhiệm vụ:

- Observe attacker state
- Analyze historical telemetry
- Assess risk
- Determine deception strategy
- Control monitoring state
- Select deception artifact
- In future: route attacker to appropriate decoy

---

## 5. Hybrid AI Agent

AI Agent sử dụng kiến trúc Hybrid.

```text
LLM Reasoning
+
Deterministic Control
```

Pipeline:

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

---

## 6. Observation Builder

Observation được xây dựng từ Tool API.

Các trường chính:

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

Observation cung cấp state cho Agent trước khi ra quyết định.

---

## 7. Derived Facts

Python tạo deterministic facts từ telemetry.

Ví dụ:

```text
failed SSH attempts
→ bruteforce_detected
```

```text
root login success
→ successful_root_login
```

```text
Nmap HTTP probe
→ nmap_http_probe_detected
```

```text
MySQL-related commands
→ attacker_commands_observed
```

Mục đích là giảm hallucination và tránh bắt LLM tự suy luận các fact có thể xác định trực tiếp.

---

## 8. Evidence Fingerprint

Fingerprint được tạo từ `derived_facts`.

```text
Derived Facts
     ↓
Normalize JSON
     ↓
SHA-256
     ↓
Evidence Fingerprint
```

Nó đại diện cho evidence state hiện tại.

```text
same fingerprint
→ same evidence state
```

```text
different fingerprint
→ changed evidence state
```

---

## 9. Adaptation State

Agent kiểm tra deception history.

```text
Fingerprint
    +
Deception History
    ↓
Adaptation State
```

Kết quả:

```text
same_evidence_already_adapted
```

Giá trị này giúp tránh repeated adaptation.

---

## 10. Qwen Local LLM

Qwen chịu trách nhiệm:

- Behavior analysis
- Risk assessment
- Evidence interpretation
- Strategy recommendation
- Artifact selection

Qwen chỉ tạo structured proposal.

Qwen không trực tiếp:

- chạy shell
- truy cập SQLite
- sửa host
- sửa Docker
- thay đổi network
- tạo arbitrary action

---

## 11. Deterministic Policy

Policy layer xử lý các state transition quan trọng.

```text
Normal + strong malicious evidence
→ increase_monitoring
```

```text
Enhanced + same evidence already adapted
→ observe_only
```

```text
Enhanced + new evidence
→ allow Qwen analysis
```

Policy có thể override LLM output.

---

## 12. Validator

Validator kiểm tra:

- allowed risk
- allowed action
- evidence format
- parameter shape
- artifact whitelist
- monitoring state
- action compatibility

Allowed decisions:

```text
observe_only
increase_monitoring
update_artifact
```

---

## 13. Action Executor

Action Executor chỉ thực thi decision hợp lệ.

```text
observe_only
→ no environment change
```

```text
increase_monitoring
→ normal → enhanced
```

```text
update_artifact
→ controlled deception artifact update
```

---

## 14. Decision Gateway Role

Trong target architecture, AI Agent nằm inline trước deception environment.

```text
Incoming attacker interaction
        ↓
AI Decision Gateway
        ↓
Current state + history
        ↓
Decision
        ↓
Deception environment selection/configuration
        ↓
Attacker interaction continues
```

Các capability tương lai có thể bao gồm:

```text
route_to_decoy
select_deception_profile
redirect_service
modify_decoy_exposure
```

Những capability này chưa được coi là hoàn thành nếu chưa có routing/gateway implementation.

---

## 15. Deception Data Plane

Deception Environment gồm:

```text
Cowrie SSH      : 2222
HTTP Decoy      : 8080
Database Decoy  : 3307
Redis Decoy     : 6380
```

Đây là nơi attacker trực tiếp tương tác.

---

## 16. Cowrie Honeypot

Cowrie thu thập:

- connection
- login attempts
- authentication result
- session
- command
- session end

Luồng:

```text
AI Gateway
    ↓
Cowrie
    ↓
Attacker interaction
    ↓
Telemetry
```

---

## 17. Decoy Services

Các decoy service bổ sung telemetry ngoài SSH:

```text
HTTP
Database
Redis
```

Chúng hỗ trợ phát hiện reconnaissance và service probing.

---

## 18. Telemetry & State Layer

Sau mỗi interaction:

```text
Honeypot / Decoy
      ↓
Telemetry
      ↓
Data Pipeline
      ↓
SQLite
      ↓
Tool API
      ↓
AI Feedback
```

Feedback này cập nhật state cho decision cycle tiếp theo.

---

## 19. Data Pipeline

Data Pipeline:

- Parse logs
- Normalize events
- Extract structured fields
- Store persistent state

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

## 20. Tool API

Tool API cung cấp interface giữa state và Agent.

### Read Operations

- sessions
- recent commands
- events
- login attempts
- brute force state
- decoy events
- monitoring state
- deception history

### Environment Actions

```text
increase_monitoring
update_artifact
```

Trong future inline architecture, Tool API hoặc gateway control API có thể bổ sung routing action.

---

## 21. Adaptive Artifacts

Các artifact hiện tại:

```text
backup_credentials
db_config
cloud_keys
```

Guidance:

```text
Database behavior
→ db_config
```

```text
Cloud behavior
→ cloud_keys
```

```text
Credential / backup behavior
→ backup_credentials
```

Nội dung artifact được Python tạo từ controlled template.

---

## 22. Monitoring State

Hai state:

```text
normal
enhanced
```

Normal:

```text
less telemetry
```

Enhanced:

```text
more sessions
more commands
more events
more decoy events
```

---

## 23. Decision State Transition

```text
NORMAL MONITORING
       │
       │ strong malicious evidence
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
            QWEN ANALYSIS
                  ↓
        ┌─────────┴─────────┐
        │                   │
        ▼                   ▼
  OBSERVE ONLY       UPDATE ARTIFACT
                            │
                            ▼
                    ENVIRONMENT ADAPTS
                            │
                            ▼
                      NEXT INTERACTION
```

---

## 24. Feedback Loop

Adaptive behavior không kết thúc sau một action.

```text
AI Decision
    ↓
Deception Environment
    ↓
Attacker Interaction
    ↓
Telemetry
    ↓
Persistent State
    ↓
AI Feedback
    ↓
Next Decision
```

Đây là vòng lặp:

```text
Observe → Analyze → Decide → Act → Adapt → Observe Again
```

---

## 25. Target Architecture

```text
┌─────────────────────┐
│    Kali Attacker    │
└──────────┬──────────┘
           │
           ▼
┌──────────────────────────────┐
│ AI Deception Agent / Gateway│
│                              │
│ Observation Builder          │
│ Derived Facts                │
│ Evidence Fingerprint         │
│ Adaptation State             │
│ Qwen Local LLM               │
│ Policy                       │
│ Validator                    │
│ Action Executor              │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ Honeypot / Decoy Environment│
│                              │
│ Cowrie SSH                   │
│ HTTP Decoy                   │
│ Database Decoy               │
│ Redis Decoy                  │
└──────────────┬───────────────┘
               │
            Telemetry
               │
               ▼
┌─────────────────────┐
│    Data Pipeline    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│       SQLite        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│      Tool API       │
└──────────┬──────────┘
           │
           └────────────→ AI Agent
```

---

## 26. Current Implementation Status

### Implemented

- Cowrie telemetry
- Decoy telemetry
- Data Pipeline
- SQLite
- Tool API
- Observation Builder
- Derived Facts
- Evidence Fingerprint
- Adaptation State
- Qwen Local LLM
- Deterministic Policy
- Validator
- Action Executor
- Increase Monitoring
- Update Artifact
- Duplicate Protection

### Target / Next Step

```text
Attacker
   ↓
Inline AI Decision Gateway
   ↓
Dynamic deception routing
   ↓
Honeypot / Decoy selection
```

Hiện prototype đã chứng minh adaptive feedback loop.

Bước tiếp theo là chuyển AI control layer thành inline gateway để attacker interaction được điều phối trước khi đi vào deception environment.
