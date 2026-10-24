# Adaptive Cyber Deception with Hybrid AI Agent

Đồ án xây dựng hệ thống **AI Agent hỗ trợ Adaptive Cyber Deception dựa trên Honeypot**, sử dụng Cowrie Honeypot, các decoy service, Tool API và Local LLM.

## Project Overview

Hệ thống thu thập hành vi từ attacker thông qua Cowrie và các dịch vụ decoy, xử lý log qua Data Pipeline, lưu dữ liệu vào SQLite và cung cấp dữ liệu cho AI Agent thông qua Tool API.

AI Agent hoạt động theo mô hình Hybrid:

```text
Observe → Analyze → Decide → Act → Adapt → Observe Again
```

Trong đó:

- Qwen Local LLM phân tích hành vi và đề xuất action.
- Python xử lý derived facts, evidence fingerprint và adaptation state.
- Policy layer và validator kiểm soát quyết định của LLM.
- Action Executor chỉ thực thi các action được whitelist.
- Tool API chịu trách nhiệm thay đổi monitoring state hoặc deception artifact.
## Team Members

- Lê Duy
- Lê Phi Hoàng
- Phạm Nhật Huy


## Core Architecture

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
Policy + Validator
      ↓
Action Executor
      ↓
Adaptive Deception Environment
      ↓
Observe Again
```

## Adaptive Actions

Hệ thống hiện hỗ trợ ba decision/action chính:

```text
observe_only
increase_monitoring
update_artifact
```

Trong đó:

- `observe_only`: Agent tiếp tục quan sát và không gọi action endpoint thay đổi môi trường.
- `increase_monitoring`: tăng monitoring từ normal lên enhanced.
- `update_artifact`: cập nhật deception artifact được whitelist.

Ba nhánh adaptive chính đã được kiểm thử:

```text
Normal monitoring + strong malicious evidence
→ increase_monitoring
```

```text
Enhanced monitoring + same evidence already adapted
→ observe_only
```

```text
Enhanced monitoring + new evidence
→ Qwen analysis
→ update_artifact hoặc observe_only
```

Trong kịch bản database discovery đã kiểm thử, Qwen chọn:

```text
update_artifact → db_config
```

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

## Documentation

- [System & AI Agent Workflow](WORKFLOW.md)
- [System Architecture](ARCHITECTURE.md)
- [Demo Scenarios](DEMO.md)

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
└── README.md
```

## Current Status

Các thành phần lõi đã hoạt động:

- Cowrie ghi nhận login, session và command.
- Decoy services ghi nhận reconnaissance và probing.
- Data Pipeline xử lý và lưu dữ liệu vào SQLite.
- Tool API cung cấp dữ liệu và controlled action endpoints.
- Observation Builder tổng hợp trạng thái hệ thống.
- Python tạo derived facts từ telemetry.
- Evidence fingerprint giúp nhận biết trạng thái evidence mới hoặc đã từng xử lý.
- Adaptation state kiểm tra lịch sử deception.
- Local Qwen thực hiện phân tích hành vi và đề xuất strategy.
- Deterministic policy có thể override quyết định của LLM khi cần.
- Validator kiểm tra action và parameters trước khi thực thi.
- Action Executor chỉ cho phép các action đã được kiểm soát.
- Tool API có duplicate protection cho deception artifact update.
- Agent có thể tăng monitoring hoặc thay đổi deception artifact theo trạng thái attacker.

## Adaptive Decision Flow

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
                       OBSERVE AGAIN
```

## Safety Design

LLM không được phép thực thi shell command tự do hoặc sửa trực tiếp hệ thống.

LLM chỉ tạo structured proposal. Decision cuối cùng phải đi qua các lớp kiểm soát:

```text
LLM Proposal
    ↓
Deterministic Policy
    ↓
Schema / Safety Validation
    ↓
Controlled Action Executor
    ↓
Tool API
```

Các deception artifact hiện được whitelist:

```text
backup_credentials
db_config
cloud_keys
```

LLM chỉ lựa chọn loại artifact phù hợp với hành vi quan sát được. Nội dung artifact được Python tạo từ controlled template.

## Design Principle

Hệ thống không sử dụng mô hình:

```text
LLM → unrestricted command execution
```

Mà sử dụng:

```text
LLM
 ↓
Recommendation
 ↓
Deterministic Control
 ↓
Validation
 ↓
Whitelisted Tool
 ↓
Controlled Environment Change
```

Mục tiêu của thiết kế là tận dụng khả năng phân tích linh hoạt của Local LLM nhưng vẫn giữ các hành động deception trong phạm vi kiểm soát, có thể giải thích và tái hiện trong môi trường lab.
