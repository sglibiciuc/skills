# Obstacles and changes

Rules for an obstacle, a changed requirement, and a task that changes or stops.

- An obstacle that does not go away: one stop with a question in plain words, and options with a recommendation: narrow the task, change the source, stop the work. "Narrow" or "change" goes into a new PRD version and the work continues. On "stop", one message: what is built and works, what is not and why. Then run `resume.py --deactivate`.
- If the work stopped for something the person gives (an access key), nothing is deleted.
- If the task changes or stops for good, propose to remove the temporary material of the earlier work (by `created.md`). Only after the person agrees, the executor removes it (job "cleanup").
- The person changes a requirement mid-build: finish the current block, clarify the change, recommend by size: "now" if it does not touch what is built, "later" if it does. The person chooses.
  - "Now": one message with what changes in the PRD and which built blocks are affected. The person confirms a new PRD version (the old one stays), and the composer rewrites the affected part of the spec (job "rewrite"). Nothing built changes without a new PRD version.
  - "Later": finish by the approved PRD. Write the change into `interview.md` marked `TO BACKLOG`, so the executor carries it into the backlog at the final. It is done later as improvement.
