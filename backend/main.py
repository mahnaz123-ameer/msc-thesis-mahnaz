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
import importlib.util
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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

PROJECTS = {
    "01_university_management": "University Management",
    "02_banking_system": "Banking System",
    "03_hospital_management": "Hospital Management",
    "04_ecommerce_system": "E-Commerce System",
    "05_ride_sharing": "Ride Sharing",
}


# ─── Helper: Load a module from file ─────────────────────────
def load_module(project: str, filename: str):
    file_path = BASE_DIR / project / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {filename}")
    spec = importlib.util.spec_from_file_location("module", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ─── Helper: Extract functions from a file ───────────────────
def get_functions_from_file(project: str, filename: str) -> List[Dict]:
    file_path = BASE_DIR / project / filename
    source = file_path.read_text()
    tree = ast.parse(source)
    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            args = [arg.arg for arg in node.args.args]
            docstring = ast.get_docstring(node) or ""
            functions.append({
                "name": node.name,
                "args": args,
                "docstring": docstring,
                "lineno": node.lineno,
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
    """List all research projects."""
    result = []
    for folder, name in PROJECTS.items():
        project_path = BASE_DIR / folder
        if project_path.exists():
            files = [f.name for f in project_path.glob("*.py") if f.name != "__init__.py"]
            result.append({
                "id": folder,
                "name": name,
                "files": files,
                "file_count": len(files),
            })
    return result


@app.get("/projects/{project}/files")
def list_files(project: str):
    """List Python files in a project."""
    project_path = BASE_DIR / project
    if not project_path.exists():
        raise HTTPException(status_code=404, detail="Project not found")
    files = [f.name for f in project_path.glob("*.py") if f.name != "__init__.py"]
    return {"project": project, "files": files}


@app.get("/projects/{project}/files/{filename}/functions")
def list_functions(project: str, filename: str):
    """List all functions in a file."""
    functions = get_functions_from_file(project, filename)
    return {"project": project, "file": filename, "functions": functions}


@app.get("/projects/{project}/files/{filename}/source")
def get_source(project: str, filename: str):
    """Get full source code of a file."""
    file_path = BASE_DIR / project / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return {"source": file_path.read_text()}


@app.get("/projects/{project}/files/{filename}/functions/{function_name}/source")
def get_function_source(project: str, filename: str, function_name: str):
    """Get source code of a specific function."""
    file_path = BASE_DIR / project / filename
    source = file_path.read_text()
    tree = ast.parse(source)
    lines = source.splitlines()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            start = node.lineno - 1
            end = node.end_lineno
            func_source = "\n".join(lines[start:end])
            return {"function": function_name, "source": func_source}
    raise HTTPException(status_code=404, detail=f"Function {function_name} not found")


@app.get("/projects/{project}/files/{filename}/functions/{function_name}/ast")
def get_ast(project: str, filename: str, function_name: str):
    """Get AST tree of a specific function."""
    file_path = BASE_DIR / project / filename
    source = file_path.read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            ast_dict = ast_to_dict(node)
            # Also build a simplified tree for visualization
            simplified = build_simplified_ast(node)
            return {
                "function": function_name,
                "ast": ast_dict,
                "simplified": simplified,
            }
    raise HTTPException(status_code=404, detail=f"Function not found")


def build_simplified_ast(node, depth=0):
    """Build a simplified AST tree for frontend visualization."""
    if depth > 6:
        return None
    name = type(node).__name__
    label = name
    if isinstance(node, ast.FunctionDef):
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


class RunRequest(BaseModel):
    args: List[Any] = []
    kwargs: Dict[str, Any] = {}


@app.post("/projects/{project}/files/{filename}/functions/{function_name}/run")
def run_function(project: str, filename: str, function_name: str, body: RunRequest):
    """Run a function with provided arguments."""
    try:
        module = load_module(project, filename)
        func = getattr(module, function_name, None)
        if func is None:
            raise HTTPException(status_code=404, detail=f"Function {function_name} not found")

        # Parse args from string if needed
        parsed_args = []
        for arg in body.args:
            if isinstance(arg, str):
                try:
                    parsed_args.append(json.loads(arg))
                except Exception:
                    parsed_args.append(arg)
            else:
                parsed_args.append(arg)

        result = func(*parsed_args, **body.kwargs)
        return {"success": True, "result": result, "type": type(result).__name__}
    except HTTPException:
        raise
    except Exception as e:
        return {"success": False, "error": str(e), "type": type(e).__name__}


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
    file_path = BASE_DIR / body.project / body.filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    source = file_path.read_text()

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

    in_function = False
    for i, line in enumerate(lines):
        if f"def {function_name}" in line:
            in_function = True
        if in_function and line.strip() == "" and i > 0:
            if not lines[i-1].strip().startswith("def"):
                in_function = False

        if in_function:
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

    for folder, name in PROJECTS.items():
        project_path = BASE_DIR / folder
        if project_path.exists():
            files = list(project_path.glob("*.py"))
            files = [f for f in files if f.name != "__init__.py"]
            func_count = 0
            for f in files:
                try:
                    source = f.read_text()
                    tree = ast.parse(source)
                    func_count += sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
                except Exception:
                    pass
            total_files += len(files)
            total_functions += func_count
            projects_data.append({
                "id": folder,
                "name": name,
                "files": len(files),
                "functions": func_count,
            })

    return {
        "total_projects": len(projects_data),
        "total_files": total_files,
        "total_functions": total_functions,
        "projects": projects_data,
    }
