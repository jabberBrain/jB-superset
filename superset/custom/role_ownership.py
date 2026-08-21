"""
Who owns an Insight Hub user's roles. Short answer: not Authentik.

    Authentik owns identity and app access; jBKB owns role and assignment.

⛔ PHASE 2 OF TWO. Phase 1 (``ih-stop-overwrite``) stopped Authentik OVERWRITING
roles on every login but let it still SEED them. This removes the seed, which is
the difference between 90% of the rule and 100% of it: seeding still lets
Authentik decide the role of anyone who signs in before jBKB has set one, and it
keeps the ``role/ih/*`` groups load-bearing — the very groups being retired, one
user at a time, by ``convertToDirectAccess``.

So the OAuth token contributes identity (name, email) and access scope
(``solution_uuid``, from ``virtual_assistants``). It contributes NOTHING to
roles, ever.

## ⛔ Do not merge this before the prerequisites

Audited 2026-08-21: **7 people hold ``application/ih`` and have never opened
Insight Hub**. Under phase 1 they get their ``role/ih/advanced`` role at first
login. Without the seed they arrive with the bare ``Public`` that
``create_new_user`` hands out, and see nothing.

That gap is closed on the OTHER side, not here: jBKB creates the Superset
account WITH its roles, via ``POST /api/v1/security/users/`` (knowledge_builder
``services/superset-client.ts``, ``docs/user-provisioning.md`` §9) — the same
way it already creates AIM users. So this branch is safe to merge only once:

  1. jBKB has the Insight Hub service account configured and working, and
  2. the Insight Hub role data has been curated in jBKB, and
  3. the ``role/ih/*`` groups have been cleaned up in Authentik.

Anyone left over after that — access granted, never signed in, never provisioned
by jBKB — shows in the jBKB Users list as Insight Hub access with no role.
Visible and fixable beats silently decided elsewhere.
"""

from __future__ import annotations

#: The role FAB hands out on registration. Not a decision anyone made, and the
#: reason "has a role" is not the same question as "has roles beyond Public".
SEED_ROLE = "Public"
