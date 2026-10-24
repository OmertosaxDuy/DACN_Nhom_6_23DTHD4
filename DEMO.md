# Demo Scenarios

## 1. Mục tiêu demo

Demo hiện tại nhằm chứng minh **adaptive feedback logic** của AI Agent, là nền tảng cho target architecture:

```text
Attacker
   ↓
AI Decision Gateway
   ↓
Honeypot / Decoy Environment
```

Prototype hiện tại tập trung chứng minh Agent có thể:

- nhận telemetry
- phân tích attacker state
- duy trì adaptation state
- thay đổi monitoring
- thay đổi deception artifact
- tránh duplicate adaptation

---

## 2. Target Demo Architecture

Kiến trúc mục tiêu:

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
Feedback to AI Agent
```

---

## 3. Current Prototype Demo

Prototype hiện tại thực hiện:

```text
Kali Attacker
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

Đây là feedback-driven adaptive loop.

Inline routing trước Honeypot là bước phát triển tiếp theo.

---

## 4. Lab Environment

### Kali

```text
IP: 192.168.255.130
```

### Ubuntu

```text
IP: 192.168.255.128
```

### Windows / Ollama Host

```text
IP: 192.168.255.1
```

### Services

```text
Cowrie SSH      : 2222
HTTP Decoy      : 8080
Database Decoy  : 3307
Redis Decoy     : 6380
Tool API        : 8000
```

### LLM

```text
Qwen3 1.7B
via Ollama
```

---

# Scenario 1 – Increase Monitoring

## 5. Initial State

Monitoring:

```text
normal
```

Evidence:

```text
SSH brute force
successful root login
Nmap HTTP probing
```

Derived facts:

```text
bruteforce_detected = true
failed_ssh_attempts = 37
successful_root_login = true
nmap_http_probe_detected = true
```

---

## 6. Decision

Policy:

```text
normal
+
strong malicious evidence
↓
increase_monitoring
```

Expected final decision:

```json
{
  "recommended_action": "increase_monitoring",
  "action_params": {}
}
```

---

## 7. Result

Monitoring chuyển:

```text
normal
  ↓
enhanced
```

Ý nghĩa:

```text
AI detects higher-risk behavior
→ collect more telemetry
→ improve next decision
```

---

# Scenario 2 – Observe Only

## 8. Initial State

Monitoring:

```text
enhanced
```

Adaptation state:

```text
same_evidence_already_adapted = true
```

---

## 9. Decision

```text
enhanced
+
same evidence
+
already adapted
↓
observe_only
```

Expected:

```json
{
  "recommended_action": "observe_only",
  "action_params": {}
}
```

---

## 10. Policy Override

Qwen có thể vẫn đề xuất:

```text
update_artifact
```

nhưng policy kiểm tra adaptation state:

```text
Qwen Proposal
      ↓
same evidence already adapted
      ↓
Policy Override
      ↓
observe_only
```

Điều này chứng minh LLM không có quyền trực tiếp điều khiển môi trường.

---

# Scenario 3 – New Database Evidence

## 11. Create New Evidence

Từ Kali:

```bash
ssh root@192.168.255.128 -p 2222
```

Attacker chạy:

```bash
cat /etc/mysql/my.cnf
```

```bash
find / -iname "*mysql*" 2>/dev/null
```

sau đó:

```bash
exit
```

---

## 12. Telemetry

Cowrie ghi nhận:

```text
command_count = 3
```

Recent commands:

```text
cat /etc/mysql/my.cnf
find / -iname "*mysql*" 2>/dev/null
exit
```

Derived facts:

```text
attacker_commands_observed = true
attacker_command_count = 3
```

---

## 13. Fingerprint Change

Old:

```text
e264005a8359d8dd
```

New:

```text
dc01172b11d69b9f
```

Adaptation state:

```text
same_evidence_already_adapted = false
```

---

## 14. AI Analysis

New evidence được gửi tới Qwen.

```text
database-related attacker behavior
        ↓
Qwen analysis
        ↓
update_artifact
        ↓
db_config
```

Expected:

```json
{
  "recommended_action": "update_artifact",
  "action_params": {
    "artifact_name": "db_config"
  }
}
```

---

## 15. Controlled Execution

Decision tiếp tục đi qua:

```text
Qwen
 ↓
Policy
 ↓
Validator
 ↓
Action Executor
 ↓
Tool API
```

Tool API cập nhật:

```text
db_config
```

Một deception event mới được ghi cùng evidence fingerprint.

---

## 16. Duplicate Protection

Lần chạy tiếp theo:

```text
same fingerprint
↓
same_evidence_already_adapted = true
↓
observe_only
```

Tool API cũng có lớp duplicate gate:

```text
same session
+
same artifact
+
same fingerprint
↓
already_applied
```

---

# 17. Adaptive State Demo

```text
NORMAL
   │
   │ malicious evidence
   ▼
INCREASE MONITORING
   │
   ▼
ENHANCED
   │
   ├── same evidence
   │      ↓
   │  OBSERVE ONLY
   │
   └── new evidence
          ↓
      QWEN ANALYSIS
          ↓
      ┌───┴───────────┐
      │               │
      ▼               ▼
OBSERVE ONLY    UPDATE ARTIFACT
                      │
                      ▼
                ENVIRONMENT ADAPTS
```

---

# 18. Target Inline Workflow

Sau khi bổ sung AI Gateway / routing layer, demo mục tiêu sẽ trở thành:

```text
STEP 1
Kali initiates interaction
       ↓

STEP 2
Traffic enters AI Deception Gateway
       ↓

STEP 3
AI reads current attacker state
       ↓

STEP 4
AI selects deception strategy
       ↓

STEP 5
Attacker is routed to selected
Honeypot / Decoy environment
       ↓

STEP 6
Interaction produces telemetry
       ↓

STEP 7
Data Pipeline + SQLite + Tool API
update feedback state
       ↓

STEP 8
AI adapts next interaction
```

---

## 19. Current vs Target Demo

### Current

```text
Attacker
→ Honeypot
→ Telemetry
→ AI
→ Adapt
```

### Target

```text
Attacker
→ AI Gateway
→ Honeypot / Decoy
→ Telemetry
→ AI Feedback
→ Next Adaptive Decision
```

Đây là điểm cần nói rõ khi báo cáo.

---

## 20. What Current Demo Proves

Prototype hiện tại chứng minh:

- telemetry collection hoạt động
- monitoring state hoạt động
- evidence fingerprint hoạt động
- adaptation history hoạt động
- Qwen reasoning hoạt động
- deterministic policy hoạt động
- validator hoạt động
- controlled action hoạt động
- duplicate protection hoạt động
- environment có thể được thích ứng

---

## 21. What Remains for Target Architecture

Cần bổ sung:

- Inline AI Gateway
- Traffic interception / proxy layer
- Dynamic routing
- Decoy selection
- Route validation
- Connection/session continuity
- Integration giữa routing decision và deception state

---

## 22. Final Adaptive Loop

Target loop:

```text
ATTACKER REQUEST
      ↓
AI GATEWAY
      ↓
ANALYZE CURRENT STATE
      ↓
SELECT DECEPTION STRATEGY
      ↓
HONEYPOT / DECOY INTERACTION
      ↓
TELEMETRY
      ↓
DATA PIPELINE
      ↓
STATE UPDATE
      ↓
AI FEEDBACK
      ↓
NEXT DECISION
```

Tóm tắt:

```text
Observe → Analyze → Decide → Route/Act → Adapt → Observe Again
```
