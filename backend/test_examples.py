"""
Example inputs taken from a library's own test suite.

Every open-source library in research_projects ships with tests written by its
developers, e.g. `assert util.is_timestamp(1565358758)`. Calls like that are the
best possible example inputs: real values chosen by people who know the code.

We parse each library's tests/ folder once, remember every call whose arguments
are plain literals (numbers, text, lists, dicts, True/False/None), and later use
them to pre-fill the Function Runner.
"""

import ast
import json
import warnings
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

MAX_PER_NAME = 30
MAX_FILE_BYTES = 1_500_000


def _literal(node: ast.AST):
    """(ok, value) — value must be a JSON-friendly literal."""
    try:
        value = ast.literal_eval(node)
    except Exception:
        return False, None
    if isinstance(value, bytes):
        try:
            value = value.decode("utf-8")
        except UnicodeDecodeError:
            return False, None
    if isinstance(value, (tuple, set, frozenset)):
        value = list(value)
    try:
        json.dumps(value)
    except (TypeError, ValueError):
        return False, None
    return True, value


def _dotted(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        inner = _dotted(node.value)
        return f"{inner}.{node.attr}" if inner else node.attr
    return ""


def _parametrize_env(func: ast.AST) -> Dict[str, Any]:
    """Values for names bound by @pytest.mark.parametrize (first fully-literal row)."""
    env: Dict[str, Any] = {}
    for deco in getattr(func, "decorator_list", []):
        if not (isinstance(deco, ast.Call) and _dotted(deco.func).endswith("parametrize") and len(deco.args) >= 2):
            continue
        ok, names = _literal(deco.args[0])
        if not ok:
            continue
        if isinstance(names, str):
            names = [n.strip() for n in names.split(",") if n.strip()]
        rows = deco.args[1]
        if not isinstance(rows, (ast.List, ast.Tuple)):
            continue
        for row in rows.elts:
            # pytest.param(a, b, id=...) -> its positional args
            if isinstance(row, ast.Call) and _dotted(row.func).endswith("param"):
                row = ast.Tuple(elts=row.args, ctx=ast.Load())
            elts = row.elts if (len(names) > 1 and isinstance(row, (ast.Tuple, ast.List))) else [row]
            if len(elts) != len(names):
                continue
            values = [_literal(e) for e in elts]
            if all(good for good, _ in values):
                for n, (_, v) in zip(names, values):
                    env.setdefault(n, v)
                break
    return env


def _local_env(func: ast.AST) -> Dict[str, Any]:
    """`x = <literal>` assignments inside a test (first one wins)."""
    env: Dict[str, Any] = {}
    for node in ast.walk(func):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            good, v = _literal(node.value)
            if good:
                env.setdefault(node.targets[0].id, v)
    return env


def _negative_context(node: ast.AST, parents: Dict[ast.AST, ast.AST]) -> bool:
    """Is this call checking a *wrong* input? (assert not f(x), with pytest.raises: f(x))"""
    cur = node
    while cur in parents:
        par = parents[cur]
        if isinstance(par, ast.UnaryOp) and isinstance(par.op, ast.Not):
            return True
        if isinstance(par, ast.Compare) and any(
                isinstance(c, ast.Constant) and c.value in (False, None) for c in par.comparators):
            return True
        if isinstance(par, (ast.With, ast.AsyncWith)) and any(
                "raises" in _dotted(i.context_expr.func if isinstance(i.context_expr, ast.Call) else i.context_expr)
                or "warns" in _dotted(i.context_expr.func if isinstance(i.context_expr, ast.Call) else i.context_expr)
                for i in par.items):
            return True
        if isinstance(par, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return False
        cur = par
    return False


def _value(node: ast.AST, env: Dict[str, Any]):
    if isinstance(node, ast.Name) and node.id in env:
        return True, env[node.id]
    return _literal(node)


@lru_cache(maxsize=None)
def build_index(tests_dir: str) -> Dict[str, List[Dict[str, Any]]]:
    """function name -> literal calls found in the tests."""
    index: Dict[str, List[Dict[str, Any]]] = {}
    root = Path(tests_dir)
    if not root.exists():
        return index
    for path in sorted(root.rglob("*.py")):
        try:
            if path.stat().st_size > MAX_FILE_BYTES:
                continue
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        except (SyntaxError, ValueError, OSError):
            continue
        parents = {child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
        # each test function gets its own name -> value environment
        scopes = [tree] + [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        seen = set()
        for scope in reversed(scopes):          # innermost functions first
            env = {} if scope is tree else {**_local_env(scope), **_parametrize_env(scope)}
            for node in ast.walk(scope):
                if not isinstance(node, ast.Call) or id(node) in seen:
                    continue
                seen.add(id(node))
                func = node.func
                if isinstance(func, ast.Name):
                    name, qualifier = func.id, ""
                elif isinstance(func, ast.Attribute):
                    name, qualifier = func.attr, _dotted(func.value)
                else:
                    continue
                if any(isinstance(a, ast.Starred) for a in node.args) or any(k.arg is None for k in node.keywords):
                    continue
                vals = [_value(a, env) for a in node.args]
                kvals = {k.arg: _value(k.value, env) for k in node.keywords}
                if not all(g for g, _ in vals) or not all(g for g, _ in kvals.values()):
                    continue
                args = [v for _, v in vals]
                kwargs = {k: v for k, (_, v) in kvals.items()}
                if not args and not kwargs:
                    continue
                bucket = index.setdefault(name, [])
                if len(bucket) < MAX_PER_NAME:
                    bucket.append({
                        "args": args,
                        "kwargs": kwargs,
                        "qualifier": qualifier,
                        "negative": _negative_context(node, parents),
                        "where": f"{path.relative_to(root.parent).as_posix()}:{node.lineno}",
                    })
    return index


_KIND_CHECK = {
    "string": lambda v: isinstance(v, str),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "bool":   lambda v: isinstance(v, bool),
    "list":   lambda v: isinstance(v, list),
    "dict":   lambda v: isinstance(v, dict),
    "record": lambda v: isinstance(v, dict),
}


def _fits(p: Dict[str, Any], value: Any) -> bool:
    check = _KIND_CHECK.get(p["type"])
    if check is None:                 # any / object / null: accept, unless it needs a real object
        return p.get("json_ok", True) or value is not None
    if value is None:
        return "None" in (p.get("annotation") or "") or p.get("default") == "None"
    return check(value)


def _match(call: Dict[str, Any], params: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Map a recorded call onto the function's parameters; None if it doesn't fit."""
    positional = [p for p in params if p["kind"] in ("positional_only", "positional")]
    has_varargs = any(p["kind"] == "var_positional" for p in params)
    has_varkw = any(p["kind"] == "var_keyword" for p in params)
    by_name = {p["name"]: p for p in params if p["kind"] not in ("var_positional", "var_keyword")}

    if len(call["args"]) > len(positional) and not has_varargs:
        return None
    mapping: Dict[str, Any] = {}
    for p, v in zip(positional, call["args"]):
        if not _fits(p, v):
            return None
        mapping[p["name"]] = v
    for k, v in call["kwargs"].items():
        if k in mapping:
            return None
        if k in by_name:
            if not _fits(by_name[k], v):
                return None
            mapping[k] = v
        elif not has_varkw:
            return None
    for p in params:
        if p["required"] and p["name"] not in mapping:
            return None
    return mapping


def apply_test_examples(project_root: Path, packages: List[str], module: str,
                        qualname: str, params: List[Dict[str, Any]]) -> Optional[str]:
    """Overwrite example values in `params` with ones from the library's tests.
    Returns where the example was found (e.g. "tests/test_util.py:42") or None."""
    index = build_index(str(project_root / "tests"))
    name = qualname.split(".")[-1]
    calls = index.get(name)
    if not calls:
        return None
    module_tail = module.split(".")[-1]
    owner = qualname.split(".")[0] if "." in qualname else ""

    best, best_score = None, -1
    from_tests: Dict[str, List[Any]] = {}      # param -> distinct values seen in the tests
    for call in calls:
        if call.get("negative"):
            continue          # deliberately wrong input (assert not f(x) / pytest.raises)
        mapping = _match(call, params)
        if mapping is None:
            continue
        for k, v in mapping.items():
            vals = from_tests.setdefault(k, [])
            if v not in vals and len(vals) < 6:
                vals.append(v)
        q = call["qualifier"]
        score = 0
        if owner and q.split(".")[-1] == owner:
            score += 3
        if q and (q.split(".")[-1] == module_tail or q.split(".")[0] in packages):
            score += 2
        if not q and not owner:
            score += 1
        text = json.dumps(mapping)
        score += 0.5 if text.isascii() else 0
        if score > best_score:
            best, best_score = (call, mapping), score
    if best is None:
        return None
    # a bare `name(...)` call could be some other function with the same name: only trust
    # it for names that are specific enough
    call, mapping = best
    if best_score <= 0.5 and (len(name) < 6 or name.startswith("_")):
        return None
    # put the values used in the tests at the top of each dropdown
    for p in params:
        tested = from_tests.get(p["name"], [])
        if tested:
            extra = [{"value": json.dumps(v, ensure_ascii=False), "note": "from the library's tests"} for v in tested]
            known = {e["value"] for e in extra}
            p["suggestions"] = (extra + [x for x in p.get("suggestions", []) if x["value"] not in known])[:10]
    for p in params:
        if p["name"] in mapping:
            v = mapping[p["name"]]
            p["example"] = v
            p["example_json"] = json.dumps(v, ensure_ascii=False)
            p["source"] = "library tests"
        if p["kind"] == "var_positional":
            n_pos = len([q for q in params if q["kind"] in ("positional_only", "positional")])
            extra = call["args"][n_pos:]
            if extra:
                p["example"], p["example_json"], p["source"] = extra, json.dumps(extra), "library tests"
        if p["kind"] == "var_keyword":
            named = {q["name"] for q in params}
            extra_kw = {k: v for k, v in call["kwargs"].items() if k not in named}
            if extra_kw:
                p["example"], p["example_json"], p["source"] = extra_kw, json.dumps(extra_kw), "library tests"
    return call["where"]
