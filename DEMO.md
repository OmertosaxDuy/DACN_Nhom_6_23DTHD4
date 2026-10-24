# Demo Scenarios

## 1. Mục tiêu demo

Phần demo nhằm chứng minh AI Agent có thể thay đổi hành vi theo trạng thái hệ thống và evidence mới thu được từ attacker.

Ba nhánh chính cần thể hiện:

```text
1. Normal + malicious evidence
   → increase_monitoring

2. Enhanced + same evidence
   → observe_only

3. Enhanced + new evidence
   → update_artifact
```

---

## 2. Lab Environment

### Attacker

```text
Kali Linux
IP: 192.168.255.130
```

### Honeypot / Server

```text
Ubuntu
IP: 192.168.255.128
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
Model: Qwen3 1.7B
Runtime: Ollama
```

---

# Scenario 1 – Increase Monitoring

## Initial State

Monitoring được đặt ở trạng thái:

```text
normal
```

Attacker đã tạo các evidence như:

```text
SSH brute force
successful root login
Nmap HTTP probing
```

Derived facts:

```text
bruteforce_detected = true
successful_root_login = true
nmap_http_probe_detected = true
```

## Expected Decision

```text
normal monitoring
+
strong malicious evidence
↓
increase_monitoring
```

Expected decision:

```json
{
  "recommended_action": "increase_monitoring",
  "action_params": {}
}
```

## Expected Result

Tool API cập nhật:

```text
monitoring_state
normal → enhanced
```

Ví dụ:

```json
{
  "level": "enhanced",
  "active": true,
  "already_active": false
}
```

## Ý nghĩa

Agent chưa thay đổi deception artifact ngay lập tức.

Thay vào đó hệ thống tăng mức monitoring để thu thập nhiều telemetry hơn trước khi thực hiện deception adaptation tiếp theo.

---

# Scenario 2 – Observe Only

## Initial State

Monitoring hiện tại:

```text
enhanced
```

Evidence fingerprint hiện tại đã từng được sử dụng để kích hoạt deception action.

Ví dụ:

```text
evidence_fingerprint = e264005a8359d8dd
```

Adaptation state:

```text
same_evidence_already_adapted = true
```

## Expected Decision

```text
enhanced monitoring
+
same evidence
+
already adapted
↓
observe_only
```

Expected decision:

```json
{
  "recommended_action": "observe_only",
  "action_params": {}
}
```

## Expected Result

```json
{
  "status": "no_action",
  "action": "observe_only"
}
```

## Ý nghĩa

Agent không lặp lại cùng một deception action đối với cùng evidence state.

Điều này giúp tránh:

```text
Repeated artifact update
Repeated deception event
Unnecessary environment changes
```

---

# Scenario 3 – Update Artifact

## Initial State

Monitoring vẫn ở:

```text
enhanced
```

Attacker tạo thêm evidence mới thông qua Cowrie SSH.

Ví dụ trên Kali:

```bash
ssh root@192.168.255.128 -p 2222
```

Sau khi đăng nhập, attacker thực hiện:

```bash
cat /etc/mysql/my.cnf
```

và:

```bash
find / -iname "*mysql*" 2>/dev/null
```

Sau đó:

```bash
exit
```

---

## Data Collected

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

Derived facts thay đổi:

```text
attacker_commands_observed = true
attacker_command_count = 3
```

---

## New Evidence Fingerprint

Fingerprint cũ:

```text
e264005a8359d8dd
```

Fingerprint mới:

```text
dc01172b11d69b9f
```

Adaptation state:

```text
same_evidence_already_adapted = false
```

Điều này chứng minh Agent nhận biết được một trạng thái attacker mới.

---

## Expected AI Decision

Qwen phân tích hành vi database discovery và đề xuất:

```json
{
  "risk_level": "high",
  "recommended_action": "update_artifact",
  "action_params": {
    "artifact_name": "db_config"
  }
}
```

---

## Expected Execution

Action Executor gửi request đến Tool API.

Tool API cập nhật deception artifact:

```text
db_config
```

Expected result:

```json
{
  "status": "success",
  "artifact_name": "db_config"
}
```

Một deception event mới được ghi lại.

---

# 3. Full Demo Flow

Toàn bộ demo có thể trình bày theo thứ tự:

```text
STEP 1
Reset monitoring to normal
       ↓

STEP 2
Run Agent
       ↓
Malicious evidence detected
       ↓
increase_monitoring
       ↓

STEP 3
Run Agent again
       ↓
Monitoring = enhanced
Same evidence already adapted
       ↓
observe_only
       ↓

STEP 4
Kali SSH vào Cowrie
       ↓
Run new database discovery commands
       ↓

STEP 5
Run Agent again
       ↓
New evidence fingerprint
       ↓
same_evidence_already_adapted = false
       ↓
update_artifact
       ↓
db_config updated
```

---

# 4. State Transition Demo

```text
              ┌─────────────────────┐
              │  NORMAL MONITORING  │
              └──────────┬──────────┘
                         │
                  malicious evidence
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
        Same evidence          New evidence
              │                      │
              ▼                      ▼
     ┌────────────────┐    ┌─────────────────┐
     │  OBSERVE ONLY  │    │ UPDATE ARTIFACT │
     └────────────────┘    └────────┬────────┘
                                    │
                                    ▼
                           Adaptive Environment
                                    │
                                    ▼
                              Observe Again
```

---

# 5. What the Demo Proves

Demo chứng minh các điểm sau:

- Agent sử dụng telemetry thực tế từ Cowrie và decoy services.
- Monitoring state ảnh hưởng trực tiếp đến action.
- Agent phân biệt same evidence và new evidence.
- Evidence fingerprint được dùng để theo dõi trạng thái attacker.
- LLM không trực tiếp thực thi hành động.
- Policy layer có thể override LLM decision.
- Validator giới hạn action hợp lệ.
- Tool API kiểm soát thay đổi môi trường.
- Duplicate deception action được ngăn chặn.
- Environment có thể thay đổi theo attacker behavior.

---

# 6. Expected Adaptive Loop

```text
Attacker Action
      ↓
Telemetry
      ↓
Observation
      ↓
Derived Facts
      ↓
Evidence Fingerprint
      ↓
LLM Analysis
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

Đây là vòng lặp Adaptive Cyber Deception chính của hệ thống.
