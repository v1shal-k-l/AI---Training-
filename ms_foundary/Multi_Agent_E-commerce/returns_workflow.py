# returns_workflow.py

import os
import json
from dataclasses import dataclass, asdict

from guardrails import (
    validate_length,
    contains_pii,
    detect_prompt_injection,
    detect_sql_injection,
    detect_xss,
    REFUSAL_MESSAGE,
    output_contains_sensitive_data,
    run_input_guardrails,
    run_output_guardrails
)

###############################################################################
# CONFIG VALIDATION
###############################################################################
from dotenv import load_dotenv
import os

load_dotenv()

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_BASE_URL = os.getenv("AZURE_OPENAI_BASE_URL")
AZURE_OPENAI_MODEL = os.getenv("AZURE_OPENAI_MODEL")
def validate_configuration():

    required = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_BASE_URL",
        "AZURE_OPENAI_MODEL"
    ]

    missing = []

    for item in required:

        value = os.getenv(item)

        if not value:
            missing.append(item)

    if missing:

        raise EnvironmentError(
            f"Missing configuration: {', '.join(missing)}"
        )


###############################################################################
# STATE
###############################################################################

@dataclass
class WorkflowState:

    request_id: str
    order_id: str
    product: str
    product_category: str

    requested_amount: float

    eligibility_findings: dict
    risk_assessment: dict

    approval_route: str
    final_decision: str

    customer_communication: str


###############################################################################
# AGENT 1
# ELIGIBILITY AGENT
###############################################################################

class EligibilityAgent:

    def execute(self, request):

        findings = []

        if request["amount_inr"] >= 25000:

            findings.append(
                "Amount exceeds auto approval threshold."
            )

        if request["days_since_delivery"] > 30:

            findings.append(
                "Return requested after 30 days."
            )

        if not request["invoice_available"]:

            findings.append(
                "Invoice evidence missing."
            )

        if (
            request["item_condition"].lower() == "damaged"
            and not request["photo_evidence_available"]
        ):

            findings.append(
                "Damaged item without photos."
            )

        if (
            request["previous_returns_90_days"] >= 3
        ):

            findings.append(
                "Excessive previous returns."
            )

        status = (
            "ELIGIBLE"
            if len(findings) == 0
            else "REVIEW_REQUIRED"
        )

        return {
            "status": status,
            "findings": findings
        }


###############################################################################
# AGENT 2
# RISK AGENT
###############################################################################

class RiskAgent:

    def execute(self, request):

        findings = []

        risk = "LOW"

        if request["amount_inr"] >= 25000:

            risk = "HIGH"

            findings.append(
                "High-value request."
            )

        if request["previous_returns_90_days"] >= 3:

            risk = "HIGH"

            findings.append(
                "Frequent return behavior."
            )

        if (
            request["item_condition"].lower() == "damaged"
            and not request["photo_evidence_available"]
        ):

            findings.append(
                "Missing supporting photos."
            )

        if not request["invoice_available"]:

            findings.append(
                "Invoice unavailable."
            )

        if not findings:

            findings.append(
                "No significant risk detected."
            )

        return {
            "risk_level": risk,
            "assessment": findings
        }


###############################################################################
# AGENT 3
# RESPONSE AGENT
###############################################################################

class CustomerResponseAgent:

    def execute(
            self,
            request,
            decision
    ):

        if decision in [
            "AUTO_APPROVED",
            "MANAGER_APPROVED"
        ]:

            return (
                f"Dear Customer,\n\n"
                f"Your {request['request_type']} request for "
                f"{request['product']} "
                f"(Request ID {request['request_id']}) "
                f"has been approved for further processing.\n\n"
                f"Our team will perform final verification "
                f"before determining next steps.\n\n"
                f"This approval does not mean a refund "
                f"or replacement has already been completed."
            )

        return (
            f"Dear Customer,\n\n"
            f"After review, your request for "
            f"{request['product']} "
            f"(Request ID {request['request_id']}) "
            f"cannot be approved at this time.\n\n"
            f"No refund or replacement action "
            f"has been initiated."
        )


###############################################################################
# BUSINESS RULES
###############################################################################

def auto_approval_check(
        request,
        risk_result
):

    condition_rule = (

            request["item_condition"].lower()
            == "unopened"

            or

            (
                request["item_condition"].lower()
                == "damaged"
                and request["photo_evidence_available"]
            )
    )

    return all([

        request["amount_inr"] < 25000,

        request["days_since_delivery"] <= 30,

        request["invoice_available"],

        condition_rule,

        request["previous_returns_90_days"] < 3,

        risk_result["risk_level"] != "HIGH"
    ])


###############################################################################
# HUMAN REVIEW
###############################################################################

def human_review(
        request,
        eligibility,
        risk
):

    print("\n" + "=" * 80)
    print("WORKFLOW PAUSED")
    print("HUMAN REVIEW REQUIRED")
    print("=" * 80)

    print(
        f"Request ID : {request['request_id']}"
    )

    print(
        f"Product    : {request['product']}"
    )

    print(
        f"Amount     : ₹{request['amount_inr']}"
    )

    print("\nEligibility Findings")

    if eligibility["findings"]:

        for item in eligibility["findings"]:
            print("-", item)

    else:

        print("No findings")

    print("\nRisk Assessment")

    for item in risk["assessment"]:
        print("-", item)

    while True:

        decision = input(
            "\nEnter approve/reject : "
        ).strip()

        valid, msg = run_input_guardrails(
            decision
        )

        if not valid:

            print(msg)
            continue

        decision = decision.lower()

        if decision in [
            "approve",
            "reject"
        ]:

            print("\nWorkflow Resumed")

            return decision

        print(
            "Invalid input. "
            "Use approve or reject."
        )


###############################################################################
# APPROVAL GATEWAY
###############################################################################

class ApprovalGateway:

    def execute(
            self,
            request,
            eligibility,
            risk
    ):

        if auto_approval_check(
                request,
                risk
        ):

            return {
                "route": "Automatic",
                "decision": "AUTO_APPROVED"
            }

        decision = human_review(
            request,
            eligibility,
            risk
        )

        if decision == "approve":

            return {
                "route": "Human Review",
                "decision": "MANAGER_APPROVED"
            }

        return {
            "route": "Human Review",
            "decision": "MANAGER_REJECTED"
        }


###############################################################################
# WORKFLOW
###############################################################################

class ReturnWorkflow:

    def __init__(self):

        self.eligibility_agent = (
            EligibilityAgent()
        )

        self.risk_agent = (
            RiskAgent()
        )

        self.response_agent = (
            CustomerResponseAgent()
        )

        self.gateway = (
            ApprovalGateway()
        )

    def process_request(
            self,
            request
    ):

        reason = request.get(
            "return_reason",
            ""
        )

        if not validate_length(reason):

            return {
                "request_id":
                    request["request_id"],
                "error":
                    "Length validation failed"
            }

        if contains_pii(reason):

            return {
                "request_id":
                    request["request_id"],
                "error":
                    "PII detected"
            }

        if detect_prompt_injection(reason):

            return {
                "request_id":
                    request["request_id"],
                "error":
                    "Prompt injection detected"
            }

        if detect_sql_injection(reason):

            return {
                "request_id":
                    request["request_id"],
                "error":
                    "SQL injection detected"
            }

        if detect_xss(reason):

            return {
                "request_id":
                    request["request_id"],
                "error":
                    "XSS attack detected"
            }

        eligibility = (
            self.eligibility_agent.execute(
                request
            )
        )

        risk = (
            self.risk_agent.execute(
                request
            )
        )

        approval = (
            self.gateway.execute(
                request,
                eligibility,
                risk
            )
        )

        customer_message = (
            self.response_agent.execute(
                request,
                approval["decision"]
            )
        )

        if output_contains_sensitive_data(
                customer_message
        ):

            customer_message = (
                REFUSAL_MESSAGE
            )

        if not run_output_guardrails(
                customer_message
        ):

            customer_message = (
                REFUSAL_MESSAGE
            )

        final_state = WorkflowState(

            request_id=request["request_id"],

            order_id=request["order_id"],

            product=request["product"],

            product_category=request["product_category"],

            requested_amount=request["amount_inr"],

            eligibility_findings=eligibility,

            risk_assessment=risk,

            approval_route=
            approval["route"],

            final_decision=
            approval["decision"],

            customer_communication=
            customer_message
        )

        return asdict(final_state)


###############################################################################
# LOAD RETURNS
###############################################################################

def load_returns():

    with open(
        "returns.json",
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


###############################################################################
# MAIN
###############################################################################

def main():

    print(
        "\nRETURN MANAGEMENT WORKFLOW"
    )

    try:

        validate_configuration()

    except Exception as ex:

        print(
            "\nCONFIGURATION ERROR"
        )

        print(str(ex))

        return

    requests = load_returns()

    workflow = ReturnWorkflow()

    results = []

    for request in requests:

        print(
            f"\nProcessing "
            f"{request['request_id']}"
        )

        result = (
            workflow.process_request(
                request
            )
        )

        results.append(result)

        print(
            json.dumps(
                result,
                indent=4
            )
        )

    with open(
        "workflow_results.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            indent=4
        )

    print("\nworkflow_results.json generated")


if __name__ == "__main__":
    main()