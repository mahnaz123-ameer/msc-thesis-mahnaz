"""
Real example files for functions that take a file or folder path.

A function like rich's Theme.read(path) needs a file that actually exists.
We keep a small set of sample files in backend/sample_files/ (re-created on
every start, so a function that changes them can't break later runs) and
point path inputs at the right one.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional

SAMPLE_DIR = (Path(__file__).parent / "sample_files").resolve()

SAMPLES: Dict[str, str] = {
    "example.txt": "Hello world\nThis is a sample text file.\nThird line.\n",
    "example.py": "def add(a, b):\n    return a + b\n\n\nprint(add(1, 2))\n",
    "example.json": '{\n  "name": "Alice",\n  "age": 30,\n  "tags": ["student", "researcher"]\n}\n',
    # configparser format; the [styles] section is what rich's Theme.read expects
    "example.ini": "[styles]\ninfo = dim cyan\nwarning = magenta\ndanger = bold red\n",
    "pyproject.toml": '[project]\nname = "example"\nversion = "1.0.0"\n\n[tool.black]\nline-length = 88\n',
    "example.html": "<!doctype html>\n<html><body><h1>Hello</h1><p>Sample page</p></body></html>\n",
    "example.md": "# Title\n\nSome **bold** text and a [link](https://example.com).\n",
    "example.csv": "name,age\nAlice,30\nBob,25\n",
}

_FILE_NAMES = re.compile(r"(^|_)(path|file|filename|file_name|filepath|config_file|path_config|path_or_file)$")
_DIR_NAMES = re.compile(r"(^|_)(dir|directory|folder|root|cache_dir)$")
_WEB_PROJECTS = {"fastapi", "flask", "httpx", "requests"}


def ensure_sample_files() -> None:
    SAMPLE_DIR.mkdir(exist_ok=True)
    for name, content in SAMPLES.items():
        path = SAMPLE_DIR / name
        if not path.exists() or path.read_text() != content:
            path.write_text(content)


def _pick_file(text: str) -> str:
    t = text.lower()
    if "configparser" in t or "theme" in t or ".ini" in t or "config file" in t:
        return "example.ini"
    if "toml" in t or "pyproject" in t:
        return "pyproject.toml"
    if "json" in t:
        return "example.json"
    if "python" in t or ".py" in t or "module" in t or "source" in t:
        return "example.py"
    if "html" in t:
        return "example.html"
    if "markdown" in t:
        return "example.md"
    if "csv" in t:
        return "example.csv"
    return "example.txt"


def apply_sample_paths(project: str, params: List[dict], docstring: str) -> None:
    """Point file/folder inputs at real sample files (library projects only)."""
    for p in params:
        if p["type"] not in ("string", "any") or not p.get("typeable", True):
            continue
        name = p["name"]
        if p.get("source") == "library tests" and name != "path":
            continue                                    # the tests already gave a real value
        if _DIR_NAMES.search(name):
            p["example"] = str(SAMPLE_DIR)
            note = "sample folder"
        elif _FILE_NAMES.search(name):
            if name == "path" and project in _WEB_PROJECTS and "file" not in docstring.lower():
                continue                                # in web libraries `path` is a URL path
            p["example"] = str(SAMPLE_DIR / _pick_file(docstring + " " + name))
            note = "sample file"
        else:
            continue
        import json
        p["example_json"] = json.dumps(p["example"])
        p["type"] = "string"
        p["source"] = "sample file"
        files = [{"value": json.dumps(str(SAMPLE_DIR / f)), "note": "sample file"} for f in SAMPLES]
        if note == "sample folder":
            files = [{"value": json.dumps(str(SAMPLE_DIR)), "note": "sample folder"}]
        first = {"value": p["example_json"], "note": note}
        p["suggestions"] = [first] + [f for f in files if f["value"] != first["value"]]


def web_path_example(project: str, params: List[dict]) -> None:
    """In web libraries, give URL-path inputs a URL path instead of 'hello'."""
    if project not in _WEB_PROJECTS:
        return
    for p in params:
        if p["name"] in ("path", "url_path", "route", "rule") and p["type"] == "string" \
                and p.get("source") not in ("library tests", "sample file"):
            p["example"] = "/items/1"
            p["example_json"] = '"/items/1"'
            p["suggestions"] = [{"value": '"/items/1"', "note": "URL path"},
                                {"value": '"/"', "note": "home page"}] + p.get("suggestions", [])
