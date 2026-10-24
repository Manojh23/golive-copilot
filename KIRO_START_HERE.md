> For the updated submission workflow, start with **KIRO_NEXT_STEPS.md** and **UPDATE_EXISTING_PROJECT.md**. The original continuation notes below are retained.

# Open this project in Kiro

1. Extract the project ZIP. In Kiro choose **Open Folder** and select the folder containing `package.json`, `backend/`, and `.kiro/`. If merging into your existing hackathon repository, copy the folder contents including `.kiro/`; retain your existing `.git` directory and do not copy a `.env` from anyone else.
2. Trust only your own extracted project folder. Open Kiro Terminal and run:

```bash
bash scripts/setup.sh
npm run dev
```

3. Visit http://localhost:8000. Start with the disclosed demo. Add your key to `.env` if you want live generation and restart the backend.
4. Give Kiro this concrete task:

> Read `.kiro/steering/` and `.kiro/specs/golive-impact/` completely. This is the GoLive Impact Copilot hackathon project. Run the existing build and tests, then independently review the document-to-finding path: active source selection, citation validation, product/version attribution, custom-app isolation, and stale approvals. Fix any issue you reproduce. Implement a source-snapshot comparison view that shows added and removed source passages with their location, preserving earlier evidence, and add a meaningful test. Verify the actual application in my browser. Keep synthetic material clearly labeled, do not add patient data, and never claim provider connectivity without testing it. Record the exact work and actual results in `KIRO_USAGE.md`. Preserve `.kiro/` in Git.

5. Use Kiro to perform actual development and verification. Generated specs alone do not meet the event's material-use requirement. The source prepared here was not developed inside your Kiro session.
6. Before submission: verify Git remote, remove secrets, include `.kiro/`, make the intended repository public, and follow the event's actual submission form. The supplied brief requires a public video shorter than three minutes.

## Demo narration (target 2:30)

- 0:00–0:20: A new hospital app changes staff tasks and handoffs. Introduce the clinical rollout reviewer.
- 0:20–0:55: Run the review, open one evidence-linked finding, assign an owner.
- 0:55–1:20: Approve content and export the nurse brief/checklist.
- 1:20–1:50: Load labeled synthetic check-ins, group them, and inspect a suggested relationship to an earlier concern.
- 1:50–2:10: Change a requirement and show that the assessment must be refreshed.
- 2:10–2:30: Show real public hospital aggregates, describe data boundaries, and explain only the Kiro features actually used.
