import time

from json_logic import jsonLogic

# Add a new workflow definition//Can use json as above
# Use jsonLogic data convention
budgetApprovalWorkflow = {
    "workflow": {
        "formValidation": {
            "desc": "Validation of form input",  # For front end display/user information
            "operation": {
                "type": "ACTOR-INPUT-BASED",  # Can only be "ACTOR-INPUT-BASED" or "DATA-LOGIC-BASED"
                "actor": "HR-AGENT1",  # Should be a predefined role (possibly with name and email id)
                "nextStep": {"if": [
                    {"==": [{"var": "stepInput"}, "Approved"]}, "budgetApproverDetermination",
                    {"==": [{"var": "stepInput"}, "ReviewInput"]}, "crossCheckUserInput",
                    "__TERMINATE__"  # Ensure step name from front end/API should not being with double underscores
                    # If nextStep cannot be identified, the workflow is deemed to be ABORTED.
                    # There has to be an explicit __TERMINATE__ step for any branch
                    # or step has to be marked with isTerminal attribute set to true
                ]}
            }
        },
        "budgetApproverDetermination": {
            "desc": "Determine which department head approves the budget",
            "operation": {
                "type": "DATA-LOGIC-BASED",
                "nextStep": {"if": [
                    {">": [{"var": "proposedAmount"}, 10000]}, "ceoApproval",
                    {">": [{"var": "proposedAmount"}, 5000]}, "managerApproval",
                    "hrApproval"
                ]}
            }
        },
        "crossCheckUserInput": {
            "desc": "Field agent to review user input",
            "operation": {
                "type": "ACTOR-INPUT-BASED",
                "actor": "FIELD-AGENT1",
                "nextStep": {"if": [
                    {"==": [{"var": "stepInput"}, "Approved"]}, "formValidation",
                    "__TERMINATE__"
                ]}
            }
        },
        "ceoApproval": {
            "desc": "Get CEO Approval",
            "operation": {
                "type": "ACTOR-INPUT-BASED",
                "actor": "CEO",
                "nextStep": "__TERMINATE__"  # This will return __TERMINATE__ on jsonLogic.apply
            }
        },
        "managerApproval": {
            "desc": "Get Manager Approval",
            "operation": {
                "type": "ACTOR-INPUT-BASED",
                "actor": "MANAGER",
                "nextStep": "__TERMINATE__"
            }
        },
        "hrApproval": {
            "desc": "Get HR head approval",
            "operation": {
                "type": "ACTOR-INPUT-BASED",  # In the corresponding workflow instance, a boolean will track whether
                # user-input was received or not
                "actor": "HR-HEAD",
                "nextStep": "__TERMINATE__"
            }
        }
    },
    "firstStep": "formValidation"
}

# Workflow stages can only be IN-PROGRESS, ABORTED,
# or COMPLETED (on finding a __TERMINATE__ instruction).
# It doesn't have SUCCESS/FAILURE

# New form definition.
# Use Json schema
budgetRequisitionFormDefinition = {
    "type": "object",
    "properties":
        {
            "name": {"type": "string"},
            "proposedAmount": {"type": "number", "minimum": 0},
            "desc": {"type": "string"}
        }
}

# Roles
roles = {
    "HR-AGENT1": {
        "name": "HR Agent",
        "email": "hragent@org.com"},
    "FIELD-AGENT1": {
        "name": "Field Agent",
        "email": "fieldagent@org.com"},
    "CEO": {
        "name": "Ceo",
        "email": "ceo@org.com"},
    "MANAGER": {
        "name": "Manager",
        "email": "manager@org.com"},
    "HR-HEAD": {
        "name": "HR Head",
        "email": "hrhead@org.com"
    }}


# Engine Definition
def startWorkflow(formData, workflowDefinition, associatedRoles):
    workflowComptionStatus = "Completed successfully"
    nextStep = workflowDefinition["firstStep"]
    print("Workflow initiated for form <<{}>> with first step <<{}>>".format(formData, nextStep), end="\n=====\n\n")
    while nextStep != "__TERMINATE__":
        if nextStep is None:
            workflowComptionStatus = "Aborted"
            break
        nextStep, stepCompleted = executeWorkflowStep(formData, workflowDefinition["workflow"][nextStep], associatedRoles)
    print("Workflow {}".format(workflowComptionStatus), end="\n=====\n\n\n\n")


def executeWorkflowStep(formData, step, associatedRoles):
    time.sleep(1)
    print("   ** Executing: <<{}>> with next step defined as {}"
          .format(step['desc'], step['operation']['nextStep']), end="\n\n")
    jsonLogicData = formData
    if step['operation']['type'] == "ACTOR-INPUT-BASED":
        print("   Notified <<{}>> for input.".format(associatedRoles[step['operation']['actor']]['email']))
        userInput = input("   Please provide input for this step:  ")
        jsonLogicData = {"stepInput": userInput}
        print("   Step actions captured: {}".format(jsonLogicData), end="\n\n")
    nextStep = jsonLogic(step['operation']['nextStep'], jsonLogicData)
    print("   Next step to execute: {}".format(nextStep), end="\n\n")
    return nextStep, True


# Workflow executions


# Execute workflow for a form that requires CEO approval
# Save form data
print("Workflow with CEO approval")
newEmpBudgetRequisitionForm = {
    "name": "Emp Name",
    "proposedAmount": 50000,
    "desc": "new emp onboarding"
}
startWorkflow(newEmpBudgetRequisitionForm, budgetApprovalWorkflow, roles)

# Execute workflow for a form that requires Manager approval
print("Workflow with Manager approval")
newEmpBudgetRequisitionFormWithManagerApproval = {
    "name": "Emp Name",
    "proposedAmount": 6000,
    "desc": "new emp onboarding"
}
startWorkflow(newEmpBudgetRequisitionFormWithManagerApproval, budgetApprovalWorkflow, roles)

# Execute workflow for a form that requires HR approval
print("Workflow with HR approval")
newEmpBudgetRequisitionFormWithHRApproval = {
    "name": "Emp Name",
    "proposedAmount": 400,
    "desc": "new emp onboarding"
}
startWorkflow(newEmpBudgetRequisitionFormWithHRApproval, budgetApprovalWorkflow, roles)

# TODO
# Validate workflow definition - check if all branches have definite termination

# TODO
# Validate if all referenced fields are there in the form //might not be required as they can be handled by null

# TODO
# Create a form in UI/Front end and send to backend that form as json which confirms to the defined schema

# TODO
# Role definition and attributes required for roles

# TODO
# Capture all print statements as part of audit/workflow

# TODO
# Define role hierarchy

# TODO
# Multi-input flow definitions
