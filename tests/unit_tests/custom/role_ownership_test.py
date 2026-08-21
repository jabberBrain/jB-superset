"""
The OAuth token must never write a user's roles.

⛔ THIS IS A STRUCTURAL TEST ON PURPOSE, and it is the only kind that can catch
this regression. The defect it guards is one line —

    user.roles = [role for role in (...userinfo["roles"]) if role]

— sitting in ``auth_user_oauth``, and it is INVISIBLE at first login: Authentik's
roles get applied and everything looks right. It only shows on the SECOND login,
when a role set from jBKB is quietly reverted. AIM had the identical line and it
had to be watched happen in production before anyone believed it (a role
corrected at 18:00 was back by 18:12).

A behavioural test would need a Flask app, a database and a security manager
just to assert that nothing happened. Reading the AST is direct: whatever else
that method does, it does not assign to ``user.roles``.

Authentik owns identity and app access; jBKB owns role and assignment. Roles are
written through Superset's security API, by jBKB, and by nothing else.
"""

import ast
import pathlib

SECURITY_PY = pathlib.Path(__file__).parents[3] / "superset" / "custom" / "security.py"


def _method(name: str) -> ast.FunctionDef:
    tree = ast.parse(SECURITY_PY.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"{name} is gone from CustomSecurityManager")


def _assigned_attributes(fn: ast.FunctionDef) -> set:
    """Every ``something.attr`` this method writes to."""
    out = set()
    for node in ast.walk(fn):
        targets = []
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, (ast.AugAssign, ast.AnnAssign)):
            targets = [node.target]
        for t in targets:
            if isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name):
                out.add(f"{t.value.id}.{t.attr}")
    return out


def test_the_token_does_not_write_roles():
    assert "user.roles" not in _assigned_attributes(_method("auth_user_oauth"))


def test_the_token_still_writes_identity_and_access_scope():
    # The counterpart. Authentik DOES own these — name and email are identity,
    # solution_uuid is the VA access scope — so an over-eager fix that stopped
    # the method writing anything at all would be just as wrong, and this test
    # would go red instead of passing quietly.
    written = _assigned_attributes(_method("auth_user_oauth"))
    assert {"user.email", "user.first_name", "user.last_name", "user.solution_uuid"} <= written


def test_a_self_registered_user_still_lands_somewhere_defined():
    # Superset self-creates an account for anyone with application/ih access who
    # signs in before jBKB provisioned them. They must get Public rather than
    # nothing — an account with zero roles cannot even render the landing page.
    assert "Public" in ast.unparse(_method("create_new_user"))
