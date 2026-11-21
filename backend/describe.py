"""
Plain-English "what does this function do" for the Function Runner.

For every function we build:
  summary   one or two sentences: the cleaned-up docstring, or (for library
            functions without a docstring) a hand-written description from
            function_descriptions.json
  returns   what you get back, in simple words
  outcomes  the possible results, read from the `return` statements
            (e.g. (True, "Account created") / (False, "Account already exists"))
  raises    errors the function raises on purpose, with their message
"""

import ast
import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

_DESC_FILE = Path(__file__).parent / "function_descriptions.json"

# docstring sections that are not part of the summary
_SECTION = re.compile(
    r"^\s*(Args|Arguments|Parameters|Params|Returns?|Yields?|Raises|Example|Examples|Note|Notes|"
    r"Attributes|Usage|See Also|Warning|Warnings|Todo)\s*:?\s*$|^\s*(:param|:type|:return|:rtype|:raises|"
    r"\.\. |>>>|!!!|```|-{3,}|={3,})",
    re.IGNORECASE)


@lru_cache(maxsize=1)
def _written() -> Dict[str, str]:
    try:
        return json.loads(_DESC_FILE.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def clean_docstring(doc: str) -> str:
    """First paragraph of a docstring, without Sphinx / Markdown markup."""
    lines = []
    for line in doc.strip().splitlines():
        if _SECTION.match(line):
            break
        if not line.strip():
            if lines:
                break
            continue
        lines.append(line.strip())
    text = " ".join(lines)
    text = re.sub(r":[a-z]+:`~?(?:[\w.]+\.)?([^`<]+?)(?:\s*<[^>]+>)?`", r"\1", text)   # :class:`~a.b.C` -> C
    text = re.sub(r"\[([^\]]+)\]\[[^\]]*\]", r"\1", text)                                # [text][ref] -> text
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)                                 # [text](url) -> text
    text = text.replace("``", "").replace("`", "").replace("**", "")
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > 400:
        text = text[:400].rsplit(" ", 1)[0] + "…"
    return text


# ─── Reading the code ────────────────────────────────────────

def _own_nodes(func: ast.AST):
    """Nodes of `func` itself, not of functions/classes nested inside it."""
    stack = list(ast.iter_child_nodes(func))
    while stack:
        node = stack.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            continue
        yield node
        stack.extend(ast.iter_child_nodes(node))


def _text(node: ast.AST) -> Optional[str]:
    """Readable text for a string constant or f-string ({var} kept as a placeholder)."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        parts = []
        for v in node.values:
            if isinstance(v, ast.Constant):
                parts.append(str(v.value))
            elif isinstance(v, ast.FormattedValue):
                expr = ast.unparse(v.value)
                parts.append("{" + expr + "}" if expr.isidentifier() else "…")
        return "".join(parts)
    return None


_ANN_WORDS = {
    "bool": "true or false", "str": "text", "int": "a whole number", "float": "a number",
    "list": "a list", "List": "a list", "dict": "a dictionary", "Dict": "a dictionary",
    "tuple": "a tuple (several values together)", "Tuple": "a tuple (several values together)",
    "set": "a set", "None": "nothing (None)", "bytes": "bytes", "Any": "any value",
    "Iterator": "values one by one (an iterator)", "Iterable": "a sequence of values",
    "Generator": "values one by one (a generator)", "Sequence": "a list", "Optional": "",
}


def _annotation_words(ann: str) -> str:
    ann = ann.strip().strip("'\"")
    parts = [p.strip() for p in re.split(r"\|", ann)]
    if len(parts) > 1:
        words = [_annotation_words(p) for p in parts]
        return " or ".join(dict.fromkeys(w for w in words if w))
    m = re.match(r"^(?:t\.|typing\.)?(\w+)(?:\[(.*)\])?$", ann)
    if not m:
        return ann
    base, inner = m.group(1), m.group(2)
    if base == "Optional" and inner:
        return _annotation_words(inner) + " or nothing (None)"
    if base == "Union" and inner:
        return " or ".join(dict.fromkeys(_annotation_words(p) for p in inner.split(",")))
    if base == "Literal" and inner:
        return "one of: " + inner
    if base in _ANN_WORDS:
        return _ANN_WORDS[base]
    return f"a {base} object"


def _returns_from_code(returns: List[ast.AST]) -> Optional[str]:
    vals = [r.value for r in returns]
    if not vals or all(v is None or (isinstance(v, ast.Constant) and v.value is None) for v in vals):
        return "nothing (None) — it changes the data you pass in" if vals else None

    def kind(v):
        if v is None or (isinstance(v, ast.Constant) and v.value is None):
            return "nothing (None)"
        if isinstance(v, ast.Constant):
            return {bool: "true or false", str: "text", int: "a number", float: "a number"}.get(type(v.value), "a value")
        if isinstance(v, (ast.Compare, ast.BoolOp)) or (isinstance(v, ast.UnaryOp) and isinstance(v.op, ast.Not)):
            return "true or false"
        if isinstance(v, ast.JoinedStr):
            return "text"
        if isinstance(v, (ast.List, ast.ListComp)):
            return "a list"
        if isinstance(v, (ast.Dict, ast.DictComp)):
            return "a dictionary"
        if isinstance(v, (ast.Set, ast.SetComp)):
            return "a set"
        if isinstance(v, ast.Tuple):
            return f"{len(v.elts)} values together (a tuple)"
        if isinstance(v, ast.BinOp):
            return "a number"
        if isinstance(v, ast.Call) and isinstance(v.func, ast.Name):
            return {"round": "a number", "len": "a number", "sum": "a number", "int": "a whole number",
                    "float": "a number", "str": "text", "list": "a list", "dict": "a dictionary",
                    "sorted": "a list", "bool": "true or false", "max": "a value", "min": "a value",
                    "set": "a set", "tuple": "a tuple"}.get(v.func.id)
        return None

    kinds = [k for k in (kind(v) for v in vals) if k]
    if not kinds:
        return None
    uniq = list(dict.fromkeys(kinds))
    if len(uniq) > 3:
        return None
    return " or ".join(uniq)


def describe(func: ast.AST, key: str, docstring: str) -> Dict[str, Any]:
    nodes = list(_own_nodes(func))
    returns = [n for n in nodes if isinstance(n, ast.Return)]
    raises = [n for n in nodes if isinstance(n, ast.Raise)]

    # summary
    summary = clean_docstring(docstring) if docstring else ""
    written = _written().get(key)
    if written and (len(summary) < 25 or summary.startswith(":") or "!!!" in (docstring or "")[:20]):
        summary = written
    summary_source = "written for this app" if summary == written else ("docstring" if summary else None)

    # what you get back
    if func.returns is not None:
        ret = _annotation_words(ast.unparse(func.returns))
    else:
        ret = _returns_from_code(returns)

    # possible results: (True/False, "message") tuples or plain text results
    outcomes: List[Dict[str, Any]] = []
    seen = set()
    for r in returns:
        v = r.value
        if isinstance(v, ast.Tuple) and len(v.elts) >= 2 and isinstance(v.elts[0], ast.Constant) \
                and isinstance(v.elts[0].value, (bool, type(None))):
            msg = _text(v.elts[1])
            if msg is not None and (v.elts[0].value, msg) not in seen:
                seen.add((v.elts[0].value, msg))
                outcomes.append({"ok": v.elts[0].value is True, "message": msg})
        elif v is not None and _text(v) is not None and len(returns) > 1:
            msg = _text(v)
            if (None, msg) not in seen:
                seen.add((None, msg))
                outcomes.append({"ok": None, "message": msg})
    if any(o["ok"] is not None for o in outcomes) and ret and "tuple" in ret:
        firsts = [r.value.elts[0] for r in returns if isinstance(r.value, ast.Tuple) and r.value.elts]
        if all(isinstance(f, ast.Constant) and isinstance(f.value, bool) for f in firsts):
            ret = "a pair: (True or False, message)"
        else:
            ret = "a pair: (the result — or None if it failed, message)"

    # errors it raises on purpose
    errors: List[Dict[str, str]] = []
    for r in raises:
        exc = r.exc
        if exc is None:
            continue
        name, msg = None, None
        if isinstance(exc, ast.Call):
            f = exc.func
            name = f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else None
            if exc.args:
                msg = _text(exc.args[0])
        elif isinstance(exc, ast.Name):
            name = exc.id
        if name and (name, msg) not in {(e["type"], e.get("message")) for e in errors}:
            errors.append({"type": name, "message": msg or ""})

    return {
        "summary": summary,
        "summary_source": summary_source,
        "returns": ret,
        "outcomes": outcomes[:12],
        "raises": errors[:8],
    }
