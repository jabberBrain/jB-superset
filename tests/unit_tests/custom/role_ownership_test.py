"""
Authentik seeds Insight Hub roles; Superset keeps them.

⛔ The case worth pinning is the SECOND LOGIN. The defect this replaces was not
visible on login one — Authentik's roles were applied and everything looked
right. It showed up when someone changed a role and the next sign-in put it
back. So every test here is really the same question asked twice: what happens
when the token and the database disagree?

Checked against the live Superset database on 2026-08-21: every account's stored
roles already equal what the token sends, except one user whose Authentik groups
changed after her last login. She is the only person this deploy moves, and it
moves her by leaving her alone.
"""

import pytest

from superset.custom.role_ownership import decide_role_sync


def test_a_brand_new_user_takes_authentiks_roles():
    assert decide_role_sync([], ["Alpha"]) == "adopt"


def test_public_alone_is_not_an_assignment():
    # ⛔ create_new_user gives every account Public, so nobody is ever literally
    # role-less. Reading that as a deliberate choice would mean Authentik's
    # roles were never adopted and new users landed able to see nothing.
    assert decide_role_sync(["Public"], ["Alpha"]) == "adopt"


def test_public_alongside_a_real_role_is_an_assignment():
    assert decide_role_sync(["Public", "Alpha"], ["Gamma"]) == "diverged"


def test_agreement_is_a_no_op():
    assert decide_role_sync(["Advanced"], ["Advanced"]) == "keep"


def test_order_is_not_significance():
    # Same user either way. Authentik and Superset have no reason to agree on
    # the order of a set, and a false "diverged" would spam the log forever.
    assert decide_role_sync(["Admin", "Advanced"], ["Advanced", "Admin"]) == "keep"


def test_the_stored_roles_win_when_they_disagree():
    # The real row, from the 2026-08-21 audit: Authentik says builder +
    # jb_supervisor, Superset stores Admin + Advanced, because her groups
    # changed after her last login. Today's build would downgrade her at the
    # next sign-in. This one leaves her as she is.
    assert decide_role_sync(["Admin", "Advanced"], ["Builder", "jb_supervisor"]) == "diverged"


@pytest.mark.parametrize("token", [[], [""], None])
def test_an_empty_token_never_strips_a_user(token):
    # ⛔ A missing property mapping or a dropped scope looks exactly like this.
    # "Adopt nothing" would leave the user with zero roles — strictly worse than
    # the Public they registered with. Absence is not an instruction.
    assert decide_role_sync(["Admin"], token or []) == "keep"
    assert decide_role_sync([], token or []) == "keep"
