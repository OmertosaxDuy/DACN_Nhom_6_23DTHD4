# Demo Scenarios

## 1. Mục tiêu demo

Phần demo nhằm chứng minh AI Agent có thể thay đổi quyết định dựa trên:

- monitoring state
- malicious evidence
- evidence fingerprint
- adaptation history
- new attacker behavior
- LLM analysis
- deterministic policy
- validator
- controlled execution

Ba nhánh chính cần thể hiện:

```text
1. Normal monitoring + strong malicious evidence
   → increase_monitoring

2. Enhanced monitoring + same evidence already adapted
   → observe_only

3. Enhanced monitoring + new evidence
   → Qwen analysis
   → update_artifact hoặc observe_only
```

Trong kịch bản database discovery đã kiểm thử, Qwen lựa chọn:

```text
update_artifact → db_config
```

---

## 2. Lab Environment

### Attacker

```text
Kali Linux
IP: 192.168.255.130
```

### Honeypot / Agent Server

```text
Ubuntu Linux
IP: 192.168.255.128
```

### Ollama Host

```text
Windows Host
IP: 192.168.255.1
```

### Main Services

```text
Cowrie SSH      : 2222
HTTP Decoy      : 8080
Database Decoy  : 3307
Redis Decoy     : 6380
Tool API        : 8000
```

### Local LLM

```text
Model   : Qwen3 1.7B
Runtime : Ollama
```

AI Agent trên Ubuntu gọi Qwen thông qua Ollama đang chạy trên Windows host.

---

# Scenario 1 – Increase Monitoring

## 3. Initial State

Monitoring ban đầu được đặt ở:

```text
normal
```

Hệ thống đã ghi nhận các malicious indicators như:

```text
SSH brute force
successful root login
Nmap HTTP probing
```

Derived facts tương ứng:

```text
bruteforce_detected = true
failed_ssh_attempts = 37
successful_root_login = true
nmap_http_probe_detected = true
nmap_http_probe_port = 8080
```

---

## 4. Decision Logic

Khi:

```text
monitoring = normal
```

và có strong malicious evidence:

```text
normal monitoring
+
strong malicious evidence
        ↓
increase_monitoring
```

Deterministic policy ưu tiên tăng monitoring trước khi thực hiện deception artifact adaptation.

Expected final decision:

```json
{
  "risk_level": "high",
  "recommended_action": "increase_monitoring",
  "action_params": {}
}
```

---

## 5. Expected Execution

Action Executor gửi action đến Tool API.

Tool API cập nhật monitoring state:

```text
normal
  ↓
enhanced
```

Ví dụ kết quả:

```json
{
  "level": "enhanced",
  "active": true,
  "already_active": false
}
```

---

## 6. Ý nghĩa

Agent không thay đổi deception artifact ngay khi mới phát hiện malicious behavior.

Thay vào đó, hệ thống tăng mức monitoring để thu thập nhiều telemetry hơn.

Luồng:

```text
Normal Monitoring
      ↓
Malicious Evidence
      ↓
Increase Monitoring
      ↓
Enhanced Monitoring
      ↓
Collect More Context
```

Điều này tạo ra một bước thích ứng trước khi Agent quyết định có cần thay đổi deception environment hay không.

---

# Scenario 2 – Observe Only

## 7. Initial State

Sau Scenario 1, monitoring đang ở:

```text
enhanced
```

Evidence fingerprint hiện tại đã từng được sử dụng trong một deception adaptation trước đó.

Ví dụ:

```text
evidence_fingerprint = e264005a8359d8dd
```

Adaptation state:

```text
same_evidence_already_adapted = true
```

Deception history có thể chứa:

```text
updated:db_config:e264005a8359d8dd
```

---

## 8. Decision Logic

Khi:

```text
monitoring = enhanced
```

và:

```text
same_evidence_already_adapted = true
```

Agent không cần thực hiện lại deception action.

Luồng:

```text
Enhanced Monitoring
       +
Same Evidence
       +
Already Adapted
       ↓
OBSERVE ONLY
```

Expected final decision:

```json
{
  "recommended_action": "observe_only",
  "action_params": {}
}
```

---

## 9. Policy Override

Qwen vẫn có thể đề xuất:

```text
update_artifact
```

nhưng deterministic policy kiểm tra adaptation state.

Ví dụ:

```text
Qwen Proposal
      ↓
update_artifact
      ↓
same_evidence_already_adapted = true
      ↓
Policy Override
      ↓
observe_only
```

Điều này chứng minh final action không phụ thuộc hoàn toàn vào LLM.

---

## 10. Expected Execution

`observe_only` không gọi action endpoint làm thay đổi môi trường.

Expected execution result:

```json
{
  "status": "no_action",
  "action": "observe_only"
}
```

---

## 11. Ý nghĩa

Agent không lặp lại cùng một deception adaptation đối với cùng evidence state.

Cơ chế này giúp tránh:

```text
Repeated artifact update
Repeated deception event
Unnecessary environment changes
Repeated identical adaptation
```

Hệ thống tiếp tục quan sát attacker để chờ evidence mới.

---

# Scenario 3 – New Evidence and Artifact Update

## 12. Initial State

Monitoring vẫn đang ở:

```text
enhanced
```

Attacker tạo hành vi mới thông qua Cowrie SSH.

Từ Kali:

```bash
ssh root@192.168.255.128 -p 2222
```

Sau khi đăng nhập, attacker thực hiện database-related discovery:

```bash
cat /etc/mysql/my.cnf
```

```bash
find / -iname "*mysql*" 2>/dev/null
```

Sau đó kết thúc session:

```bash
exit
```

---

## 13. Cowrie Telemetry

Cowrie ghi nhận session mới và các command mới.

Ví dụ:

```text
command_count = 3
```

Recent commands:

```text
cat /etc/mysql/my.cnf
find / -iname "*mysql*" 2>/dev/null
exit
```

Cowrie cũng ghi nhận:

```text
login_success
command
command
command
session_end
```

---

## 14. Derived Facts Update

Từ telemetry mới, Python cập nhật derived facts:

```text
attacker_commands_observed = true
attacker_command_count = 3
```

và:

```text
recent_attacker_commands = [
    "cat /etc/mysql/my.cnf",
    "find / -iname \"*mysql*\" 2>/dev/null",
    "exit"
]
```

Đây là evidence mới mà trước đó chưa tồn tại trong state.

---

## 15. New Evidence Fingerprint

Fingerprint cũ:

```text
e264005a8359d8dd
```

Sau khi derived facts thay đổi, fingerprint mới được tạo:

```text
dc01172b11d69b9f
```

Luồng:

```text
Old Derived Facts
       ↓
Old Fingerprint

New Attacker Commands
       ↓
Updated Derived Facts
       ↓
New Fingerprint
```

Do fingerprint mới chưa từng kích hoạt deception adaptation:

```text
same_evidence_already_adapted = false
```

---

## 16. Ý nghĩa của New Evidence

Điểm quan trọng:

```text
new evidence
```

không có nghĩa là:

```text
always update_artifact
```

New evidence chỉ có nghĩa là Agent được phép xem xét một adaptation mới.

Luồng chính xác:

```text
Enhanced Monitoring
       +
New Evidence
       ↓
Qwen Analysis
       ↓
Structured Proposal
```

Qwen có thể đề xuất:

```text
observe_only
```

hoặc:

```text
update_artifact
```

tùy theo evidence.

---

## 17. AI Decision trong Database Discovery Scenario

Trong scenario đã kiểm thử, các command:

```text
cat /etc/mysql/my.cnf
find / -iname "*mysql*"
```

thể hiện database-related discovery.

Qwen đề xuất:

```json
{
  "risk_level": "high",
  "recommended_action": "update_artifact",
  "action_params": {
    "artifact_name": "db_config"
  }
}
```

Artifact được chọn:

```text
db_config
```

Decision sau đó tiếp tục đi qua:

```text
Policy
  ↓
Validator
  ↓
Action Executor
```

---

## 18. Artifact Selection

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
Cloud / AWS credential discovery
→ prefer cloud_keys
```

```text
Credential / backup discovery
→ prefer backup_credentials
```

Trong scenario hiện tại:

```text
MySQL-related commands
       ↓
db_config
```

---

## 19. Expected Execution

Action Executor gửi request đã được kiểm soát tới Tool API.

Request logic gồm:

```text
session_id
artifact_name
controlled deception content
evidence_fingerprint
```

Tool API cập nhật deception artifact:

```text
db_config
```

Ví dụ expected result:

```json
{
  "status": "success",
  "artifact_name": "db_config"
}
```

Một deception event mới được lưu lại cùng evidence fingerprint.

---

## 20. Duplicate Protection

Sau khi artifact đã được cập nhật cho fingerprint mới:

```text
dc01172b11d69b9f
```

lần chạy Agent tiếp theo sẽ thấy:

```text
same_evidence_already_adapted = true
```

Khi đó:

```text
enhanced monitoring
+
same evidence
+
already adapted
↓
observe_only
```

Ngoài Agent policy, Tool API còn có duplicate protection riêng.

Nếu cùng:

```text
session_id
artifact_name
evidence_fingerprint
```

được gửi lại, Tool API trả:

```text
already_applied
```

thay vì tạo action trùng.

---

# 21. Full Demo Flow

Toàn bộ demo có thể trình bày theo thứ tự sau.

```text
STEP 1
Prepare existing malicious evidence
       ↓

STEP 2
Set monitoring to normal
       ↓

STEP 3
Run Agent
       ↓
Strong malicious evidence detected
       ↓
increase_monitoring
       ↓
Monitoring becomes enhanced
```

Tiếp theo:

```text
STEP 4
Run Agent again
       ↓
Enhanced monitoring
+
same evidence already adapted
       ↓
observe_only
```

Sau đó tạo evidence mới:

```text
STEP 5
Kali SSH → Cowrie
       ↓
Run database discovery commands
       ↓
Cowrie records new commands
```

Cuối cùng:

```text
STEP 6
Run Agent again
       ↓
Derived facts changed
       ↓
New evidence fingerprint
       ↓
same_evidence_already_adapted = false
       ↓
Qwen analysis
       ↓
update_artifact
       ↓
db_config updated
```

---

# 22. Demo State Transition

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

# 23. Hybrid Decision Flow

Demo cũng cần thể hiện rằng Qwen không trực tiếp điều khiển môi trường.

```text
Observation
     ↓
Derived Facts
     ↓
Evidence Fingerprint
     ↓
Adaptation State
     ↓
Qwen Analysis
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
```

LLM chịu trách nhiệm:

```text
Behavior analysis
Risk assessment
Evidence interpretation
Strategy recommendation
Artifact selection
```

Python / Tool API chịu trách nhiệm:

```text
State tracking
Policy enforcement
Validation
Duplicate protection
Controlled execution
```

---

# 24. What the Demo Proves

Demo chứng minh:

- Cowrie thu thập session, login và attacker command thực tế.
- Decoy services cung cấp thêm reconnaissance telemetry.
- Data Pipeline chuẩn hóa dữ liệu trước khi Agent sử dụng.
- Tool API tách AI Agent khỏi database trực tiếp.
- Monitoring state ảnh hưởng đến behavior của Agent.
- Normal monitoring có thể được nâng lên enhanced.
- Derived facts được tạo deterministic từ telemetry.
- Evidence fingerprint thay đổi khi attacker behavior thay đổi.
- Agent phân biệt same evidence và new evidence.
- Adaptation history được sử dụng để tránh action lặp lại.
- Qwen tạo structured recommendation.
- Policy layer có thể override Qwen.
- Validator giới hạn action hợp lệ.
- `observe_only` không thay đổi môi trường.
- `increase_monitoring` thay đổi monitoring state.
- `update_artifact` thay đổi deception environment có kiểm soát.
- Tool API cung cấp lớp duplicate protection thứ hai.
- LLM không trực tiếp thực thi shell command.
- LLM không trực tiếp sửa database hoặc host configuration.
- Hệ thống tạo được vòng lặp Adaptive Cyber Deception có state.

---

# 25. Expected Adaptive Loop

```text
Attacker Action
      ↓
Cowrie / Decoy Telemetry
      ↓
Data Pipeline
      ↓
SQLite
      ↓
Tool API
      ↓
Observation
      ↓
Derived Facts
      ↓
Evidence Fingerprint
      ↓
Adaptation State
      ↓
Qwen Analysis
      ↓
Policy + Validation
      ↓
Controlled Action
      ↓
Environment Adaptation
      ↓
New Attacker Interaction
      ↓
Observe Again
```

---

## 26. Demo Conclusion

Ba behavior chính đã được kiểm thử:

```text
Normal monitoring
+
strong malicious evidence
→ increase_monitoring
```

```text
Enhanced monitoring
+
same evidence already adapted
→ observe_only
```

```text
Enhanced monitoring
+
new database-related evidence
→ Qwen analysis
→ update_artifact
→ db_config
```

Ba scenario này chứng minh hệ thống không chỉ phát hiện attacker behavior mà còn sử dụng monitoring state, evidence state và adaptation history để thay đổi response theo từng chu kỳ.

Đây là vòng lặp Adaptive Cyber Deception chính của hệ thống:

```text
Observe → Analyze → Decide → Act → Adapt → Observe Again
```
