from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src" / "axiom_tools"
VIEWS = SRC / "web" / "views"
TEMPLATES = SRC / "web" / "templates"
APP = SRC / "web" / "app.py"
MUTATING = {"POST", "PUT", "PATCH", "DELETE"}
VERBS = {"get":{"GET"},"post":{"POST"},"put":{"PUT"},"patch":{"PATCH"},"delete":{"DELETE"}}


def _routes():
    rows=[]
    for path in VIEWS.rglob("*.py"):
        tree=ast.parse(path.read_text(encoding="utf-8"))
        for node in tree.body:
            if not isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
                continue
            route=None; methods=None; decorators=[]
            for deco in node.decorator_list:
                decorators.append(ast.unparse(deco))
                if not (isinstance(deco,ast.Call) and isinstance(deco.func,ast.Attribute)):
                    continue
                name=deco.func.attr
                if name not in {*VERBS,"route"}:
                    continue
                if deco.args and isinstance(deco.args[0],ast.Constant):
                    route=str(deco.args[0].value)
                if name in VERBS:
                    methods=set(VERBS[name])
                else:
                    methods={"GET"}
                    for kw in deco.keywords:
                        if kw.arg=="methods" and isinstance(kw.value,(ast.List,ast.Tuple)):
                            methods={str(x.value).upper() for x in kw.value.elts if isinstance(x,ast.Constant)}
            if route is not None:
                rows.append({"file":path,"line":node.lineno,"fn":node.name,"route":route,"methods":methods or {"GET"},"decorators":decorators})
    return rows


def test_all_mutating_internal_routes_require_session_decorator():
    missing=[]; routes=_routes(); mutating=[r for r in routes if r["methods"] & MUTATING]
    assert len(routes) >= 182
    assert len(mutating) >= 125
    for row in mutating:
        if row["file"].name=="auth_views.py" and row["fn"] in {"login","logout"}:
            continue
        if not any("login_required" in d or "admin_required" in d for d in row["decorators"]):
            missing.append(f"{row['file'].name}:{row['line']} {row['route']}")
    assert missing == []


def test_csrf_is_global_and_has_no_exemptions():
    app=APP.read_text(encoding="utf-8")
    assert "csrf = CSRFProtect()" in app and "csrf.init_app(app)" in app
    hits=[]
    for path in SRC.rglob("*.py"):
        text=path.read_text(encoding="utf-8",errors="ignore")
        if "csrf.exempt" in text or "csrf_exempt" in text:
            hits.append(str(path.relative_to(ROOT)))
    assert hits == []


def test_all_post_forms_emit_csrf_token():
    missing=[]; total_post=0
    for path in TEMPLATES.rglob("*.html"):
        text=path.read_text(encoding="utf-8",errors="ignore")
        for match in re.finditer(r"<form\b[^>]*>",text,re.I):
            tag=match.group(0)
            meth=re.search(r"method\s*=\s*[\"']?([^\"'\s>]+)",tag,re.I)
            method=(meth.group(1).upper() if meth else "GET")
            if method!="POST":
                continue
            total_post += 1
            end=text.find("</form>",match.end())
            body=text[match.end():end if end!=-1 else min(len(text),match.end()+4000)]
            if "csrf_token" not in tag and "csrf_token" not in body:
                missing.append(f"{path.relative_to(ROOT)}:{text.count(chr(10),0,match.start())+1}")
    assert total_post >= 111
    assert missing == []


def test_auth_decorators_really_validate_session_and_admin_profile():
    source=(SRC/"web"/"auth"/"decorators.py").read_text(encoding="utf-8")
    assert 'session.get("usuario")' in source
    assert 'usuario.get("perfil") != "administrador"' in source
    assert "abort(403)" in source


def test_mutations_have_transversal_audit_with_request_correlation():
    app=APP.read_text(encoding="utf-8")
    assert "@app.after_request" in app
    assert "HTTP_MUTACAO_BLOQUEADA" in app
    assert 'request.method in {"POST", "PUT", "PATCH", "DELETE"}' in app
    assert "X-Axiom-Request-ID" in app and "campos_formulario" in app
    block=app[app.index("def _auditar_mutacao_http"):app.index('@app.get("/health")')]
    assert "request.form.to_dict" not in block
    assert "request.form.values" not in block
