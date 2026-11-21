"""
Stage 1 — AI Test Generation

1. Dataset   : pick functions from every project, balanced across
               simple / moderate / complex (by cyclomatic complexity).
2. Prompt    : one standard prompt, identical for every AI tool.
3. Collect   : save the test file each tool (ChatGPT, Claude, Gemini)
               produced — pasted by hand, or generated through an API key.
4. Run       : run every saved test file with pytest and record the result.

Files:
  stage1/dataset.json              chosen functions
  stage1/prompt_template.txt       the standard prompt (edit to change it for all tools)
  generated_tests/<tool>/<project>/test_<id>.py     the tests
  generated_tests/<tool>/<project>/test_<id>.json   who/when/how + last pytest result
"""

import ast
import csv
import io
import json
import os
import random
import re
import ssl
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

import main as core

ROOT = Path(__file__).resolve().parent.parent
STAGE1_DIR = ROOT / "stage1"
DATASET_FILE = STAGE1_DIR / "dataset.json"
PROMPT_FILE = STAGE1_DIR / "prompt_template.txt"
TESTS_DIR = ROOT / "generated_tests"

TOOLS: Dict[str, Dict[str, Any]] = {
    "chatgpt": {"name": "ChatGPT", "key_env": "OPENAI_API_KEY", "model_env": "OPENAI_MODEL",
                "default_model": "gpt-4o", "where": "chatgpt.com"},
    "claude":  {"name": "Claude", "key_env": "ANTHROPIC_API_KEY", "model_env": "ANTHROPIC_MODEL",
                "default_model": "claude-sonnet-5-5", "where": "claude.ai"},
    "gemini":  {"name": "Gemini", "key_env": "GEMINI_API_KEY", "model_env": "GEMINI_MODEL",
                "default_model": "gemini-3.1-pro-preview", "where": "gemini.google.com"},
}

DEFAULT_PROMPT = '''You are given a Python function from the project "{project_name}".

Write a complete pytest unit test file for this function.

Rules:
- Import the function with exactly this line: {import_line}
- Use pytest. Write each test as a separate function whose name starts with test_.
- Cover normal cases, edge cases and invalid inputs.
- Do not use the network, real files, or any library other than pytest and the Python standard library.
- Return only the Python code of the test file, in one code block.

Function (module {module}):
```python
{source}
```
'''

LEVELS = ("simple", "moderate", "complex")


def _load_env_file() -> None:
    """Read API keys / model names from backend/.env (KEY=value lines). Never committed."""
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            v = v.strip().strip('"').strip("'")
            if v:
                os.environ.setdefault(k.strip(), v)


_load_env_file()

router = APIRouter(prefix="/stage1", tags=["stage1"])


# ─── Complexity ──────────────────────────────────────────────

def cyclomatic_complexity(func: ast.AST) -> int:
    """McCabe complexity: 1 + number of decision points."""
    cc = 1
    for node in ast.walk(func):
        if isinstance(node, (ast.If, ast.IfExp, ast.For, ast.AsyncFor, ast.While, ast.ExceptHandler,
                             ast.Assert)):
            cc += 1
        elif isinstance(node, ast.BoolOp):
            cc += len(node.values) - 1
        elif isinstance(node, ast.comprehension):
            cc += 1 + len(node.ifs)
        elif isinstance(node, ast.match_case):
            cc += 1
    return cc


def level_for(cc: int) -> str:
    if cc <= 2:
        return "simple"
    if cc <= 6:
        return "moderate"
    return "complex"


def code_lines(func: ast.AST, source_lines: List[str]) -> int:
    """Lines of code, without blank lines, comments and the docstring."""
    doc_lines = set()
    body = getattr(func, "body", [])
    if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) \
            and isinstance(body[0].value.value, str):
        doc_lines = set(range(body[0].lineno, body[0].end_lineno + 1))
    n = 0
    for i in range(func.lineno, func.end_lineno + 1):
        line = source_lines[i - 1].strip()
        if line and not line.startswith("#") and i not in doc_lines:
            n += 1
    return n


# ─── Dataset ─────────────────────────────────────────────────

def _item_id(project: str, filename: str, name: str) -> str:
    stem = filename[:-3].replace("/", ".")
    return f"{project}__{stem}__{name}"


def _import_line(meta: Dict, filename: str, name: str) -> str:
    module = filename[:-3].split("/")[-1] if meta["kind"] == "domain" else core._module_name(filename)
    return f"from {module} import {name}"


def candidates() -> List[Dict[str, Any]]:
    """Every function that is a good Stage 1 subject: top-level, public, and runs fine."""
    out = []
    for project, meta in core.PROJECTS.items():
        if not (core.BASE_DIR / project).exists():
            continue
        for filename in core.list_project_files(project):
            source = core.resolve_file(project, filename).read_text()
            tree = ast.parse(source)
            lines = source.splitlines()
            nodes = {n.name: n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
            for fn in core.get_functions_from_file(project, filename):
                name = fn["name"]
                if fn["class"] or name.startswith("_") or not fn["runnable"] or fn["works"] is False:
                    continue
                if "overload" in core._decorator_names(nodes[name]):
                    continue
                node = nodes[name]
                loc = code_lines(node, lines)
                if loc < 2:
                    continue
                cc = cyclomatic_complexity(node)
                out.append({
                    "id": _item_id(project, filename, name),
                    "project": project,
                    "project_name": meta["name"],
                    "kind": meta["kind"],
                    "file": filename,
                    "module": filename[:-3].split("/")[-1] if meta["kind"] == "domain" else core._module_name(filename),
                    "function": name,
                    "import_line": _import_line(meta, filename, name),
                    "complexity": cc,
                    "lines": loc,
                    "level": level_for(cc),
                    "summary": fn["about"]["summary"],
                })
    return out


def build_dataset(per_level: Optional[int] = None, seed: int = 42) -> Dict[str, Any]:
    """per_level=None: every eligible function. Otherwise pick `per_level` functions of each
    level from every project (fixed seed = repeatable)."""
    pool = candidates()
    order = {p: i for i, p in enumerate(core.PROJECTS)}
    if per_level is None:
        chosen = sorted(pool, key=lambda c: (order[c["project"]], LEVELS.index(c["level"]), c["id"]))
    else:
        rng = random.Random(seed)
        chosen = []
        for project in core.PROJECTS:
            for level in LEVELS:
                group = sorted((c for c in pool if c["project"] == project and c["level"] == level),
                               key=lambda c: c["id"])
                chosen += rng.sample(group, min(per_level, len(group)))
    data = {
        "created": time.strftime("%Y-%m-%d %H:%M"),
        "mode": "all eligible functions" if per_level is None else f"{per_level} per level per project",
        "per_level": per_level,
        "seed": seed,
        "levels": {"simple": "complexity 1-2", "moderate": "complexity 3-6", "complex": "complexity 7+"},
        "functions": chosen,
    }
    STAGE1_DIR.mkdir(exist_ok=True)
    DATASET_FILE.write_text(json.dumps(data, indent=1, ensure_ascii=False))
    return data


_dataset_cache = {"mtime": None, "data": None}


def load_dataset() -> Dict[str, Any]:
    if not DATASET_FILE.exists():
        return build_dataset()
    mtime = DATASET_FILE.stat().st_mtime
    if _dataset_cache["mtime"] != mtime:
        _dataset_cache["data"] = json.loads(DATASET_FILE.read_text())
        _dataset_cache["mtime"] = mtime
    return _dataset_cache["data"]


def get_item(item_id: str) -> Dict[str, Any]:
    for it in load_dataset()["functions"]:
        if it["id"] == item_id:
            return it
    raise HTTPException(status_code=404, detail="Function not in the Stage 1 dataset")


# ─── Prompt ──────────────────────────────────────────────────

def prompt_template() -> str:
    if not PROMPT_FILE.exists():
        STAGE1_DIR.mkdir(exist_ok=True)
        PROMPT_FILE.write_text(DEFAULT_PROMPT)
    return PROMPT_FILE.read_text()


def function_source(item: Dict[str, Any]) -> str:
    source = core.resolve_file(item["project"], item["file"]).read_text()
    node = core.find_function(source, item["function"])
    lines = source.splitlines()
    start = (node.decorator_list[0].lineno if node.decorator_list else node.lineno) - 1
    return "\n".join(lines[start:node.end_lineno])


def build_prompt(item: Dict[str, Any]) -> str:
    return prompt_template().format(
        project_name=item["project_name"], import_line=item["import_line"],
        module=item["module"], function=item["function"], source=function_source(item))


# ─── Saved tests ─────────────────────────────────────────────

def test_paths(tool: str, item: Dict[str, Any]):
    if tool not in TOOLS:
        raise HTTPException(status_code=404, detail="Unknown tool")
    folder = TESTS_DIR / tool / item["project"]
    safe = re.sub(r"[^A-Za-z0-9_]", "_", item["id"])     # dots would look like a package to Python
    return folder / f"test_{safe}.py", folder / f"test_{safe}.json"


def extract_code(text: str) -> str:
    """Take the Python code out of an AI answer (largest ``` block, or the whole text)."""
    blocks = re.findall(r"```(?:python|py)?[^\n]*\n(.*?)```", text, flags=re.S)
    code = max(blocks, key=len) if blocks else text
    return code.strip() + "\n"


def count_test_functions(code: str) -> Optional[int]:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None
    return sum(1 for n in ast.walk(tree)
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith("test"))


def read_saved(tool: str, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    code_path, meta_path = test_paths(tool, item)
    if not code_path.exists():
        return None
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    return {"code": code_path.read_text(), **meta}


def save_test(tool: str, item: Dict[str, Any], raw: str, source: str, model: Optional[str] = None,
              usage: Optional[Dict[str, Any]] = None) -> Dict:
    code = extract_code(raw)
    code_path, meta_path = test_paths(tool, item)
    code_path.parent.mkdir(parents=True, exist_ok=True)
    code_path.write_text(code)
    meta = {
        "tool": tool, "tool_name": TOOLS[tool]["name"], "source": source, "model": model,
        "saved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "test_functions": count_test_functions(code),
        "syntax_ok": count_test_functions(code) is not None,
        "usage": usage,
        "raw_answer_chars": len(raw),
    }
    meta_path.write_text(json.dumps(meta, indent=1))
    return meta


# ─── Running tests with pytest ───────────────────────────────

def run_tests(tool: str, item: Dict[str, Any]) -> Dict[str, Any]:
    code_path, meta_path = test_paths(tool, item)
    if not code_path.exists():
        raise HTTPException(status_code=404, detail="No saved test for this tool yet")
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    project_meta = core.PROJECTS[item["project"]]

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "pytest.ini").write_text("[pytest]\n")       # ignore the libraries' own pytest settings
        stubs = tmp / "stubs"
        stubs.mkdir()
        for mod_name, attrs in project_meta.get("stub_modules", {}).items():
            (stubs / f"{mod_name}.py").write_text("".join(f"{k} = {v!r}\n" for k, v in attrs.items()))
        paths = [str(core.project_src_root(item["project"]))]
        paths += [str((core.BASE_DIR / x).resolve()) for x in project_meta.get("extra_paths", [])]
        paths.append(str(stubs))
        env = {**os.environ, "PYTHONPATH": os.pathsep.join(paths), "PYTHONDONTWRITEBYTECODE": "1"}
        report = tmp / "report.xml"
        try:
            proc = subprocess.run(
                [core.LIBRARY_PYTHON, "-m", "pytest", str(code_path), "-q", "-p", "no:cacheprovider",
                 "-c", str(tmp / "pytest.ini"), "--rootdir", str(tmp), "--timeout", "20",
                 f"--junitxml={report}", "-o", "junit_family=xunit2"],
                cwd=tmp, env=env, capture_output=True, text=True, timeout=180)
            output = (proc.stdout + proc.stderr)[-6000:]
        except subprocess.TimeoutExpired:
            output, proc = "Timed out after 180 seconds", None

        total = failed = errors = skipped = 0
        if report.exists():
            suite = ET.parse(report).getroot()
            suite = suite if suite.tag == "testsuite" else suite.find("testsuite")
            total = int(suite.get("tests", 0))
            failed = int(suite.get("failures", 0))
            errors = int(suite.get("errors", 0))
            skipped = int(suite.get("skipped", 0))
    passed = max(total - failed - errors - skipped, 0)
    run = {
        "ran_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total": total, "passed": passed, "failed": failed, "errors": errors, "skipped": skipped,
        # collection errors (wrong import, syntax error) mean no test could run at all
        "could_run": total > 0 and "during collection" not in output,
        "output": output,
    }
    meta["run"] = run
    meta_path.write_text(json.dumps(meta, indent=1))
    return run


# ─── Optional: generate through an API key ───────────────────

# python.org builds of Python on macOS ship without CA certificates; use certifi's bundle.
try:
    import certifi
    _SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    _SSL_CONTEXT = ssl.create_default_context()

def _post_json(url: str, headers: Dict[str, str], body: Dict) -> Dict:
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json", **headers})
    try:
        with urllib.request.urlopen(req, timeout=180, context=_SSL_CONTEXT) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"{e.code}: {e.read().decode()[:400]}")
    except urllib.error.URLError as e:
        raise HTTPException(status_code=502, detail=f"Could not reach the API: {e.reason}")


def _call_api(tool: str, key: str, model: str, prompt: str):
    if tool == "chatgpt":
        data = _post_json("https://api.openai.com/v1/chat/completions",
                          {"Authorization": f"Bearer {key}"},
                          {"model": model, "messages": [{"role": "user", "content": prompt}]})
        u = data.get("usage") or {}
        return (data["choices"][0]["message"]["content"], data.get("model", model),
                {"input_tokens": u.get("prompt_tokens"), "output_tokens": u.get("completion_tokens")})
    if tool == "claude":
        data = _post_json("https://api.anthropic.com/v1/messages",
                          {"x-api-key": key, "anthropic-version": "2023-06-01"},
                          {"model": model, "max_tokens": 8000,
                           "messages": [{"role": "user", "content": prompt}]})
        u = data.get("usage") or {}
        text = "".join(b.get("text", "") for b in data["content"] if b.get("type") == "text")
        return text, data.get("model", model), {"input_tokens": u.get("input_tokens"),
                                                 "output_tokens": u.get("output_tokens")}
    if tool == "gemini":
        data = _post_json(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                          {"x-goog-api-key": key},
                          {"contents": [{"role": "user", "parts": [{"text": prompt}]}]})
        cands = data.get("candidates") or []
        if not cands:
            reason = (data.get("promptFeedback") or {}).get("blockReason", "no answer returned")
            raise HTTPException(status_code=502, detail=f"Gemini returned no answer ({reason})")
        parts = (cands[0].get("content") or {}).get("parts") or []
        u = data.get("usageMetadata") or {}
        return ("".join(p.get("text", "") for p in parts), data.get("modelVersion", model),
                {"input_tokens": u.get("promptTokenCount"), "output_tokens": u.get("candidatesTokenCount")})
    raise HTTPException(status_code=400, detail="This tool has no API — paste its answer instead")


def generate_with_api(tool: str, prompt: str, retries: int = 5):
    """Returns (answer text, model name, token usage). Retries when the API is busy."""
    cfg = TOOLS[tool]
    key = os.environ.get(cfg["key_env"] or "", "")
    if not key:
        raise HTTPException(status_code=400, detail=f"{cfg['name']} has no API key set "
                                                    f"(add {cfg['key_env']} to backend/.env)")
    model = os.environ.get(cfg["model_env"], cfg["default_model"])
    for attempt in range(retries + 1):
        try:
            return _call_api(tool, key, model, prompt)
        except HTTPException as e:
            busy = str(e.detail).startswith(("429", "500", "502", "503", "504", "529", "Could not reach"))
            if not busy or attempt == retries:
                raise
            time.sleep(min(60, 5 * 2 ** attempt))   # 5s, 10s, 20s, 40s, 60s


def tools_info() -> Dict[str, Any]:
    return {
        t: {"name": c["name"], "where": c["where"],
            "auto": bool(c["key_env"] and os.environ.get(c["key_env"])),
            "key_env": c["key_env"],
            "model": os.environ.get(c["model_env"], c["default_model"]) if c["model_env"] else None}
        for t, c in TOOLS.items()
    }


# ─── Status helpers ──────────────────────────────────────────

def status_of(tool: str, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    saved = read_saved(tool, item)
    if saved is None:
        return None
    run = saved.get("run") or {}
    return {
        "saved_at": saved.get("saved_at"), "source": saved.get("source"),
        "test_functions": saved.get("test_functions"), "syntax_ok": saved.get("syntax_ok"),
        "total": run.get("total"), "passed": run.get("passed"), "failed": run.get("failed"),
        "errors": run.get("errors"), "could_run": run.get("could_run"), "ran": bool(run),
    }


# ─── Routes ──────────────────────────────────────────────────

class SaveBody(BaseModel):
    code: str


class RebuildBody(BaseModel):
    per_level: Optional[int] = None     # None = all eligible functions
    seed: int = 42


@router.get("/overview")
def overview():
    data = load_dataset()
    rows = []
    for it in data["functions"]:
        rows.append({**it, "status": {t: status_of(t, it) for t in TOOLS}})
    return {"dataset": {k: v for k, v in data.items() if k != "functions"}, "functions": rows,
            "tools": tools_info(), "prompt_template": prompt_template()}


@router.post("/dataset/rebuild")
def rebuild(body: RebuildBody):
    if body.per_level is not None and not 1 <= body.per_level <= 50:
        raise HTTPException(status_code=400, detail="per_level must be 1-50, or empty for all")
    data = build_dataset(body.per_level, body.seed)
    return {"count": len(data["functions"])}


@router.get("/items/{item_id}")
def item_detail(item_id: str):
    it = get_item(item_id)
    return {**it, "source": function_source(it), "prompt": build_prompt(it),
            "tests": {t: read_saved(t, it) for t in TOOLS}, "tools": tools_info()}


@router.put("/items/{item_id}/{tool}")
def save_and_run(item_id: str, tool: str, body: SaveBody):
    it = get_item(item_id)
    if not body.code.strip():
        raise HTTPException(status_code=400, detail="Paste the test code first")
    save_test(tool, it, body.code, source="pasted")
    run_tests(tool, it)
    return read_saved(tool, it)


@router.post("/items/{item_id}/{tool}/run")
def rerun(item_id: str, tool: str):
    it = get_item(item_id)
    run_tests(tool, it)
    return read_saved(tool, it)


@router.post("/items/{item_id}/{tool}/generate")
def generate(item_id: str, tool: str):
    it = get_item(item_id)
    answer, model, usage = generate_with_api(tool, build_prompt(it))
    save_test(tool, it, answer, source="api", model=model, usage=usage)
    run_tests(tool, it)
    return read_saved(tool, it)


@router.delete("/items/{item_id}/{tool}")
def delete_test(item_id: str, tool: str):
    it = get_item(item_id)
    code_path, meta_path = test_paths(tool, it)
    for p in (code_path, meta_path):
        if p.exists():
            p.unlink()
    return {"deleted": True}


@router.get("/export.csv", response_class=PlainTextResponse)
def export_csv():
    """One row per function x tool — for the thesis results chapter."""
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["project", "file", "function", "level", "complexity", "lines", "tool", "has_tests",
                "test_functions", "tests_run", "passed", "failed", "errors", "source", "saved_at"])
    for it in load_dataset()["functions"]:
        for tool in TOOLS:
            s = status_of(tool, it) or {}
            w.writerow([it["project"], it["file"], it["function"], it["level"], it["complexity"], it["lines"],
                        tool, bool(s), s.get("test_functions"), s.get("total"), s.get("passed"),
                        s.get("failed"), s.get("errors"), s.get("source"), s.get("saved_at")])
    return out.getvalue()
