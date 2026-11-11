# System & AI Agent Workflow

**Project:** Adaptive Cyber Deception with Hybrid AI Agent  
**Platform:** Cowrie Honeypot, TCP Gateway, Python, FastAPI, SQLite, Ollama, Qwen3 1.7B  
**Document Status:** Current Implementation and Development Roadmap  
**Last Updated:** November 2026

---

## 1. Project Overview

Đồ án xây dựng hệ thống **AI Agent hỗ trợ Cyber Deception thích ứng dựa trên Honeypot**, nhằm thu thập, phân tích hành vi của đối tượng tấn công và điều chỉnh môi trường deception theo các bằng chứng quan sát được.

Hệ thống kết hợp:

- **Cowrie Honeypot:** Mô phỏng môi trường SSH để ghi nhận hành vi tương tác.
- **TCP Gateway:** Tiếp nhận và chuyển tiếp kết nối SSH tới Honeypot.
- **Telemetry Pipeline:** Thu thập, chuẩn hóa và lưu trữ dữ liệu.
- **Hybrid AI Agent:** Kết hợp suy luận của mô hình ngôn ngữ với các cơ chế điều khiển xác định.
- **Tool API:** Cung cấp dữ liệu và thực thi các hành động deception được kiểm soát.
- **Adaptive Artifacts:** Các tệp mồi nhử có thể được cập nhật dựa trên hành vi quan sát được.

Mục tiêu không chỉ là ghi nhận các lệnh mà attacker thực hiện, mà còn nghiên cứu khả năng sử dụng AI Agent để **lựa chọn và điều chỉnh chiến lược deception phù hợp với hành vi tấn công**.

### 1.1. Phạm vi triển khai hiện tại

Phiên bản prototype đã triển khai được vòng lặp:

```text
Attacker Interaction
        |
        v
TCP Gateway
        |
        v
Cowrie Honeypot
        |
        v
Telemetry Collection
        |
        v
Data Pipeline + SQLite
        |
        v
AI Agent Analysis
        |
        v
Controlled Deception Action
        |
        v
Environment Updated
        |
        v
Next Attacker Interaction
```

AI Agent hiện phân tích các phiên SSH **sau khi phiên kết thúc**, sau đó cập nhật trạng thái hoặc nội dung deception cho các lần tương tác tiếp theo.

Đây là cơ chế **feedback-driven adaptive deception giữa các phiên**, chưa phải cơ chế điều chỉnh nội dung ngay trong cùng một phiên SSH.

### 1.2. Kiến trúc mục tiêu

Hệ thống hướng tới kiến trúc có khả năng phân tích hành vi và điều phối attacker đến các môi trường deception phù hợp.

```text
Attacker
    |
    v
AI-Controlled Decision Gateway
    |
    v
Deception Strategy Selection
    |
    +-------------------+
    |                   |
    v                   v
SSH Honeypot       Other Decoys
    |                   |
    +---------+---------+
              |
              v
          Telemetry
              |
              v
         AI Feedback
```

Các khả năng điều phối nhiều backend độc lập và thích ứng trong cùng phiên thuộc phạm vi phát triển tiếp theo.

---

## 2. System Architecture

### 2.1. Kiến trúc đang triển khai

```text
+--------------------------+
|   Kali Linux Attacker    |
|      192.168.255.130     |
+------------+-------------+
             |
             | SSH Connection
             v
+--------------------------+
|       TCP Gateway        |
|         Port 2223        |
|   Routing State/Logic    |
+------------+-------------+
             |
             | TCP Forwarding
             v
+--------------------------+
|     Cowrie Honeypot      |
|      SSH Port 2222       |
|    Fake Shell/HoneyFS    |
+------------+-------------+
             |
             | Events / Commands / Sessions
             v
+--------------------------+
|      Data Pipeline       |
|  Normalize and Persist   |
+------------+-------------+
             |
             v
+--------------------------+
|       SQLite DB          |
|      Session State       |
|    Telemetry History     |
+------------+-------------+
             |
             v
+--------------------------+
|         Tool API         |
| Read State / Apply Action|
+------------+-------------+
             |
             v
+--------------------------+
|      Hybrid AI Agent     |
|                          |
| Observation Builder      |
| Derived Facts            |
| Evidence Fingerprint     |
| Adaptation State         |
| Qwen Local LLM           |
| Deterministic Policy     |
| Validator                |
| Action Executor          |
+------------+-------------+
             |
             | Controlled Action
             v
+--------------------------+
|   Deception Environment  |
|                          |
| Monitoring State         |
| Adaptive Artifacts       |
| Deception History        |
+------------+-------------+
             |
             v
    Next Interaction Cycle
```

**Lưu ý:** Đây là sơ đồ logic. Việc đọc dữ liệu và thực thi hành động được thực hiện thông qua Tool API; AI Agent không trực tiếp điều khiển toàn bộ lưu lượng SSH đang đi qua Gateway.

### 2.2. Các lớp kiến trúc

Hệ thống được chia thành năm lớp:

1. **Attacker Simulation Layer:** Tạo hành vi tấn công trong môi trường kiểm thử.
2. **Gateway and Deception Layer:** Tiếp nhận kết nối, chuyển tiếp và mô phỏng dịch vụ.
3. **Telemetry and Persistence Layer:** Thu thập và lưu trữ bằng chứng tương tác.
4. **AI Deception Control Layer:** Phân tích dữ liệu, lựa chọn hành động và kiểm soát quyết định.
5. **Evaluation Layer:** Đo lường và so sánh kết quả giữa các chế độ hoạt động.

---

## 3. Laboratory Environment

### 3.1. Kali Linux

```text
Role : Attacker Simulation
IP   : 192.168.255.130
```

Kali được sử dụng để chạy các công cụ kiểm thử và attacker simulator.

Các hành vi đã sử dụng trong quá trình phát triển bao gồm:

- Network reconnaissance.
- SSH authentication attempts.
- SSH login.
- Command execution.
- File and configuration discovery.
- Credential discovery.

Các chuỗi tấn công hậu đăng nhập có nhiều giai đoạn vẫn đang được nghiên cứu và xây dựng.

### 3.2. Ubuntu Linux

```text
Role : Deception Infrastructure
IP   : 192.168.255.128
```

Ubuntu chạy các thành phần chính:

- Cowrie Honeypot.
- TCP Gateway.
- Docker Compose services.
- Data Pipeline.
- SQLite.
- Tool API.
- Realtime AI Agent.

### 3.3. Windows Host

```text
Role : Local LLM Host
IP   : 192.168.255.1
```

Windows chạy Ollama để cung cấp mô hình Qwen3 1.7B cho AI Agent.

### 3.4. Service Configuration

| Component | Port | Purpose |
|---|---|---|
| TCP Gateway | 2223 | Tiếp nhận SSH từ attacker simulator |
| Cowrie SSH | 2222 | Mô phỏng SSH Honeypot |
| Tool API | 8000 | Giao tiếp giữa Agent và hệ thống |
| Ollama | 11434 | Local LLM inference |
| HTTP Decoy | 8080 | Môi trường deception HTTP |
| Database Decoy | 3307 | Môi trường deception database |
| Redis Decoy | 6380 | Môi trường deception Redis |

Các dịch vụ deception ngoài SSH phục vụ phạm vi kiểm thử và mở rộng của dự án. Thực nghiệm Static vs Adaptive được trình bày trong tài liệu này tập trung vào Cowrie SSH.

---

## 4. Attacker Workflow

### 4.1. Vai trò của attacker simulator

Attacker simulator được sử dụng để tạo các hành vi có thể tái hiện, nhằm kiểm tra hệ thống thu thập telemetry và phản ứng deception.

Simulator không đại diện cho toàn bộ hành vi của attacker thực tế.

### 4.2. Các giai đoạn hành vi

Định hướng nghiên cứu sử dụng các giai đoạn tấn công được tham chiếu từ MITRE ATT&CK và các nghiên cứu về xâm nhập hệ thống Linux.

```text
Initial Access
      |
      v
System Discovery
      |
      v
File / Credential Discovery
      |
      v
Persistence Attempt
      |
      v
Execution / Follow-on Activity
      |
      v
Deception Interaction
```

Các nhóm hành vi dự kiến nghiên cứu:

**Initial Access**

- SSH login.
- Password-based authentication.
- Authentication failure and success.

**Discovery**

- System information discovery.
- Account discovery.
- Directory enumeration.
- Process and service discovery.

**Credential Access**

- Configuration file discovery.
- Credential file discovery.
- SSH key discovery.
- Backup information discovery.

**Persistence**

- SSH authorized key modification attempts.
- Account modification attempts.
- Scheduled task or cron discovery.

**Execution and Follow-on Activity**

- Shell command execution.
- Download or execution attempts using harmless test artifacts.
- Interaction with decoy resources.
- Further discovery based on exposed deception artifacts.

### 4.3. Trạng thái triển khai

**Đã kiểm chứng:**

- SSH login.
- Command execution.
- File discovery.
- Credential discovery.
- Adaptive response involving backup artifacts.

**Đang phát triển:**

- Bộ kịch bản tấn công hậu đăng nhập dựa trên hành vi thực tế.
- Chuỗi tấn công nhiều giai đoạn.
- Đánh giá phản ứng của Agent đối với nhiều nhóm hành vi.
- So sánh hiệu quả của các chiến lược deception trên các kịch bản khác nhau.

Không xem các kịch bản hậu đăng nhập là đã hoàn thành cho đến khi được tích hợp và kiểm chứng bằng telemetry thực tế.

---

## 5. TCP Gateway Workflow

### 5.1. Gateway Overview

TCP Gateway là điểm tiếp nhận kết nối SSH trước khi chuyển tiếp đến Honeypot.

```text
Kali
 |
 | 192.168.255.128:2223
 v
TCP Gateway
 |
 | Forward Connection
 v
Cowrie SSH
 |
 | Port 2222
 v
Fake SSH Environment
```

Gateway cho phép triển khai logic điều phối kết nối tách biệt với Cowrie.

### 5.2. Routing State

Prototype sử dụng các trạng thái routing logic:

```text
allow_normal
route_to_decoy
route_to_honeypot
```

Gateway có thể sử dụng routing state để lựa chọn đường chuyển tiếp.

Tuy nhiên, trong cấu hình kiểm thử SSH hiện tại, các đường routing vẫn dẫn về cùng một Cowrie Honeypot.

Vì vậy, **routing state hiện tại chưa tương đương với việc lựa chọn giữa nhiều backend deception độc lập**.

### 5.3. Gateway Limitations

Các hạn chế:

- Các route SSH chưa sử dụng những Honeypot có nội dung và cấu hình độc lập.
- Routing chưa chứng minh được khả năng thay đổi chiến lược deception ngay trong phiên.
- Cơ chế tương quan danh tính attacker giữa Gateway và Cowrie cần được xem xét khi đánh giá dữ liệu.

Đặc biệt, địa chỉ IP được Cowrie ghi nhận bên trong Docker có thể là địa chỉ của Gateway hoặc Docker network, không nhất thiết là địa chỉ Kali ban đầu.

Do đó, việc phân tích source IP cần phân biệt:

- IP do Gateway quan sát.
- IP do Cowrie quan sát.
- Session ID do Cowrie tạo.

### 5.4. Future Gateway Development

Các mục tiêu tiếp theo:

- Independent backend selection.
- Dynamic deception routing.
- Route validation.
- Per-attacker routing policies.
- Connection and session correlation.
- Integration between Agent decision and gateway routing.
- Support for multiple deception profiles.

---

## 6. Cowrie Honeypot Workflow

### 6.1. Cowrie Role

Cowrie là SSH Honeypot cung cấp môi trường shell giả nhằm ghi nhận hành vi attacker mà không cấp quyền truy cập vào hệ thống Ubuntu thực.

Cowrie có thể ghi nhận:

- Connection establishment.
- SSH client information.
- Login attempts.
- Login success and failure.
- Shell interaction.
- Command execution.
- Session termination.

### 6.2. SSH Interaction

```text
SSH Connection
      |
      v
Authentication Attempt
      |
      v
Fake Shell
      |
      v
Attacker Commands
      |
      v
Cowrie Events
      |
      v
Session End
```

Dữ liệu được lưu để phục vụ phân tích và thực nghiệm.

### 6.3. HoneyFS

Cowrie sử dụng filesystem giả để cung cấp các đường dẫn và nội dung đánh lừa attacker.

Những artifact liên quan đến hệ thống gồm:

```text
/root/backup_credentials.txt
/root/db_config.txt
/root/cloud_keys.txt
/srv/archive/nightly/manifest.txt
```

Một số đường dẫn cần có cả:

- Cấu trúc filesystem trong Cowrie.
- Nội dung tương ứng trong thư mục HoneyFS.

Điều này giúp các lệnh liệt kê và đọc tệp có thể phản hồi nhất quán trong môi trường giả.

### 6.4. Cowrie Execution Limitations

Cowrie mô phỏng tương tác shell, không phải môi trường Linux đầy đủ.

Do đó, các hành vi hậu đăng nhập cần được kiểm tra về mức độ hỗ trợ lệnh và tính nhất quán của phản hồi.

Không mặc định rằng mọi command hoặc payload thực tế đều có thể thực thi trong Cowrie.

---

## 7. Telemetry Collection Workflow

### 7.1. Overview

Telemetry được tạo ra từ hành vi tương tác với Honeypot hoặc các decoy service.

```text
Attacker Interaction
        |
        v
Honeypot / Decoy Logs
        |
        v
Data Pipeline
        |
        v
Normalized Events
        |
        v
SQLite Database
```

### 7.2. Collected Evidence

Các loại dữ liệu quan trọng:

- Session identifier.
- Connection timestamps.
- Authentication attempts.
- Username.
- SSH client metadata.
- Executed commands.
- Session termination.
- Decoy interaction.
- Deception action history.

### 7.3. Important Distinction

Hệ thống cần phân biệt:

**Connection metadata:** Thông tin về kết nối, client và phiên.

**Behavioral evidence:** Chuỗi lệnh, hành vi khám phá và tương tác với artifact.

**Deception events:** Những hành động môi trường đã được hệ thống thực hiện.

**Indicators of Compromise:** Các dấu hiệu kỹ thuật có giá trị trong quá trình nhận diện hoặc điều tra hoạt động xâm nhập.

Không xem mọi command hoặc event là một IOC độc lập.

---

## 8. Data Pipeline

### 8.1. Responsibilities

Data Pipeline thực hiện:

- Parse logs.
- Normalize event formats.
- Extract structured fields.
- Persist sessions.
- Persist commands.
- Persist authentication events.
- Maintain deception history.
- Support AI observation and experiment evaluation.

### 8.2. Data Flow

```text
Cowrie Events -------+
                     |
                     v
               Data Pipeline
                     |
                     v
                  SQLite
                     ^
                     |
Decoy Events --------+
```

### 8.3. Database Structure

Các bảng chính trong kiến trúc hệ thống gồm:

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

Những bảng được sử dụng trực tiếp trong thực nghiệm SSH bao gồm:

```text
sessions
events
commands
```

### 8.4. Session Metrics

Các chỉ số được trích xuất từ telemetry:

- Session duration.
- Command count.
- Unique command strings.
- Specific artifact interaction count.
- SSH client fingerprint.
- Authentication information.

Chỉ sử dụng các phiên có dữ liệu hợp lệ để tính toán kết quả.

---

## 9. Tool API Workflow

### 9.1. Purpose

Tool API là lớp giao tiếp giữa AI Agent, trạng thái hệ thống và các hành động có thể làm thay đổi môi trường deception.

```text
SQLite
   |
   v
Tool API
   ^
   |
   v
AI Agent
   |
   v
Controlled Actions
```

AI Agent sử dụng các interface được cung cấp thay vì trực tiếp sửa cơ sở dữ liệu hoặc tự ý thực thi lệnh hệ thống.

### 9.2. Read Operations

Các loại dữ liệu được cung cấp bao gồm:

- Session information.
- Recent commands.
- Recent events.
- Login attempts.
- Brute-force state.
- Decoy events.
- Monitoring state.
- Deception history.

### 9.3. Environment-Changing Actions

Các hành động hiện tại:

```text
increase_monitoring
update_artifact
```

Ngoài ra:

```text
observe_only
```

là decision không làm thay đổi môi trường.

### 9.4. Controlled Execution

Các hành động môi trường phải tuân thủ:

- Action whitelist.
- Parameter validation.
- Artifact whitelist.
- Monitoring constraints.
- Duplicate protection.

---

## 10. Hybrid AI Agent Architecture

### 10.1. Overview

AI Agent kết hợp:

```text
LLM Reasoning
      +
Deterministic Control
```

Mục đích là tận dụng khả năng phân tích hành vi của LLM nhưng vẫn kiểm soát được các hành động có thể tác động đến môi trường.

### 10.2. Internal Pipeline

```text
Observation Builder
        |
        v
Derived Facts
        |
        v
Evidence Fingerprint
        |
        v
Adaptation State
        |
        v
Qwen Local LLM
        |
        v
Deterministic Policy
        |
        v
Validator
        |
        v
Action Executor
```

### 10.3. LLM Reasoning Layer

Qwen chịu trách nhiệm:

- Behavior analysis.
- Risk assessment.
- Evidence interpretation.
- Strategy recommendation.
- Artifact selection.

Qwen tạo structured proposal và không trực tiếp thực thi hành động hệ thống.

### 10.4. Deterministic Control Layer

Python chịu trách nhiệm:

- Observation building.
- Derived facts.
- Evidence fingerprint.
- Adaptation state.
- Policy enforcement.
- Validation.
- Duplicate protection.
- Controlled execution.

---

## 11. Realtime Agent Workflow

### 11.1. Execution Model

Realtime Agent hoạt động như một dịch vụ được quản lý bởi systemd và kiểm tra telemetry theo chu kỳ.

Trong cấu hình đã thử nghiệm, chu kỳ polling là khoảng hai giây.

### 11.2. Session Processing

```text
Attacker SSH Session
        |
        v
Commands and Events
        |
        v
Session End
        |
        v
Telemetry Available
        |
        v
Observation Builder
        |
        v
AI Analysis
        |
        v
Deception Decision
        |
        v
Environment Update
```

Agent xử lý phiên đã kết thúc nhằm xây dựng observation ổn định trước khi đưa ra quyết định.

### 11.3. Important Limitation

Tên gọi Realtime Agent phản ánh cơ chế kiểm tra dữ liệu định kỳ, nhưng **không đồng nghĩa với việc Agent phản ứng ngay sau mỗi lệnh trong một phiên SSH đang mở**.

Trong prototype hiện tại:

- Telemetry của phiên được ghi nhận.
- Agent phân tích khi phiên kết thúc.
- Action được áp dụng sau quá trình phân tích.
- Artifact cập nhật được sử dụng trong các tương tác tiếp theo.

Khả năng phân tích và phản ứng ngay trong phiên đang được xem xét như hướng phát triển tiếp theo.

---

## 12. Observation Builder

Observation Builder xây dựng trạng thái phân tích từ Tool API.

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

Observation được sử dụng làm context cho AI Agent.

Dữ liệu cần được chuẩn hóa để giảm phụ thuộc vào cách diễn giải trực tiếp của LLM.

---

## 13. Derived Facts

### 13.1. Purpose

Derived Facts là các kết luận được tạo bằng logic Python từ telemetry.

Ví dụ:

```text
Multiple Failed SSH Logins
        |
        v
bruteforce_detected = true
```

```text
Successful Root Login
        |
        v
successful_root_login = true
```

```text
MySQL-related Commands
        |
        v
attacker_commands_observed = true
```

### 13.2. Existing Facts

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

### 13.3. Development Direction

Khi bộ tấn công hậu đăng nhập được tích hợp, hệ thống có thể mở rộng tập derived facts để phân biệt những hành vi như:

- System discovery.
- Credential access.
- Persistence attempt.
- Suspicious execution.
- Follow-on artifact discovery.

Đây là các nhóm hành vi mục tiêu, không phải khẳng định rằng toàn bộ detector tương ứng đã được triển khai.

---

## 14. Evidence Fingerprint

### 14.1. Purpose

Evidence Fingerprint được tạo từ các derived facts đã chuẩn hóa.

```text
Derived Facts
      |
      v
Normalize JSON
      |
      v
SHA-256
      |
      v
Evidence Fingerprint
```

Fingerprint đại diện cho trạng thái bằng chứng mà Agent sử dụng để ra quyết định.

```text
Same Evidence State
        |
        v
Same Evidence Fingerprint
```

```text
Changed Evidence State
        |
        v
New Evidence Fingerprint
```

### 14.2. Distinction from SSH Fingerprint

Cần phân biệt hai khái niệm:

**Evidence Fingerprint:** Giá trị hash do Agent tạo ra để nhận diện trạng thái bằng chứng.

**SSH Client Fingerprint / HASSH:** Thông tin đặc trưng của SSH client được ghi nhận trong telemetry.

Hai giá trị này có mục đích khác nhau và không được sử dụng thay thế cho nhau.

---

## 15. Adaptation State

### 15.1. Overview

Agent kết hợp:

```text
Evidence Fingerprint
        +
Deception History
        |
        v
Adaptation State
```

Trường quan trọng:

```text
same_evidence_already_adapted
```

### 15.2. State Interpretation

Nếu bằng chứng đã được xử lý:

```text
same_evidence_already_adapted = true
```

Nếu bằng chứng tạo ra trạng thái mới:

```text
same_evidence_already_adapted = false
```

### 15.3. Purpose

Cơ chế này giúp hạn chế:

- Repeated adaptation.
- Duplicate artifact updates.
- Redundant action execution.

---

## 16. Qwen Local LLM Analysis

### 16.1. Model

Hệ thống sử dụng:

```text
Model   : Qwen3 1.7B
Runtime : Ollama
```

Qwen nhận observation và tạo structured proposal.

### 16.2. Example Proposal

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

Đây là ví dụ về định dạng proposal.

### 16.3. LLM Restrictions

LLM không trực tiếp:

- Execute unrestricted shell commands.
- Modify the host operating system.
- Modify arbitrary files.
- Access SQLite without the provided interface.
- Create arbitrary environment actions.
- Bypass validation.

Mọi đề xuất phải được xử lý qua các lớp kiểm soát xác định.

---

## 17. Deterministic Policy

### 17.1. Purpose

Policy layer áp dụng các quy tắc quyết định dựa trên monitoring state, evidence và adaptation history.

### 17.2. Monitoring Transition

```text
NORMAL MONITORING
        |
        | Strong Malicious Evidence
        v
INCREASE MONITORING
        |
        v
ENHANCED MONITORING
```

### 17.3. Enhanced Monitoring

```text
ENHANCED MONITORING
        |
        +---- Same Evidence Already Adapted
        |                 |
        |                 v
        |             OBSERVE ONLY
        |
        +---- New Evidence
                          |
                          v
                     QWEN ANALYSIS
                          |
                 +--------+--------+
                 |                 |
                 v                 v
            OBSERVE ONLY     UPDATE ARTIFACT
```

### 17.4. Policy Override

Policy có thể điều chỉnh hoặc từ chối proposal của LLM khi không phù hợp với trạng thái hiện tại.

Điều này giúp ngăn Agent thực hiện những hành động không hợp lệ hoặc lặp lại không cần thiết.

---

## 18. Validator

### 18.1. Purpose

Validator kiểm tra quyết định trước khi chuyển tới Action Executor.

Các yếu tố kiểm tra:

- Allowed action.
- Allowed artifact.
- Required evidence.
- Parameter format.
- Monitoring state.
- Action compatibility.

### 18.2. Allowed Decisions

```text
observe_only
increase_monitoring
update_artifact
```

Không cho phép một proposal từ LLM tự tạo action bên ngoài phạm vi được định nghĩa.

---

## 19. Action Executor

### 19.1. Observe Only

```text
Decision: observe_only
Result: No environment modification
```

### 19.2. Increase Monitoring

```text
normal
   |
   v
enhanced
```

Hành động cập nhật monitoring state theo chính sách của hệ thống.

### 19.3. Update Artifact

Action Executor gửi dữ liệu có cấu trúc tới Tool API.

Các trường liên quan:

```text
session_id
artifact_name
controlled_content
evidence_fingerprint
```

Tool API kiểm tra và áp dụng cập nhật hợp lệ.

### 19.4. Execution Safety

Các hành động phải sử dụng những interface và artifact đã được cho phép.

Không cho LLM tự do tạo lệnh hệ thống hoặc thay đổi các tài nguyên ngoài phạm vi deception.

---

## 20. Adaptive Artifacts

### 20.1. Artifact Whitelist

Các artifact hiện tại:

```text
backup_credentials
db_config
cloud_keys
```

### 20.2. Artifact Selection

```text
Database Discovery
        |
        v
db_config
```

```text
Cloud / AWS Discovery
        |
        v
cloud_keys
```

```text
Credential / Backup Discovery
        |
        v
backup_credentials
```

### 20.3. Controlled Content

Qwen hỗ trợ lựa chọn artifact phù hợp.

Nội dung deception được tạo bằng Python từ các template được kiểm soát, thay vì cho LLM tạo nội dung tùy ý rồi ghi trực tiếp vào hệ thống.

### 20.4. Backup Credential Adaptation

Kịch bản đã được kiểm chứng sử dụng:

```text
/root/backup_credentials.txt
```

Trong chế độ Static, file chứa các trường thông tin backup giả cố định.

Trong chế độ Adaptive, sau khi Agent phát hiện nhóm hành vi phù hợp, nội dung được bổ sung:

```text
BACKUP_MANIFEST=/srv/archive/nightly/manifest.txt
DECEPTION_SESSION=<session_id>
```

Trường `BACKUP_MANIFEST` dẫn tới một artifact giả khác.

### 20.5. Manifest Artifact

Đường dẫn:

```text
/srv/archive/nightly/manifest.txt
```

File cung cấp những thông tin backup và database giả nhằm tạo thêm hướng khám phá.

Attacker simulator được lập trình để tiếp tục đọc file manifest khi phát hiện trường `BACKUP_MANIFEST`.

Cơ chế này đã được kiểm chứng trong môi trường Cowrie.

---

## 21. Duplicate Protection

### 21.1. Agent-Level Protection

```text
ENHANCED MONITORING
        +
SAME EVIDENCE
        +
ALREADY ADAPTED
        |
        v
OBSERVE ONLY
```

### 21.2. Tool API Protection

Tool API sử dụng những thông tin như:

```text
session_id
artifact_name
evidence_fingerprint
```

để nhận diện các hành động trùng lặp.

Khi action tương ứng đã tồn tại, API có thể trả về:

```text
already_applied
```

### 21.3. Purpose

Duplicate Protection giúp duy trì trạng thái deception ổn định và giảm số lần cập nhật không cần thiết.

---

## 22. Full Implemented Workflow

Đây là luồng hoạt động phù hợp với prototype đã triển khai.

```text
STEP 1
KALI ATTACKER
    |
    | SSH Connection
    v

STEP 2
TCP GATEWAY
    |
    | Routing / Forwarding
    v

STEP 3
COWRIE HONEYPOT
    |
    | Fake SSH Interaction
    v

STEP 4
ATTACKER COMMANDS
    |
    | Command and Session Logs
    v

STEP 5
SESSION END
    |
    v

STEP 6
DATA PIPELINE
    |
    | Parse and Normalize
    v

STEP 7
SQLITE
    |
    | Persistent Telemetry
    v

STEP 8
TOOL API
    |
    | Observation Data
    v

STEP 9
OBSERVATION BUILDER
    |
    v

STEP 10
DERIVED FACTS
    |
    v

STEP 11
EVIDENCE FINGERPRINT
    |
    v

STEP 12
ADAPTATION STATE
    |
    v

STEP 13
QWEN LOCAL LLM
    |
    | Structured Proposal
    v

STEP 14
DETERMINISTIC POLICY
    |
    v

STEP 15
VALIDATOR
    |
    v

STEP 16
ACTION EXECUTOR
    |
    | Controlled Action
    v

STEP 17
TOOL API
    |
    | Apply Validated Action
    v

STEP 18
DECEPTION ENVIRONMENT UPDATED
    |
    v

STEP 19
NEXT ATTACKER INTERACTION
```

Không phải mọi phiên đều dẫn tới cập nhật artifact.

Tùy theo trạng thái và bằng chứng, Agent có thể lựa chọn quan sát hoặc thực hiện hành động khác được cho phép.

---

## 23. Static vs Adaptive Experimental Workflow

### 23.1. Experimental Goal

Thực nghiệm nhằm đánh giá xem artifact thích ứng có tạo ra thêm hành vi khám phá trong môi trường attacker simulator hay không.

Hai chế độ được so sánh:

```text
STATIC HONEYPOT
```

và:

```text
ADAPTIVE HONEYPOT
```

### 23.2. Static Workflow

```text
Static Artifact
      |
      v
Attacker SSH Login
      |
      v
Read Backup Credentials
      |
      v
Explore Backup Directory
      |
      v
Session End
      |
      v
Cowrie Telemetry
```

Trong chế độ này:

- Realtime Agent được dừng.
- Artifact được khôi phục về baseline.
- Không có trường `BACKUP_MANIFEST`.
- Attacker simulator thực hiện hai lệnh SSH.

### 23.3. Adaptive Workflow

```text
Initial Baseline
      |
      v
Warm-up Interaction
      |
      v
Session End
      |
      v
Agent Analysis
      |
      v
Update Backup Artifact
      |
      v
Attacker SSH Login
      |
      v
Read Backup Credentials
      |
      v
Discover BACKUP_MANIFEST
      |
      v
Read Manifest
      |
      v
Session End
      |
      v
Cowrie Telemetry
```

Trong chế độ này:

- Realtime Agent được bật.
- Agent cập nhật artifact sau phiên warm-up.
- Artifact bổ sung đường dẫn tới manifest giả.
- Attacker simulator thực hiện ba lệnh SSH.

Phiên warm-up không nằm trong năm phiên đo chính thức của nhóm Adaptive.

### 23.4. Experimental Dataset

Tổng số phiên đo:

```text
Static   : 5 sessions
Adaptive : 5 sessions
Total    : 10 sessions
```

Nguồn dữ liệu:

```text
experiments/results/static_vs_adaptive.csv
```

### 23.5. Experimental Results

| Metric | Static | Adaptive |
|---|---:|---:|
| Sessions | 5 | 5 |
| Average commands per session | 2.0 | 3.0 |
| Average SSH duration | 0.756 s | 1.022 s |
| Unique command strings | 2 | 3 |
| Manifest reads | 0 | 5 |
| Unique SSH fingerprints | 1 | 1 |

Kết quả:

- Số lệnh trung bình tăng **50%**.
- Thời gian phiên SSH trung bình tăng khoảng **35,3%**.
- Có thêm năm lượt đọc file manifest giả.
- Số lượng SSH fingerprint duy nhất không thay đổi.

### 23.6. Interpretation

Kết quả cho thấy Adaptive Artifact có khả năng dẫn dắt attacker simulator thực hiện thêm hành vi khám phá theo chính sách đã lập trình.

Tuy nhiên:

- Kết quả không chứng minh hiệu quả giữ chân attacker thực tế.
- Simulator có quy tắc phản ứng cố định.
- Số lượng phiên còn nhỏ.
- Không có bằng chứng về việc tăng số IOC độc lập.
- Chênh lệch thời gian có thể liên quan trực tiếp đến lệnh bổ sung.

Vì vậy, đây là **thực nghiệm bước đầu**, chưa phải đánh giá đầy đủ về hiệu quả của toàn bộ hệ thống Cyber Deception.

### 23.7. Experimental Documentation

Chi tiết phương pháp, dữ liệu và kết luận được trình bày tại:

[Static vs Adaptive Experiment Report](experiments/EXPERIMENT_REPORT.md)

---

## 24. Post-Login Attack Research and Integration

### 24.1. Research Objective

Giai đoạn tiếp theo tập trung nghiên cứu và mô phỏng các chuỗi tấn công sau khi attacker đăng nhập SSH thành công.

Các kịch bản phải có cơ sở từ:

- MITRE ATT&CK.
- Nghiên cứu về tấn công Linux/SSH.
- Báo cáo phân tích hành vi attacker.
- Các chuỗi tấn công thực tế được công bố.

### 24.2. Research Workflow

```text
Real-World Attack Research
        |
        v
Attack Behavior Identification
        |
        v
Attack Sequence Design
        |
        v
Safe Kali Simulation
        |
        v
Cowrie Interaction
        |
        v
Telemetry Collection
        |
        v
AI Behavior Analysis
        |
        v
Adaptive Deception Decision
        |
        v
Experimental Evaluation
```

### 24.3. Integration Requirements

Mỗi kịch bản nên cung cấp:

- Tên kịch bản.
- Nguồn tham khảo.
- Mục tiêu tấn công.
- Các giai đoạn hành vi.
- Lệnh hoặc tương tác mô phỏng.
- Dấu hiệu cần ghi nhận trong telemetry.
- Kết quả mong đợi.
- Các điều kiện an toàn và giới hạn của môi trường thử nghiệm.

### 24.4. Agent Integration

Khi kịch bản mới được cung cấp, hệ thống sẽ:

1. Kiểm tra Cowrie có hỗ trợ các tương tác cần thiết hay không.
2. Xác định telemetry tương ứng.
3. Xây dựng hoặc mở rộng Derived Facts.
4. Bổ sung chính sách phân loại hành vi.
5. Lựa chọn deception artifact hoặc action phù hợp.
6. Kiểm thử end-to-end.
7. Xuất dữ liệu phục vụ đánh giá.

### 24.5. Current Status

Bộ kịch bản tấn công hậu đăng nhập đang trong quá trình nghiên cứu và phát triển.

Phần này chưa được xem là hoàn thành trong prototype hiện tại.

---

## 25. Current Implementation Status

### 25.1. Implemented Components

Các thành phần đã được triển khai và sử dụng trong quá trình phát triển:

- Cowrie SSH Honeypot.
- TCP Gateway.
- Cowrie telemetry collection.
- Data Pipeline.
- SQLite persistence.
- Tool API.
- Observation Builder.
- Derived Facts.
- Evidence Fingerprint.
- Adaptation State.
- Qwen Local LLM.
- Deterministic Policy.
- Validator.
- Action Executor.
- Monitoring state transitions.
- Adaptive artifact update.
- Duplicate protection.

### 25.2. Verified Integration

Các chức năng đã được kiểm chứng:

- Kali kết nối SSH qua TCP Gateway tới Cowrie.
- Cowrie ghi nhận phiên SSH và các lệnh.
- Data Pipeline lưu telemetry vào SQLite.
- Agent phân tích dữ liệu phiên đã kết thúc.
- Agent lựa chọn cập nhật artifact dựa trên hành vi.
- Tool API áp dụng nội dung deception đã được kiểm soát.
- Cowrie hiển thị nội dung cập nhật trong phiên tiếp theo.
- Attacker simulator khám phá và đọc manifest giả.
- Trích xuất dữ liệu của 10 phiên thực nghiệm.

### 25.3. In Development

Những phần cần hoàn thiện:

- Bộ tấn công hậu đăng nhập dựa trên nghiên cứu thực tế.
- Phân loại nhiều giai đoạn tấn công.
- Mở rộng Derived Facts và deception policies.
- Đánh giá nhiều loại deception artifact.
- Independent deception backends.
- Dynamic routing dựa trên chiến lược deception.
- Correlation giữa Gateway identity và Cowrie telemetry.
- In-session adaptive response.
- Thực nghiệm trên nhiều chuỗi tấn công.

---

## 26. System Limitations

### 26.1. Session-Based Adaptation

Agent chỉ xử lý khi phiên SSH đã kết thúc, vì vậy không phản ứng với từng lệnh ngay trong cùng phiên.

### 26.2. Limited Attack Diversity

Bộ thực nghiệm hiện tại tập trung vào credential discovery và khám phá file giả.

Chưa có tập đánh giá đa dạng gồm các chuỗi tấn công hậu đăng nhập đầy đủ.

### 26.3. Routing Backend Limitations

Các route SSH hiện vẫn dẫn tới cùng Cowrie, chưa có nhiều backend độc lập để đánh giá đầy đủ hiệu quả của routing thích ứng.

### 26.4. Simulated Attacker Behavior

Attacker simulator sử dụng logic được lập trình trước, nên phản ứng không phản ánh đầy đủ chiến thuật của attacker thực tế.

### 26.5. Experiment Scale

Thực nghiệm hiện tại chỉ có năm phiên cho mỗi chế độ.

Chưa thể rút ra kết luận có tính khái quát cao về hiệu quả thực tế.

### 26.6. Honeypot Emulation

Cowrie mô phỏng shell và filesystem nên có giới hạn trong việc tái hiện các chuỗi hậu khai thác phức tạp.

---

## 27. Development Roadmap

### Phase 1 — Core Infrastructure

**Status: Implemented**

- Cowrie deployment.
- Telemetry collection.
- Data Pipeline.
- SQLite.
- Tool API.
- Hybrid AI Agent.

### Phase 2 — Adaptive Deception Prototype

**Status: Initial Integration Verified**

- Artifact selection.
- Controlled artifact update.
- Duplicate protection.
- Feedback-driven adaptation.
- Static vs Adaptive experiment.

### Phase 3 — Gateway Improvement

**Status: Partially Implemented**

- TCP forwarding.
- Routing state.
- Connection handling.

Planned:

- Independent backends.
- Stronger routing control.
- Session correlation.
- Gateway decision integration.

### Phase 4 — Post-Login Attack Simulation

**Status: In Development**

- Research attack sequences.
- Design safe simulations.
- Generate structured attack telemetry.
- Extend behavior detection.
- Integrate new deception policies.

### Phase 5 — Expanded Evaluation

**Status: Planned**

- Multiple attack scenarios.
- Static vs Adaptive comparison.
- Behavior coverage.
- Artifact interaction measurements.
- Session metrics.
- Deception action effectiveness.
- System stability and reproducibility.

### Phase 6 — Advanced Adaptive Architecture

**Status: Future Development**

- In-session behavior processing.
- Dynamic deception profiles.
- Multiple independent decoy environments.
- Context-aware routing.
- Broader evaluation with realistic attacker behavior.

---

## 28. Final Workflow Summary

### 28.1. Current Prototype

```text
KALI ATTACKER
      |
      v
TCP GATEWAY
      |
      v
COWRIE HONEYPOT
      |
      v
ATTACKER INTERACTION
      |
      v
SESSION END
      |
      v
TELEMETRY PIPELINE
      |
      v
SQLITE
      |
      v
TOOL API
      |
      v
HYBRID AI AGENT
      |
      +-- Observation
      |
      +-- Derived Facts
      |
      +-- Evidence Fingerprint
      |
      +-- Adaptation State
      |
      +-- Qwen Analysis
      |
      +-- Deterministic Policy
      |
      +-- Validation
      |
      v
CONTROLLED ACTION
      |
      v
DECEPTION ENVIRONMENT UPDATE
      |
      v
NEXT ATTACKER INTERACTION
```

### 28.2. Target Architecture

```text
ATTACKER
   |
   v
AI-CONTROLLED GATEWAY
   |
   v
BEHAVIOR-AWARE ROUTING
   |
   +-------------------------+
   |                         |
   v                         v
SSH HONEYPOT            OTHER DECOYS
   |                         |
   +------------+------------+
                |
                v
         TELEMETRY
                |
                v
       HYBRID AI AGENT
                |
                v
       DECEPTION STRATEGY
                |
                v
        ADAPTIVE FEEDBACK
```

### 28.3. Research Direction

Hệ thống hướng tới việc kết hợp:

```text
Realistic Attack Simulation
           +
Honeypot Interaction
           +
Telemetry Analysis
           +
Hybrid AI Reasoning
           +
Deterministic Safety Control
           +
Adaptive Deception
           +
Experimental Evaluation
```

để xây dựng nền tảng Cyber Deception có khả năng điều chỉnh chiến lược dựa trên các giai đoạn và bằng chứng hành vi của đối tượng tấn công.

---

## 29. Conclusion

Prototype hiện tại đã chứng minh khả năng tích hợp Cowrie Honeypot, TCP Gateway, Data Pipeline, Tool API và Hybrid AI Agent thành một vòng lặp deception thích ứng dựa trên telemetry.

Kết quả thực nghiệm bước đầu cho thấy việc cập nhật artifact có thể khiến attacker simulator khám phá thêm mồi nhử và tạo ra bằng chứng hành vi bổ sung.

Tuy nhiên, hệ thống vẫn cần được mở rộng và đánh giá trên các chuỗi tấn công hậu đăng nhập có cơ sở từ hành vi tấn công thực tế.

Các ưu tiên tiếp theo gồm:

1. Hoàn thiện bộ kịch bản tấn công sau đăng nhập.
2. Mở rộng khả năng phân tích hành vi theo nhiều giai đoạn.
3. Nâng cấp Gateway và môi trường deception.
4. Đánh giá khả năng thích ứng của Agent trên nhiều kịch bản khác nhau.

**Trạng thái hiện tại: Prototype đã hoạt động và có kết quả thực nghiệm ban đầu; sản phẩm vẫn đang trong quá trình hoàn thiện và mở rộng.**
