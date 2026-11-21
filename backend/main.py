"""
MSc Thesis — FastAPI Backend
Semantic Redundancy Pruning and Targeted Mutation Validation
for AI-Generated Unit Test Suites

Author: Mahnaz Ameer | University of Dhaka
"""

import ast
import os
import sys
import json
import inspect
import io
import contextlib
import subprocess
import textwrap
import importlib.util
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from type_hints import param_hints

# ─── App Setup ───────────────────────────────────────────────
app = FastAPI(
    title="MSc Thesis API",
    description="AI Test Suite Auditor — Mahnaz Ameer",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Path to research projects ───────────────────────────────
BASE_DIR = Path(__file__).parent.parent / "research_projects"

# kind: "domain"  -> hand-written thesis projects, flat folder of .py files
#       "library" -> real-world open-source Python libraries (cloned repos).
#                    `src` is the directory placed on sys.path, `packages`
#                    are the importable packages inside it.
PROJECTS: Dict[str, Dict[str, Any]] = {
    "01_university_management": {"name": "University Management", "kind": "domain"},
    "02_banking_system":        {"name": "Banking System",        "kind": "domain"},
    "03_hospital_management":   {"name": "Hospital Management",   "kind": "domain"},
    "04_ecommerce_system":      {"name": "E-Commerce System",     "kind": "domain"},
    "05_ride_sharing":          {"name": "Ride Sharing",          "kind": "domain"},
    "arrow":    {"name": "Arrow",    "kind": "library", "src": "",    "packages": ["arrow"],
                 "description": "Dates, times and timestamps"},
    "attrs":    {"name": "attrs",    "kind": "library", "src": "src", "packages": ["attr", "attrs"],
                 "description": "Classes without boilerplate"},
    "black":    {"name": "Black",    "kind": "library", "src": "src", "packages": ["black", "blib2to3", "blackd"],
                 # normally generated at install time; give it a stand-in so `import black` works
                 "stub_modules": {"_black_version": {"version": "dev"}},
                 "description": "Python code formatter"},
    "click":    {"name": "Click",    "kind": "library", "src": "src", "packages": ["click"],
                 "description": "Command-line interfaces"},
    "fastapi":  {"name": "FastAPI",  "kind": "library", "src": "",    "packages": ["fastapi"],
                 "extra_paths": ["pydantic"],   # use the pydantic clone next to it
                 "description": "Async web API framework"},
    "flask":    {"name": "Flask",    "kind": "library", "src": "src", "packages": ["flask"],
                 "description": "WSGI web framework"},
    "httpx":    {"name": "HTTPX",    "kind": "library", "src": "",    "packages": ["httpx"],
                 "description": "HTTP client"},
    "pydantic": {"name": "Pydantic", "kind": "library", "src": "",    "packages": ["pydantic"],
                 "description": "Data validation with type hints"},
    "requests": {"name": "Requests", "kind": "library", "src": "src", "packages": ["requests"],
                 "description": "HTTP for humans"},
    "rich":     {"name": "Rich",     "kind": "library", "src": "",    "packages": ["rich"],
                 "description": "Rich text and terminal formatting"},
}

FUNC_TYPES = (ast.FunctionDef, ast.AsyncFunctionDef)


def get_project(project: str) -> Dict[str, Any]:
    meta = PROJECTS.get(project)
    if meta is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return meta


def project_src_root(project: str) -> Path:
    meta = get_project(project)
    return (BASE_DIR / project / meta.get("src", "")).resolve()


def list_project_files(project: str) -> List[str]:
    """Python files of a project, as paths relative to its source root."""
    meta = get_project(project)
    root = project_src_root(project)
    if not root.exists():
        return []
    if meta["kind"] == "domain":
        return sorted(f.name for f in root.glob("*.py") if f.name != "__init__.py")
    files = []
    for pkg in meta["packages"]:
        pkg_dir = root / pkg
        for f in pkg_dir.rglob("*.py"):
            if "__pycache__" in f.parts:
                continue
            files.append(f.relative_to(root).as_posix())
    return sorted(files)


def resolve_file(project: str, filename: str) -> Path:
    """Resolve a project-relative file path safely (no path traversal)."""
    root = project_src_root(project)
    file_path = (root / filename).resolve()
    if root not in file_path.parents or file_path.suffix != ".py" or not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {filename}")
    return file_path


def iter_functions(tree: ast.AST, prefix: str = ""):
    """Yield (qualified_name, node, class_name) for module functions and class methods."""
    for node in getattr(tree, "body", []):
        if isinstance(node, FUNC_TYPES):
            yield prefix + node.name, node, prefix.rstrip(".") or None
        elif isinstance(node, ast.ClassDef):
            yield from iter_functions(node, f"{prefix}{node.name}.")


def find_function(source: str, function_name: str):
    tree = ast.parse(source)
    for qualname, node, _ in iter_functions(tree):
        if qualname == function_name:
            return node
    raise HTTPException(status_code=404, detail=f"Function {function_name} not found")


def count_functions(source: str) -> int:
    return sum(1 for _ in iter_functions(ast.parse(source)))


# ─── Helper: Load a module from file ─────────────────────────
def load_module(project: str, filename: str):
    file_path = resolve_file(project, filename)
    spec = importlib.util.spec_from_file_location("module", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _decorator_names(node) -> List[str]:
    names = []
    for d in node.decorator_list:
        d = d.func if isinstance(d, ast.Call) else d
        names.append(d.attr if isinstance(d, ast.Attribute) else getattr(d, "id", ""))
    return names


def _runnable(node, cls: Optional[str], params: List[Dict]) -> (bool, str):
    """Can this function be run from the web form (inputs typed as JSON)?"""
    decos = _decorator_names(node)
    if cls:
        if any(d in ("property", "cached_property", "setter", "getter", "deleter") for d in decos):
            return False, f"This is a property of {cls}, not a function you call."
        if "staticmethod" not in decos and "classmethod" not in decos:
            first = (node.args.posonlyargs + node.args.args)[:1]
            if first and first[0].arg == "self":
                return False, f"This is a method — it needs a {cls} object first, which can't be typed into a form."
    if "overload" in decos:
        return False, "This is only a type-checking stub (@overload), not real code."
    for p in params:
        if p["required"] and not p["json_ok"]:
            return False, f"Input '{p['name']}' must be a {p['annotation']} object, which can't be typed into a form."
    return True, ""


# ─── Helper: Extract functions from a file ───────────────────
def get_functions_from_file(project: str, filename: str) -> List[Dict]:
    source = resolve_file(project, filename).read_text()
    tree = ast.parse(source)
    module_funcs = {n.name: n for n in tree.body if isinstance(n, FUNC_TYPES)}
    functions = []
    for qualname, node, cls in iter_functions(tree):
        args = [arg.arg for arg in node.args.posonlyargs + node.args.args]
        if cls and args and args[0] in ("self", "cls"):
            args = args[1:]
        params = param_hints(node, skip_first=bool(cls), module_funcs=module_funcs)
        runnable, reason = _runnable(node, cls, params)
        functions.append({
            "name": qualname,
            "args": args,
            "docstring": ast.get_docstring(node) or "",
            "lineno": node.lineno,
            "class": cls,
            "is_async": isinstance(node, ast.AsyncFunctionDef),
            "params": params,
            "runnable": runnable,
            "reason": reason,
        })
    return functions


# ─── Helper: Get AST tree as dict ────────────────────────────
def ast_to_dict(node):
    if isinstance(node, ast.AST):
        fields = {}
        for field, value in ast.iter_fields(node):
            fields[field] = ast_to_dict(value)
        return {"type": type(node).__name__, "fields": fields}
    elif isinstance(node, list):
        return [ast_to_dict(item) for item in node]
    else:
        return node


# ─── Routes ──────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "MSc Thesis API running!", "author": "Mahnaz Ameer"}


@app.get("/projects")
def list_projects():
    """List all research projects (domain projects + open-source libraries)."""
    result = []
    for folder, meta in PROJECTS.items():
        if not (BASE_DIR / folder).exists():
            continue
        files = list_project_files(folder)
        result.append({
            "id": folder,
            "name": meta["name"],
            "kind": meta["kind"],
            "description": meta.get("description", ""),
            "files": files,
            "file_count": len(files),
        })
    return result


@app.get("/projects/{project}/files")
def list_files(project: str):
    """List Python files in a project."""
    if not (BASE_DIR / project).exists():
        raise HTTPException(status_code=404, detail="Project not found")
    return {"project": project, "files": list_project_files(project)}


@app.get("/projects/{project}/functions")
def list_project_functions(project: str):
    """Every function in a project (lightweight, for search)."""
    result = []
    for f in list_project_files(project):
        try:
            fns = get_functions_from_file(project, f)
        except Exception:
            continue
        for fn in fns:
            result.append({
                "file": f,
                "name": fn["name"],
                "summary": fn["docstring"].strip().split("\n")[0][:120],
                "runnable": fn["runnable"],
            })
    return {"project": project, "functions": result}


# NOTE: `filename` may contain slashes for library projects (e.g. "flask/sansio/app.py").
# Function-level routes are declared before file-level ones so the greedy
# `{filename:path}` converter cannot swallow "/functions/<name>".

@app.get("/projects/{project}/files/{filename:path}/functions/{function_name}/source")
def get_function_source(project: str, filename: str, function_name: str):
    """Get source code of a specific function."""
    source = resolve_file(project, filename).read_text()
    node = find_function(source, function_name)
    lines = source.splitlines()
    start = (node.decorator_list[0].lineno if node.decorator_list else node.lineno) - 1
    func_source = "\n".join(lines[start:node.end_lineno])
    return {"function": function_name, "source": textwrap.dedent(func_source)}


@app.get("/projects/{project}/files/{filename:path}/functions/{function_name}/ast")
def get_ast(project: str, filename: str, function_name: str):
    """Get AST tree of a specific function."""
    source = resolve_file(project, filename).read_text()
    node = find_function(source, function_name)
    return {
        "function": function_name,
        "ast": ast_to_dict(node),
        "simplified": build_simplified_ast(node),
    }


class RunRequest(BaseModel):
    args: List[Any] = []
    kwargs: Dict[str, Any] = {}


def _parse_args(raw: List[Any]) -> List[Any]:
    parsed = []
    for arg in raw:
        if isinstance(arg, str):
            try:
                parsed.append(json.loads(arg))
            except Exception:
                parsed.append(arg)
        else:
            parsed.append(arg)
    return parsed


# Runs a library function in a separate interpreter so the cloned packages
# (e.g. research_projects/fastapi, /pydantic) never clash with the copies
# this backend itself is running on.
_LIBRARY_RUNNER = r"""
import asyncio, importlib, inspect, json, sys
import types
src, module_name, qualname = sys.argv[1:4]
payload = json.loads(sys.stdin.read())
for extra in reversed(payload.get("extra_paths", [])):
    sys.path.insert(0, extra)
sys.path.insert(0, src)
for mod_name, attrs in payload.get("stub_modules", {}).items():
    stub = types.ModuleType(mod_name)
    stub.__dict__.update(attrs)
    sys.modules.setdefault(mod_name, stub)
import contextlib, io
real_stdout = sys.stdout
captured = io.StringIO()
def emit(data):
    data["output"] = captured.getvalue()[-5000:]
    real_stdout.write("\n" + json.dumps(data) + "\n")
try:
    with contextlib.redirect_stdout(captured):
        obj = importlib.import_module(module_name)
        for part in qualname.split("."):
            obj = getattr(obj, part)
        result = obj(*payload["args"], **payload["kwargs"])
        if inspect.isawaitable(result):
            result = asyncio.run(result)
    try:
        json.dumps(result)
        out = result
    except (TypeError, ValueError):
        out = repr(result)
    emit({"success": True, "result": out, "type": type(result).__name__})
except BaseException as e:
    emit({"success": False, "error": str(e) or type(e).__name__, "type": type(e).__name__})
"""


# Python used to run library code: its own venv with the libraries' dependencies
# (falls back to the backend's interpreter if the venv hasn't been created).
_LIB_VENV_PY = Path(__file__).parent / ".venv-libs" / "bin" / "python"
LIBRARY_PYTHON = os.environ.get("LIBRARY_PYTHON") or (str(_LIB_VENV_PY) if _LIB_VENV_PY.exists() else sys.executable)


def _module_name(filename: str) -> str:
    parts = filename[:-3].split("/")
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


@app.post("/projects/{project}/files/{filename:path}/functions/{function_name}/run")
def run_function(project: str, filename: str, function_name: str, body: RunRequest):
    """Run a function with provided arguments."""
    meta = get_project(project)
    parsed_args = _parse_args(body.args)

    if meta["kind"] == "library":
        resolve_file(project, filename)
        try:
            proc = subprocess.run(
                [LIBRARY_PYTHON, "-I", "-c", _LIBRARY_RUNNER,
                 str(project_src_root(project)), _module_name(filename), function_name],
                input=json.dumps({
                    "args": parsed_args,
                    "kwargs": body.kwargs,
                    "extra_paths": [str((BASE_DIR / x).resolve()) for x in meta.get("extra_paths", [])],
                    "stub_modules": meta.get("stub_modules", {}),
                }),
                capture_output=True, text=True, timeout=15,
            )
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Timed out after 15s", "type": "TimeoutError"}
        lines = proc.stdout.strip().splitlines()
        if lines:
            try:
                return json.loads(lines[-1])
            except json.JSONDecodeError:
                pass
        return {"success": False, "error": (proc.stderr or proc.stdout).strip()[-2000:],
                "type": "RunnerError"}

    try:
        module = load_module(project, filename)
        func = module
        for part in function_name.split("."):
            func = getattr(func, part, None)
            if func is None:
                raise HTTPException(status_code=404, detail=f"Function {function_name} not found")
        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            result = func(*parsed_args, **body.kwargs)
        try:
            json.dumps(result)
        except (TypeError, ValueError):
            result = repr(result)
        return {"success": True, "result": result, "type": type(result).__name__,
                "output": captured.getvalue()[-5000:]}
    except HTTPException:
        raise
    except Exception as e:
        return {"success": False, "error": str(e), "type": type(e).__name__}


@app.get("/projects/{project}/files/{filename:path}/functions")
def list_functions(project: str, filename: str):
    """List all functions (and class methods) in a file."""
    functions = get_functions_from_file(project, filename)
    return {"project": project, "file": filename, "functions": functions}


@app.get("/projects/{project}/files/{filename:path}/source")
def get_source(project: str, filename: str):
    """Get full source code of a file."""
    return {"source": resolve_file(project, filename).read_text()}


def build_simplified_ast(node, depth=0):
    """Build a simplified AST tree for frontend visualization."""
    if depth > 6:
        return None
    name = type(node).__name__
    label = name
    if isinstance(node, FUNC_TYPES):
        label = f"def {node.name}()"
    elif isinstance(node, ast.Return):
        label = "return"
    elif isinstance(node, ast.If):
        label = "if"
    elif isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name):
            label = f"call {node.func.id}()"
        elif isinstance(node.func, ast.Attribute):
            label = f"call .{node.func.attr}()"
    elif isinstance(node, ast.Assign):
        label = "assign"
    elif isinstance(node, ast.Compare):
        label = "compare"
    elif isinstance(node, ast.BoolOp):
        label = "and/or"
    elif isinstance(node, ast.Name):
        label = f"var:{node.id}"
    elif isinstance(node, ast.Constant):
        label = f"const:{repr(node.value)[:10]}"
    elif isinstance(node, ast.For):
        label = "for loop"
    elif isinstance(node, ast.While):
        label = "while"
    elif isinstance(node, ast.Raise):
        label = "raise"

    children = []
    for child in ast.iter_child_nodes(node):
        child_node = build_simplified_ast(child, depth + 1)
        if child_node:
            children.append(child_node)

    result = {"name": label, "type": name}
    if children:
        result["children"] = children[:6]  # Limit children for readability
    return result



class ASTAnalysisRequest(BaseModel):
    tests: List[str]  # List of test code strings


@app.post("/analyze/ast")
def analyze_ast_redundancy(body: ASTAnalysisRequest):
    """
    Analyze a list of test code strings for semantic redundancy using AST.
    Returns which tests are unique and which are duplicates.
    """
    results = []
    path_signatures = {}

    for i, test_code in enumerate(body.tests):
        try:
            tree = ast.parse(test_code)
            # Extract execution path signature
            signature = extract_path_signature(tree)
            sig_key = json.dumps(signature, sort_keys=True)

            if sig_key in path_signatures:
                results.append({
                    "index": i,
                    "code": test_code,
                    "status": "duplicate",
                    "duplicate_of": path_signatures[sig_key],
                    "signature": signature,
                    "ast": build_simplified_ast(tree),
                })
            else:
                path_signatures[sig_key] = i
                results.append({
                    "index": i,
                    "code": test_code,
                    "status": "unique",
                    "duplicate_of": None,
                    "signature": signature,
                    "ast": build_simplified_ast(tree),
                })
        except SyntaxError as e:
            results.append({
                "index": i,
                "code": test_code,
                "status": "error",
                "error": str(e),
            })

    unique_count = sum(1 for r in results if r.get("status") == "unique")
    duplicate_count = sum(1 for r in results if r.get("status") == "duplicate")

    return {
        "total": len(results),
        "unique": unique_count,
        "duplicates": duplicate_count,
        "reduction_percent": round((duplicate_count / len(results)) * 100, 1) if results else 0,
        "results": results,
    }


def extract_path_signature(tree):
    """Extract a normalized execution path signature from an AST."""
    signature = []
    for node in ast.walk(tree):
        node_type = type(node).__name__
        if node_type in ("FunctionDef", "If", "For", "While", "Return",
                         "Call", "Compare", "Assign", "Raise", "Assert"):
            entry = {"node": node_type}
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    entry["func"] = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    entry["func"] = node.func.attr
            elif isinstance(node, ast.Compare):
                entry["ops"] = [type(op).__name__ for op in node.ops]
            signature.append(entry)
    return signature


class MutationRequest(BaseModel):
    project: str
    filename: str
    function_name: str
    tests: List[str]


@app.post("/analyze/mutation")
def analyze_mutation(body: MutationRequest):
    """
    Simulate mutation testing on a function with provided test cases.
    Injects simple mutations and checks which tests would catch them.
    """
    source = resolve_file(body.project, body.filename).read_text()

    # Generate simple mutations
    mutations = generate_mutations(source, body.function_name)

    results = []
    for mutation in mutations:
        catching_tests = []
        for i, test in enumerate(body.tests):
            # Simplified: check if test would detect the mutation
            # based on assertion patterns
            catches = test_catches_mutation(test, mutation)
            if catches:
                catching_tests.append(i)

        results.append({
            "mutation": mutation["description"],
            "original": mutation["original"],
            "mutated": mutation["mutated"],
            "line": mutation["line"],
            "caught_by": catching_tests,
            "killed": len(catching_tests) > 0,
        })

    killed = sum(1 for r in results if r["killed"])
    mutation_score = round(killed / len(results), 2) if results else 0

    return {
        "total_mutations": len(results),
        "killed": killed,
        "survived": len(results) - killed,
        "mutation_score": mutation_score,
        "mutations": results,
    }


def generate_mutations(source: str, function_name: str) -> List[Dict]:
    """Generate simple operator mutations for a function."""
    mutations = []
    lines = source.splitlines()

    operator_swaps = [
        ("+", "-", "arithmetic: + → -"),
        ("-", "+", "arithmetic: - → +"),
        (">=", ">", "boundary: >= → >"),
        ("<=", "<", "boundary: <= → <"),
        ("==", "!=", "equality: == → !="),
        ("True", "False", "boolean: True → False"),
        ("and", "or", "logical: and → or"),
    ]

    node = find_function(source, function_name)
    for i in range(node.lineno - 1, node.end_lineno):
        line = lines[i]
        for original, replacement, description in operator_swaps:
            if original in line and len(mutations) < 8:
                mutated_line = line.replace(original, replacement, 1)
                mutations.append({
                    "line": i + 1,
                    "original": line.strip(),
                    "mutated": mutated_line.strip(),
                    "description": description,
                    "operator": original,
                })
                break

    return mutations[:6]  # Return max 6 mutations


def test_catches_mutation(test_code: str, mutation: Dict) -> bool:
    """Heuristic: check if a test likely catches a mutation."""
    # Simple heuristic based on assertion patterns and operators
    has_assertion = "assert" in test_code
    checks_value = any(op in test_code for op in ["==", "!=", ">=", "<=", ">", "<"])
    targets_mutated_op = mutation["operator"] in test_code

    return has_assertion and checks_value and not targets_mutated_op


@app.get("/stats")
def get_stats():
    """Get overall statistics about all projects."""
    total_files = 0
    total_functions = 0
    projects_data = []

    for folder, meta in PROJECTS.items():
        if not (BASE_DIR / folder).exists():
            continue
        files = list_project_files(folder)
        root = project_src_root(folder)
        func_count = 0
        for f in files:
            try:
                func_count += count_functions((root / f).read_text())
            except Exception:
                pass
        total_files += len(files)
        total_functions += func_count
        projects_data.append({
            "id": folder,
            "name": meta["name"],
            "kind": meta["kind"],
            "files": len(files),
            "functions": func_count,
        })

    return {
        "total_projects": len(projects_data),
        "total_files": total_files,
        "total_functions": total_functions,
        "projects": projects_data,
    }
