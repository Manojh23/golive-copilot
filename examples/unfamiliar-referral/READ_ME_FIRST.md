# Unfamiliar referral-workflow test

All documents are newly constructed fictional test material, not real hospital operating procedures or vendor specifications. They test document comparison, not clinical effectiveness. This example is separate from the original EarlyWatch scenario rules. No live Gemini evaluation has been performed on these files here.

## Prepare once

Keep the local app running with npm run dev. Extract this ZIP into Downloads. In a second Kiro terminal run:

```bash
python3 ~/Downloads/Unfamiliar_Referral_Test/prepare_workspace.py
```

This uses only Python's standard library to update the local workspace's fictional baseline assumptions and avoid importing old EarlyWatch gaps into the test. It saves the old name, owner and checks beside the script, and marks previous approvals stale. It does not delete sources or feedback, upload files, or call Gemini. It assumes the original four-app inventory (CareRecord, LabBridge, TeamInbox, FollowTrack) remains installed in the demo. If you changed that inventory, align it with 01_current_workflow.txt in workspace settings first.

## First run: upload only 01 and 02

1. Click Add document.
2. Set Document role to Replace current-workflow description.
3. Select 01_current_workflow.txt, then click Index document.
4. Click Add document again.
5. Set Document role to Replace proposed-app guide.
6. Select 02_ReferralBridge_v1.txt, then click Index document.
7. Enable Live LLM, and click Re-run review (or Run impact review on Overview).

Do not choose Supporting reference for either file. Do not upload the ZIP, this README, the script, the backup, or every app version together. Uploading alone does not run analysis.

## Reviewer expectations - do not upload these answers

- Version 1: Flag a potential mismatch between closing upon message acknowledgement and the hospital's requirement to wait for appointment confirmation. Cite both documents. Sending/receiving a referral is different from booking an appointment. Do not claim any actual patient missed a visit.
- Version 2: Upload only 03_ReferralBridge_v2.txt as Replace proposed-app guide, leaving 01 active, and rerun. The specific early-closure mismatch should no longer appear because this guide explicitly waits for appointment confirmation. Findings about version 1 must not be presented as current facts. Zero total findings is not required; independently assess any other proposals.
- Version 3: Upload only 04_ReferralBridge_v3.txt as Replace proposed-app guide and rerun. The guide does not establish a case-closure trigger. If discussed, this should be labeled unknown or a request for clarification, not a proven early-closure conflict and not proof that behavior is correct.

Use the Impact review screen for version comparisons. General Evidence-library search can retrieve historical source snapshots as well as active ones, so inspect version attribution when asking library questions.

## Check the result

Read both cited passages. Confirm that the interpretation follows from them. Check roles and product versions. Export the assessment JSON if needed: custom findings should have origin llm_proposal, not scenario_rule. The original 8/8 rule-engine benchmark should not apply to these replacement documents.

Record actual outputs, mistakes, latency and whether the three expected behaviors occurred. A passing toy example is a smoke test, not a general accuracy score or proof of real hospital usefulness. The script sets synthetic readiness assumptions for isolation; it is not a real approval or validation record.
