# System Architecture

## 1. Overview

Hệ thống được thiết kế theo kiến trúc **Hybrid AI Agent for Adaptive Cyber Deception**.

Mục tiêu chính là kết hợp khả năng phân tích linh hoạt của Local LLM với các lớp kiểm soát deterministic để AI Agent có thể đưa ra quyết định thích ứng nhưng vẫn giữ action trong phạm vi an toàn và có thể kiểm chứng trong môi trường lab.

Kiến trúc tổng quát:

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

Vòng lặp chính của hệ thống:

```text
Observe → Analyze → Decide → Act → Adapt → Observe Again
```

---

## 2. Main Components

### 2.1 Kali Attacker

Máy Kali được sử dụng để mô phỏng attacker trong môi trường lab.

Các hành vi kiểm thử gồm:

- Nmap scan
- SSH brute force
- Multi-login
- SSH login
- Command execution
- File / configuration discovery
- HTTP / decoy probing
- API testing

Kali đóng vai trò tạo telemetry để đánh giá khả năng quan sát, phân tích và thích ứng của AI Agent.

---

### 2.2 Cowrie Honeypot

Cowrie cung cấp môi trường SSH honeypot và thu thập các sự kiện như:

- New connection
- Login attempts
- Login success / failure
- Session information
- Executed commands
- SSH client information
- Session termination

Luồng cơ bản:

```text
Kali
  ↓
SSH :2222
  ↓
Cowrie Honeypot
  ↓
Raw Events / Commands
```

Cowrie không trực tiếp ra quyết định deception. Vai trò chính của nó là tạo môi trường tương tác giả lập và cung cấp telemetry cho các thành phần phía sau.

---

### 2.3 Decoy Services

Ngoài Cowrie, hệ thống triển khai thêm các dịch vụ giả lập nhằm thu thập hành vi reconnaissance và service probing.

Các service hiện tại:

```text
Cowrie SSH      : 2222
HTTP Decoy      : 8080
Database Decoy  : 3307
Redis Decoy     : 6380
```

Interaction với các service này được lưu dưới dạng `decoy_events`.

Ví dụ:

```text
Nmap / service probe
        ↓
Decoy Service
        ↓
Payload / protocol interaction captured
        ↓
decoy_events
```

Decoy traffic được xử lý độc lập với SSH telemetry của Cowrie nhưng được tổng hợp chung ở lớp observation.

---

## 3. Data Pipeline

Data Pipeline chịu trách nhiệm thu thập, chuẩn hóa và lưu dữ liệu từ Cowrie và các decoy service.

Luồng:

```text
Cowrie Events ───────┐
                     │
                     ▼
                Data Pipeline
                     │
                     ▼
                   SQLite
                     ▲
                     │
Decoy Events ────────┘
```

Các bảng dữ liệu chính:

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

Vai trò của Data Pipeline:

- Chuyển log thô thành dữ liệu có cấu trúc
- Chuẩn hóa session và event
- Lưu command của attacker
- Lưu login attempts
- Lưu decoy interactions
- Lưu lịch sử deception action
- Lưu monitoring state

AI Agent không phân tích trực tiếp file log thô mà sử dụng dữ liệu đã được chuẩn hóa thông qua Tool API.

---

## 4. SQLite Database

SQLite đóng vai trò là persistent state của hệ thống.

Dữ liệu lưu trong database được sử dụng cho hai mục đích chính:

### Observation State

Bao gồm:

- sessions
- commands
- login attempts
- decoy events
- monitoring state

### Adaptation History

Bao gồm:

- deception events
- action history
- evidence fingerprint history

Nhờ đó Agent không chỉ biết trạng thái hiện tại mà còn có thể xác định một evidence state đã từng được xử lý hay chưa.

---

## 5. Tool API

Tool API là lớp trung gian giữa dữ liệu, Agent và môi trường deception.

```text
SQLite
   ↓
Tool API
   ↓
Hybrid AI Agent
```

AI Agent không truy cập trực tiếp SQLite để đọc hoặc thay đổi dữ liệu.

### 5.1 Read Operations

Tool API cung cấp dữ liệu phục vụ observation, bao gồm:

- Session information
- Command history
- Recent events
- Login attempts
- Brute-force state
- Decoy events
- Decoy statistics
- Monitoring state
- Deception history

Ví dụ:

```text
GET /statistics
GET /sessions/{session_id}
GET /sessions/{session_id}/commands
GET /sessions/{session_id}/events
GET /ips/{src_ip}/bruteforce
GET /decoy/recent
GET /monitoring/{src_ip}
GET /sessions/{session_id}/deception-history
```

### 5.2 Environment-Changing Actions

Các action có thể làm thay đổi trạng thái hệ thống gồm:

```text
increase_monitoring
update_artifact
```

`observe_only` là một decision của Agent nhưng không yêu cầu gọi endpoint để thay đổi môi trường.

Agent decision space:

```text
observe_only
increase_monitoring
update_artifact
```

---

## 6. Hybrid AI Agent

AI Agent được xây dựng theo mô hình hybrid, gồm hai lớp chính.

### 6.1 LLM Reasoning Layer

Qwen Local LLM chịu trách nhiệm:

- Behavior analysis
- Risk assessment
- Evidence interpretation
- Strategy recommendation
- Artifact selection

LLM không trực tiếp:

- thực thi shell command
- truy cập database
- sửa cấu hình host
- tạo arbitrary action
- thay đổi trực tiếp deception environment

LLM chỉ tạo một structured proposal.

### 6.2 Deterministic Control Layer

Python chịu trách nhiệm:

- Observation building
- Derived fact extraction
- Evidence fingerprint generation
- Adaptation state lookup
- Monitoring-aware policy
- Duplicate protection
- Schema validation
- Safety validation
- Controlled action execution

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
Deterministic Policy
   ↓
Validator
   ↓
Controlled Executor
```

---

## 7. Observation Builder

Mỗi Agent cycle bắt đầu bằng việc thu thập dữ liệu qua Tool API và xây dựng một observation có cấu trúc.

Observation hiện gồm:

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

Observation Builder giúp gom dữ liệu từ nhiều nguồn thành một context thống nhất trước khi gửi cho Qwen.

---

## 8. Adaptive Collection Mode

Hệ thống có hai mức thu thập telemetry:

```text
normal
enhanced
```

### Normal Monitoring

Agent thu thập lượng dữ liệu nhỏ hơn để giảm context và chi phí xử lý.

### Enhanced Monitoring

Agent tăng giới hạn thu thập:

```text
more recent sessions
more commands
more events
more decoy events
```

Điều này tạo ra một cơ chế thích ứng ngay từ lớp observation.

```text
normal monitoring
        ↓
strong malicious evidence
        ↓
increase_monitoring
        ↓
enhanced monitoring
```

---

## 9. Derived Facts

Một số fact được Python xác định deterministic trước khi dữ liệu được gửi cho LLM.

Ví dụ:

```text
37 failed SSH attempts
        ↓
bruteforce_detected = true
```

```text
login attempt [root/...] succeeded
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

Derived facts hiện bao gồm các trường như:

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

Mục đích là giảm phụ thuộc vào suy luận tự do của LLM đối với những fact có thể xác định trực tiếp từ telemetry.

---

## 10. Evidence Fingerprint

Evidence fingerprint được tạo từ `derived_facts`.

Luồng:

```text
Derived Facts
     ↓
Normalize JSON
     ↓
SHA-256
     ↓
Evidence Fingerprint
```

Fingerprint đại diện cho evidence state hiện tại.

Ví dụ:

```text
e264005a8359d8dd
```

Khi derived facts thay đổi do attacker tạo hành vi mới, fingerprint cũng thay đổi.

Ví dụ:

```text
Before:
attacker_commands_observed = false

After:
attacker_commands_observed = true
recent_attacker_commands = [...]
```

Kết quả:

```text
old fingerprint ≠ new fingerprint
```

Fingerprint được sử dụng để phân biệt:

```text
same evidence
```

và:

```text
new evidence
```

---

## 11. Adaptation State

Agent sử dụng evidence fingerprint kết hợp với deception history để xác định trạng thái thích ứng.

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

Nếu cùng fingerprint đã từng kích hoạt `update_artifact`:

```text
same_evidence_already_adapted = true
```

Nếu fingerprint chưa từng được xử lý:

```text
same_evidence_already_adapted = false
```

Cơ chế này giúp tránh việc lặp lại cùng một deception action cho cùng evidence state.

---

## 12. Qwen Local LLM

Observation được gửi tới Qwen thông qua Ollama.

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
  },
  "reason": "New database-related behavior was observed"
}
```

Structured output giúp giảm ambiguity và giới hạn không gian hành động của model.

Qwen hiện chỉ có thể đề xuất các action được phép.

---

## 13. Deterministic Policy Layer

LLM proposal không được thực thi trực tiếp.

Sau khi parse output, hệ thống áp dụng deterministic policy dựa trên monitoring state và adaptation state.

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

Khi hệ thống đã ở enhanced:

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

Policy layer có thể override đề xuất của Qwen.

Ví dụ:

```text
Qwen proposes:
update_artifact

but:
same_evidence_already_adapted = true

final decision:
observe_only
```

Điều này đảm bảo state transition quan trọng không phụ thuộc hoàn toàn vào model.

---

## 14. Validator

Sau policy layer, decision tiếp tục đi qua validator.

Validator kiểm tra:

- allowed risk level
- allowed action
- evidence format
- evidence count
- action parameter shape
- artifact whitelist
- monitoring state
- action compatibility

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

Decision không hợp lệ sẽ không được Action Executor thực thi.

---

## 15. Controlled Action Executor

Action Executor chỉ thực hiện decision đã qua validation.

### Observe Only

```text
observe_only
```

Kết quả:

```text
no environment-changing action
```

Agent tiếp tục chu kỳ quan sát.

### Increase Monitoring

```text
increase_monitoring
```

Tool API chuyển:

```text
normal
  ↓
enhanced
```

### Update Artifact

```text
update_artifact
```

Agent gửi:

```text
session_id
artifact_name
controlled content
evidence_fingerprint
```

tới Tool API.

---

## 16. Adaptive Deception Artifacts

Các deception artifact hiện được whitelist:

```text
backup_credentials
db_config
cloud_keys
```

Artifact selection guidance:

```text
Database-related discovery
→ prefer db_config
```

```text
Cloud / AWS credential discovery
→ prefer cloud_keys
```

```text
Credential / backup / account discovery
→ prefer backup_credentials
```

Đây là guidance cho Qwen, không phải mapping bắt buộc trong mọi tình huống.

Nếu evidence không đủ để xác định artifact phù hợp, Agent có thể chọn:

```text
observe_only
```

LLM chỉ chọn `artifact_name`.

Nội dung artifact được Python tạo từ controlled template.

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
```

---

## 17. Duplicate Protection

Hệ thống có hai lớp chống duplicate action.

### Agent Layer

Nếu:

```text
same_evidence_already_adapted = true
```

và monitoring đang enhanced:

```text
final decision = observe_only
```

### Tool API Layer

Nếu Agent vẫn gửi cùng action với:

```text
same session_id
same artifact_name
same evidence_fingerprint
```

Tool API kiểm tra deception history.

Nếu đã tồn tại:

```text
status = already_applied
```

và không ghi một deception action trùng mới.

Cơ chế này tạo defense-in-depth cho adaptation logic.

---

## 18. Defense-in-Depth

Decision pipeline:

```text
Qwen Proposal
      ↓
Structured Schema
      ↓
Deterministic Policy
      ↓
Validator
      ↓
Controlled Action Executor
      ↓
Tool API Gate
      ↓
Environment Change
```

Các lớp bảo vệ:

### Structured LLM Output

Giới hạn output của model về schema cụ thể.

### Policy Layer

Ép các state transition quan trọng.

### Validator

Kiểm tra action và parameters.

### Artifact Whitelist

Chỉ cho phép artifact đã định nghĩa trước.

### Controlled Content Generator

LLM không sinh nội dung file mồi trực tiếp.

### Tool API Validation

Tool API kiểm tra request trước khi thay đổi môi trường.

### Evidence-Aware Duplicate Gate

Ngăn action trùng với cùng evidence state.

---

## 19. Adaptive State Transition

Logic hiện tại:

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

Điểm quan trọng:

```text
new evidence
```

không đồng nghĩa với:

```text
always update_artifact
```

New evidence chỉ làm cho adaptation mới trở thành khả dụng. Qwen vẫn phân tích evidence và có thể chọn `observe_only` nếu không đủ cơ sở để thay đổi artifact.

---

## 20. Example Adaptive Scenario

Ví dụ database discovery:

```text
Kali SSH login
       ↓
cat /etc/mysql/my.cnf
       ↓
find / -iname "*mysql*"
       ↓
Cowrie records commands
       ↓
Data Pipeline
       ↓
SQLite
       ↓
Tool API
       ↓
Observation Builder
       ↓
attacker_commands_observed = true
       ↓
recent_attacker_commands updated
       ↓
new evidence fingerprint
       ↓
same_evidence_already_adapted = false
       ↓
Qwen Analysis
       ↓
update_artifact
       ↓
artifact_name = db_config
       ↓
Validator
       ↓
Action Executor
       ↓
Tool API
       ↓
db_config deception artifact updated
       ↓
Observe Again
```

---

## 21. Final Architecture

```text
┌────────────────────────┐
│     Kali Attacker      │
└────────────┬───────────┘
             │
             ▼
┌────────────────────────┐
│ Cowrie / Decoy Services│
└────────────┬───────────┘
             │
             ▼
┌────────────────────────┐
│      Data Pipeline     │
└────────────┬───────────┘
             │
             ▼
┌────────────────────────┐
│        SQLite          │
└────────────┬───────────┘
             │
             ▼
┌────────────────────────┐
│       Tool API         │
└────────────┬───────────┘
             │
             ▼
┌────────────────────────┐
│  Observation Builder   │
└────────────┬───────────┘
             │
             ▼
┌────────────────────────┐
│     Derived Facts      │
└────────────┬───────────┘
             │
             ▼
┌────────────────────────┐
│ Evidence Fingerprint   │
└────────────┬───────────┘
             │
             ▼
┌────────────────────────┐
│    Adaptation State    │
└────────────┬───────────┘
             │
             ▼
┌────────────────────────┐
│    Qwen Local LLM      │
└────────────┬───────────┘
             │
             ▼
┌────────────────────────┐
│ Deterministic Policy   │
└────────────┬───────────┘
             │
             ▼
┌────────────────────────┐
│       Validator        │
└────────────┬───────────┘
             │
             ▼
┌────────────────────────┐
│ Controlled Executor    │
└────────────┬───────────┘
             │
             ▼
┌────────────────────────┐
│       Tool API         │
└────────────┬───────────┘
             │
             ▼
┌────────────────────────┐
│ Adaptive Deception Env │
└────────────┬───────────┘
             │
             ▼
┌────────────────────────┐
│ New Attacker Interaction│
└────────────┬───────────┘
             │
             └──────────────→ Cowrie / Decoy Services
```

---

## 22. Design Principle

Hệ thống không sử dụng kiến trúc:

```text
LLM
 ↓
Unrestricted command execution
```

Thay vào đó:

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

Thiết kế kết hợp:

```text
LLM flexibility
+
deterministic control
+
restricted action space
+
evidence-aware adaptation
+
observable state transitions
```

Mục tiêu là xây dựng một AI Agent có khả năng hỗ trợ Adaptive Cyber Deception trong môi trường lab nhưng vẫn đảm bảo:

- tính kiểm soát
- tính giải thích
- khả năng tái hiện
- khả năng kiểm thử
- khả năng theo dõi state transition
- giới hạn hành động rõ ràng
