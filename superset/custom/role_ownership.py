"""
Who owns an Insight Hub user's roles.

The rule jabberBrain runs on (Johan, 2026-08-20):

    Authentik owns identity and app access; jBKB owns role and assignment.

⛔ THIS IS PHASE 1 OF TWO, AND THE DISTINCTION MATTERS.

  * **Phase 1 (here).** Authentik stops OVERWRITING roles. It still SEEDS them:
    a user with nothing stored takes what the token offers, and after that the
    stored roles win.

  * **Phase 2 (later).** Authentik seeds nothing either, because jBKB creates
    the Superset account with its roles at Save. That is the rule at 100% —
    seeding still lets Authentik decide for anyone who signs in before jBKB has
    set a role, and it keeps the ``role/ih/*`` groups load-bearing when the
    whole point is retiring them.

Phase 2 waits on the Insight Hub role data being curated in jBKB and the
``role/ih/*`` groups being cleaned up in Authentik. Doing it first would leave
the **7 people who hold ``application/ih`` today and have never opened Insight
Hub** (audited 2026-08-21) landing on a Superset that shows them nothing.

## What phase 1 fixes

``auth_user_oauth`` did ``user.roles = [...token]``, unconditionally, on EVERY
login. Anything set in Superset's own Security screen was reverted the next time
that person signed in — and jBKB is about to start writing roles here.

AIM had the identical line until 2026-08-15 and it had to be watched happen in
production before anyone believed it: a role corrected at 18:00 was back to its
old value by 18:12, one login later. ``role-ownership.ts`` in AIM-backend is the
same decision in TypeScript.

## What it changes for real people — one person, checked

Audited against the live Superset database on 2026-08-21: every account's stored
roles already equal what the token would send, EXCEPT one. That user's Authentik
groups changed after her last login (2025-09-26), so today's build would
downgrade her at her next sign-in and this one will not. Everybody else is
unaffected, and nobody has opened Insight Hub since 2025-10-21.

Divergence is expected the moment an administrator changes a role, so it is
logged rather than treated as an error — it is information, not a fault.
"""

from __future__ import annotations

from typing import Iterable

#: The role FAB hands out on registration. Not a decision anyone made.
SEED_ROLE = "Public"


def decide_role_sync(
    stored_roles: Iterable[str],
    token_roles: Iterable[str],
) -> str:
    """Return ``"adopt"``, ``"keep"`` or ``"diverged"``.

    ``adopt``    — nothing meaningful stored yet; take what Authentik sent.
    ``keep``     — the two agree, or Authentik offered nothing. Do nothing.
    ``diverged`` — they disagree. The STORED roles win.

    Order is not significance: a user holding ``{Alpha, Gamma}`` is the same
    user whichever way the two systems happen to list them.
    """
    stored = {r for r in stored_roles if r}
    token = {r for r in token_roles if r}

    # ⛔ Authentik offered nothing. There is no such thing as "adopt nothing":
    # that would strip the user to zero roles, which is strictly worse than the
    # Public they were registered with, and it is what a missing property
    # mapping or a dropped scope looks like. Absence is not an instruction.
    if not token:
        return "keep"
    # ⛔ Public alone is not an assignment. `create_new_user` gives it to every
    # account it makes, so reading it as deliberate would mean Authentik's roles
    # were never adopted at all and every new user landed able to see nothing.
    if not stored or stored == {SEED_ROLE}:
        return "adopt"
    if stored == token:
        return "keep"
    return "diverged"
