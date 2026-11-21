"""
Check every function: run it once with the values the Function Runner pre-fills,
and record whether it works. The result (function_check.json) is used by the
backend to hide functions that can't run on their own.

Run it again whenever projects or the example logic change:

    cd backend && python3 check_functions.py
"""

import copy
import io
import contextlib
import json
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import main

OUT = Path(__file__).parent / "function_check.json"

# Functions we never run automatically: they could open programs, wait for the
# keyboard, change files, or go on the internet.
_RISKY_SUBSTR = ("launch", "getchar", "rmtree", "unlink", "install", "serve", "sleep", "prompt",
                 "confirm", "open_url", "webbrowser")
_RISKY_TOKENS = {"edit", "open", "run", "main", "exit", "clear", "pause", "write", "save", "dump",
                 "remove", "delete", "kill", "wait", "watch", "input", "mkdir", "touch", "chdir",
                 "reformat", "patch_stdout", "rename", "move", "copy"}
_NETWORK_TOKENS = {"get", "post", "put", "patch", "delete", "head", "options", "request", "send",
                   "stream", "connect", "fetch", "download", "upload", "urlopen"}


def is_risky(project: str, name: str) -> bool:
    low = name.lower()
    if any(r in low for r in _RISKY_SUBSTR):
        return True
    tokens = set(re.split(r"[_.]+", low))
    if tokens & _RISKY_TOKENS:
        return True
    return project in ("httpx", "requests") and bool(tokens & _NETWORK_TOKENS)


def default_call(params):
    """Exactly what the web page sends when you press Run without changing anything."""
    args, kwargs, skipped = [], {}, False
    for p in params:
        prefilled = p.get("typeable", True) and (
            p["required"] or p.get("source") in ("library tests", "sample file")) and p.get("example_json")
        if p["kind"] == "var_positional":
            if prefilled:
                v = json.loads(p["example_json"])
                if isinstance(v, list):
                    args.extend(v)
            continue
        if p["kind"] == "var_keyword":
            if prefilled:
                v = json.loads(p["example_json"])
                if isinstance(v, dict):
                    kwargs.update(v)
            continue
        if not prefilled:
            if not p["required"]:
                skipped = True
                continue
            value = ""
        else:
            value = json.loads(p["example_json"])
        if p["kind"] == "keyword_only" or skipped:
            kwargs[p["name"]] = value
        else:
            args.append(value)
    return args, kwargs


_BATCH_RUNNER = r"""
import asyncio, contextlib, importlib, inspect, io, json, os, signal, sys, tempfile, types
cfg = json.loads(sys.stdin.read())
for extra in reversed(cfg["extra_paths"]):
    sys.path.insert(0, extra)
sys.path.insert(0, cfg["src"])
for mod_name, attrs in cfg["stub_modules"].items():
    stub = types.ModuleType(mod_name); stub.__dict__.update(attrs); sys.modules.setdefault(mod_name, stub)
os.chdir(tempfile.mkdtemp())
sys.stdin = io.StringIO("")
class Timeout(BaseException): pass
def on_alarm(*_): raise Timeout()
signal.signal(signal.SIGALRM, on_alarm)
results = {}
for it in cfg["items"]:
    key = it["file"] + "::" + it["name"]
    try:
        signal.alarm(5)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            obj = importlib.import_module(it["module"])
            for part in it["name"].split("."):
                obj = getattr(obj, part)
            r = obj(*it["args"], **it["kwargs"])
            if inspect.isawaitable(r):
                r = asyncio.run(r)
        signal.alarm(0)
        results[key] = {"ok": True}
    except Timeout:
        results[key] = {"ok": False, "error": "took too long (waiting for something)"}
    except BaseException as e:
        signal.alarm(0)
        results[key] = {"ok": False, "error": (type(e).__name__ + ": " + str(e))[:200]}
print("\n" + json.dumps(results))
"""


def check_domain(project):
    results = {}
    for f in main.list_project_files(project):
        module = main.load_module(project, f)
        for fn in main.get_functions_from_file(project, f):
            key = f"{f}::{fn['name']}"
            args, kwargs = default_call(fn["params"])
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    getattr(module, fn["name"])(*copy.deepcopy(args), **copy.deepcopy(kwargs))
                results[key] = {"ok": True}
            except Exception as e:
                results[key] = {"ok": False, "error": f"{type(e).__name__}: {e}"[:200]}
    return results


def check_library(project, meta):
    results, items = {}, []
    for f in main.list_project_files(project):
        for fn in main.get_functions_from_file(project, f):
            if not fn["runnable"]:
                continue
            key = f"{f}::{fn['name']}"
            if is_risky(project, fn["name"]):
                results[key] = {"ok": False, "error": "skipped: could open programs, change files or use the internet"}
                continue
            args, kwargs = default_call(fn["params"])
            items.append({"file": f, "name": fn["name"], "module": main._module_name(f),
                          "args": args, "kwargs": kwargs})
    cfg = {
        "src": str(main.project_src_root(project)),
        "extra_paths": [str((main.BASE_DIR / x).resolve()) for x in meta.get("extra_paths", [])],
        "stub_modules": meta.get("stub_modules", {}),
        "items": items,
    }
    proc = subprocess.run([main.LIBRARY_PYTHON, "-I", "-c", _BATCH_RUNNER], input=json.dumps(cfg),
                          capture_output=True, text=True, timeout=1800, cwd=tempfile.gettempdir())
    lines = proc.stdout.strip().splitlines()
    try:
        results.update(json.loads(lines[-1]))
    except (IndexError, json.JSONDecodeError):
        for it in items:
            results[f"{it['file']}::{it['name']}"] = {"ok": False, "error": "checker crashed"}
        print(f"  ! {project}: checker crashed: {proc.stderr[-300:]}")
    return results


def main_cli():
    start = time.time()
    all_results = {}
    for project, meta in main.PROJECTS.items():
        t = time.time()
        res = check_domain(project) if meta["kind"] == "domain" else check_library(project, meta)
        all_results[project] = res
        ok = sum(r["ok"] for r in res.values())
        print(f"{project:26} works: {ok:4} / {len(res):4}   ({time.time() - t:.0f}s)")
    OUT.write_text(json.dumps({"generated": time.strftime("%Y-%m-%d %H:%M"), "results": all_results}, indent=0))
    total = sum(len(r) for r in all_results.values())
    ok = sum(x["ok"] for r in all_results.values() for x in r.values())
    print(f"TOTAL works: {ok} / {total}   in {time.time() - start:.0f}s  -> {OUT.name}")


if __name__ == "__main__":
    main_cli()
