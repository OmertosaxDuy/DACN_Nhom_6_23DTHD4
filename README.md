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
Qwen Local LLM
      ↓
Policy + Validator
      ↓
Action Executor
      ↓
Adaptive Deception Environment
```

## Adaptive Actions

Hệ thống hiện hỗ trợ ba action chính:

```text
observe_only
increase_monitoring
update_artifact
```

Ba nhánh adaptive đã được kiểm thử:

```text
Normal monitoring + malicious evidence
→ increase_monitoring
```

```text
Enhanced monitoring + same evidence
→ observe_only
```

```text
Enhanced monitoring + new evidence
→ update_artifact
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
└── README.md
```

## Current Status

Các thành phần lõi đã hoạt động:

- Cowrie ghi nhận login, session và command.
- Decoy services ghi nhận reconnaissance và probing.
- Data Pipeline lưu dữ liệu vào SQLite.
- Tool API cung cấp read/action tools.
- Local Qwen thực hiện phân tích hành vi.
- Hybrid policy kiểm soát action.
- Evidence fingerprint ngăn adaptation trùng lặp.
- Agent có thể tăng monitoring hoặc thay đổi deception artifact theo hành vi mới.

## Safety Design

LLM không được phép thực thi shell command tự do hoặc sửa trực tiếp hệ thống.

Luồng action luôn đi qua:

```text
LLM Proposal
    ↓
Deterministic Policy
    ↓
Validation
    ↓
Whitelisted Action
    ↓
Tool API
```

Mục tiêu của thiết kế là giữ AI Agent linh hoạt trong phân tích nhưng vẫn kiểm soát được hành động trong môi trường lab.
