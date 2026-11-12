E-Commerce Returns Review Workflow
Overview
This project implements a graph-based multi-agent workflow for processing e-commerce return requests using Python.

The workflow automates the initial review of customer return, refund, and replacement requests while ensuring that high-value, risky, or exceptional cases are routed for human approval.

The implementation demonstrates:

Multi-Agent Architecture
Deterministic Business Rules
Human-in-the-Loop Approval
Input and Output Guardrails
Structured Workflow Execution
Customer Communication Generation
Configuration Validation
Workflow Pause and Resume
Workflow Architecture
Return Request
      |
      v
Eligibility Agent
      |
      v
Risk Agent
      |
      v
Approval Gateway
      |
      |---- Automatic Approval
      |
      |---- Human Review
                 |
                 v
         Manager Approve / Reject
                 |
                 v
Customer Response Agent
      |
      v
Final Output
Agents
1. Eligibility Agent
Validates return requests against company return policies.

Checks include:

Return submitted within 30 days
Invoice availability
Product condition
Photo evidence availability for damaged items
Previous return history
Output:

Eligibility Status
Eligibility Findings
2. Risk Agent
Performs risk assessment on return requests.

Evaluates:

High-value requests
Missing evidence
Frequent return activity
Other policy concerns
Output:

Risk Level
Risk Assessment
3. Customer Response Agent
Creates customer-facing communication based on the final workflow decision.

The response:

Does not promise refunds
Does not confirm replacements
Clearly communicates review outcomes
Business Rules
Automatic approval is granted only when all conditions are satisfied.

Rule	Requirement
Amount	Below ₹25,000
Delivery Window	Within 30 Days
Invoice	Available
Condition	Unopened OR Damaged with Photo Evidence
Return Frequency	Fewer than 3 returns in 90 days
Risk Assessment	Must not be HIGH
If any rule fails, the request is escalated for human review.

Human-In-The-Loop Review
Requests requiring escalation pause workflow execution.

The reviewer receives:

Request ID
Product Name
Requested Amount
Eligibility Findings
Risk Assessment
Allowed responses:

approve
reject
Workflow resumes only after valid input is received.

Human rejection cannot be overridden.

Guardrails
The application includes security and safety guardrails.

Input Guardrails
Maximum length validation
Personally Identifiable Information (PII) detection
Prompt injection detection
SQL injection detection
Cross-site scripting (XSS) detection
Output Guardrails
Sensitive information leakage prevention
Response safety validation
Configuration
Create a .env file in the project root.

AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_BASE_URL=your_endpoint
AZURE_OPENAI_MODEL=gpt-4o
Required Files
project/
│
├── returns_workflow.py
├── guardrails.py
├── returns.json
├── .env
└── README.md
Installation
Install required dependencies.

pip install python-dotenv
Running the Workflow
Execute:

python returns_workflow.py
The workflow will:

Load return requests from returns.json
Run Eligibility Agent
Run Risk Agent
Apply business rules
Trigger human review when necessary
Generate customer communication
Produce final workflow output
Output Structure
Each processed request generates:

{
  "request_id": "RET201",
  "order_id": "ORD-7301",
  "product": "Wireless Keyboard",
  "requested_amount": 1499,
  "eligibility_findings": {},
  "risk_assessment": {},
  "approval_route": "Automatic",
  "final_decision": "AUTO_APPROVED",
  "customer_communication": "..."
}
Final Decision Types
AUTO_APPROVED
Request satisfied all business rules and required no manual approval.

MANAGER_APPROVED
Request was escalated and approved by a human reviewer.

MANAGER_REJECTED
Request was escalated and rejected by a human reviewer.

Demonstrated Capabilities
Multiple AI-style agents
Graph-based workflow orchestration
Deterministic policy enforcement
Human-in-the-loop approval
Workflow pause and resume
Approval and rejection flows
Guardrail enforcement
Structured outputs
Environment configuration validation