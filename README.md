# Adaptive Cyber Deception with Hybrid AI Agent

Đồ án xây dựng hệ thống **AI Agent hỗ trợ Adaptive Cyber Deception dựa trên Honeypot**, sử dụng Cowrie Honeypot, các decoy service, Tool API và Local LLM.

## Project Overview

Kiến trúc mục tiêu đặt **AI Deception Agent / Decision Gateway ở phía trước Honeypot và các decoy service**.

AI Agent sử dụng trạng thái hiện tại và feedback từ các chu kỳ trước để quyết định deception strategy trước khi attacker tiếp tục tương tác với môi trường.

Target flow:

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
      └──────────────→ AI Agent
```

Adaptive loop:

```text
Observe → Analyze → Decide → Route/Act → Adapt → Observe Again
```

---

## Core Architecture

```text
Kali Attacker
      ↓
AI Deception Agent / Decision Gateway
      ↓
Honeypot / Decoy Environment
      ↓
Data Pipeline
      ↓
SQLite Database
      ↓
Tool API
      ↓
Feedback to AI Agent
```

Bên trong Hybrid AI Agent:

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

## Hybrid AI Agent

AI Agent được thiết kế theo mô hình Hybrid.

### LLM Reasoning Layer

Qwen Local LLM chịu trách nhiệm:

- Behavior analysis
- Risk assessment
- Evidence interpretation
- Strategy recommendation
- Artifact selection

### Deterministic Control Layer

Python chịu trách nhiệm:

- Observation building
- Derived facts
- Evidence fingerprint
- Adaptation state
- Policy enforcement
- Validation
- Duplicate protection
- Controlled execution

LLM không trực tiếp thực thi shell command hoặc thay đổi hệ thống.

---

## Adaptive Decisions

Decision space hiện tại:

```text
observe_only
increase_monitoring
update_artifact
```

Trong đó:

- `observe_only`: không thay đổi môi trường.
- `increase_monitoring`: chuyển monitoring từ normal sang enhanced.
- `update_artifact`: cập nhật deception artifact được whitelist.

Target inline gateway có thể mở rộng thêm các action như:

```text
route_to_decoy
select_deception_profile
redirect_service
```

Các action này thuộc hướng phát triển tiếp theo và chưa được xem là hoàn thành trong prototype hiện tại.

---

## Adaptive Logic

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
```

New evidence không bắt buộc phải dẫn tới `update_artifact`.

Qwen phân tích evidence mới và có thể chọn `observe_only` hoặc `update_artifact`.

---

## Honeypot / Decoy Environment

Các service hiện tại:

```text
Cowrie SSH      : 2222
HTTP Decoy      : 8080
Database Decoy  : 3307
Redis Decoy     : 6380
```

Các interaction được ghi nhận thành telemetry và đưa vào feedback loop.

---

## Evidence-Aware Adaptation

Python tạo derived facts từ telemetry.

Ví dụ:

```text
failed SSH attempts
→ bruteforce_detected
```

```text
successful root login
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

Derived facts được hash thành:

```text
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

Agent kết hợp fingerprint với deception history để tạo:

```text
same_evidence_already_adapted = true / false
```

---

## Adaptive Artifacts

Các deception artifact hiện được whitelist:

```text
backup_credentials
db_config
cloud_keys
```

Guidance:

```text
Database-related behavior
→ prefer db_config
```

```text
Cloud / AWS behavior
→ prefer cloud_keys
```

```text
Credential / backup behavior
→ prefer backup_credentials
```

LLM chỉ chọn `artifact_name`.

Nội dung artifact được Python tạo từ controlled template.

---

## Technologies

- Python
- Cowrie Honeypot
- Docker / Docker Compose
- FastAPI
- SQLite
- Ollama
- Qwen3 1.7B
- Kali Linux
- Ubuntu Linux

---

## Documentation

- [System & AI Agent Workflow](WORKFLOW.md)
- [System Architecture](ARCHITECTURE.md)
- [Demo Scenarios](DEMO.md)

---

## Team Members

- Lê Duy
- Lê Phi Hoàng
- Phạm Nhật Huy

## Project Structure

```text
cyper_deception_agent/
├── agent/
├── agent_integration/
├── cowrie/
├── data_pipeline/
├── decoy_services/
├── tool_api/
├── docker-compose.yml
├── TOOL_API.md
├── WORKFLOW.md
├── ARCHITECTURE.md
├── DEMO.md
├── .env.example
├── .gitignore
└── README.md
```

---

## Current Prototype Status

Prototype hiện tại đã triển khai thành công feedback-driven adaptive loop:

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

Các thành phần đã hoạt động:

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

---

## Verified Demo Scenarios

### Scenario 1

```text
Normal monitoring
+
strong malicious evidence
→ increase_monitoring
```

### Scenario 2

```text
Enhanced monitoring
+
same evidence already adapted
→ observe_only
```

### Scenario 3

```text
Enhanced monitoring
+
new database-related evidence
→ Qwen analysis
→ update_artifact
→ db_config
```

---

## Target Architecture

Mục tiêu tiếp theo là đưa AI Agent thành inline Decision Gateway:

```text
Attacker
   ↓
AI Decision Gateway
   ↓
Honeypot / Decoy Environment
```

Khi đó mọi attacker interaction sẽ được AI control layer phân tích và điều phối trước khi đi vào deception environment.

Các capability mục tiêu:

- Inline traffic interception
- Dynamic decoy routing
- Deception profile selection
- Service redirection
- Context-aware deception strategy
- Continuous feedback adaptation

---

## Safety Design

Hệ thống không sử dụng:

```text
LLM
 ↓
Unrestricted command execution
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

Điều này giúp giữ AI Agent trong phạm vi:

- kiểm soát được
- giải thích được
- kiểm thử được
- tái hiện được
- giới hạn action rõ ràng

---

## Design Goal

Mục tiêu cuối cùng của hệ thống là kết hợp:

```text
AI-driven deception control
+
Honeypot interaction
+
telemetry feedback
+
evidence-aware adaptation
+
restricted action space
```

để xây dựng một nền tảng Adaptive Cyber Deception có khả năng thay đổi deception strategy theo attacker behavior qua từng chu kỳ.
