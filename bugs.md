# Team Bug Tracker

This is our shared hackathon tracking board. Use it to avoid duplicate work, keep proof for every bug, and coordinate direct commits during the round.

Before changing this file:

```bash
git pull --rebase
```

After adding a claim, reproduction, fix note, verification result, or push note:

```bash
git add bugs.md
git commit -m "chore: update bug tracker"
git push
```

The final judge-facing explanation should go in `bug_report.md`. This file is our working board.

## Team Sync Rule

Every work block follows this cycle:

```bash
git pull --rebase
git status --short
# work on one bug claim, reproduction, fix, verification, or report update
git add <changed-files>
git commit -m "clear bug-specific message"
git pull --rebase
git push
```

For a new bug, push the `bugs.md` claim before working on the fix:

```bash
git pull --rebase
# add BUG-XXX to the Live Board
git add bugs.md
git commit -m "chore: claim BUG-XXX short area"
git pull --rebase
git push
```

If the second `git pull --rebase` creates conflicts, resolve them, rerun the focused verification if code changed, then push.

## Status Flow

```text
SUSPECTED -> CLAIMED -> REPRODUCED -> ROOT_CAUSED -> FIXING -> FIXED -> VERIFIED -> REPORTED
```

Other useful statuses:

```text
STALE
REJECTED
BLOCKED
PUSHED
```

## Live Board

| Bug ID | Status | Owner | Last Updated | Area / Workflow | Difficulty Guess | Commit(s) | Evidence |
|---|---|---|---|---|---|---|---|
| _None yet_ |  |  |  |  |  |  |  |

## Confirmed Fixes

| Bug ID | Root Cause | Fix Commit | Verification Command / Result | Verified By | Added To `bug_report.md` |
|---|---|---|---|---|---|
| _None yet_ |  |  |  |  |  |

## Push Log

Use this table to make direct pushes easy to follow. Add a row when a bug claim, reproduction, fix, verification, or report update is pushed.

| Time | Bug ID | Owner | Commit | Files Touched | Push Status | Notes |
|---|---|---|---|---|---|---|
| _None yet_ |  |  |  |  |  |  |

## Test Matrix

Adapt this table to the actual problem statement and repository.

| Area | Case | Result | Bug ID / Notes |
|---|---|---|---|
| Startup | App boots with documented command | Not tested | |
| Health/docs | Public status/docs route works if documented | Not tested | |
| Config/env | Required env vars and sample config work | Not tested | |
| Auth/session | Valid credentials or session flow works if applicable | Not tested | |
| Auth/session | Missing/invalid credentials fail correctly if applicable | Not tested | |
| Authorization | User/resource isolation is enforced if applicable | Not tested | |
| Core create/write | Documented create/write operation works | Not tested | |
| Core read/list | Documented read/list operation returns correct scope | Not tested | |
| Core update | Documented update operation persists correct data | Not tested | |
| Core delete/cleanup | Documented delete/cleanup operation affects only intended data | Not tested | |
| Validation | Missing/malformed input returns expected error | Not tested | |
| Error handling | Missing resource or invalid action returns expected error | Not tested | |
| Persistence | Data survives a new request/session when it should | Not tested | |
| Response shape | Output matches documented schema/format | Not tested | |
| Regression | Existing automated tests pass | Not tested | |

## Rejected Suspicions

| Suspicion | Why rejected | Checked by | Evidence |
|---|---|---|---|
| _None yet_ |  |  |  |

## Bug Detail Entries

Add a new entry below for each reproduced bug. Keep the details practical: what we did, what failed, where the bug lives, and how we proved the fix.

### BUG-XXX - Short title

Status:
Owner:
Last updated:
Difficulty guess:
Area / workflow:
Commit(s):

#### Setup data

```bash
# setup commands or notes
```

#### Reproduction

```bash
# request, command, or manual steps
```

#### Expected behavior

```text

```

#### Actual behavior before fix

```text

```

#### Why this is wrong


#### Suspected or confirmed file/line

- `path/to/file.ext:Lx`

#### Root cause


#### Fix summary


#### Verification after fix

```bash
# verification command
```

Result:

```text

```
