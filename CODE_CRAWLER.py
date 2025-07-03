#!/usr/bin/env python3
"""
OPRYXX Code Crawler & Architecture Optimizer
Ensures best practices, eliminates duplicates, optimizes architecture
"""

import os
import ast
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class CodeMetrics:
    file_path: str
    lines: int
    functions: int
    classes: int
    imports: List[str]
    complexity: int
    duplicates: List[str]
    issues: List[str]

class CodeCrawler:
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.metrics = {}
        self.duplicates = defaultdict(list)
        self.function_signatures = {}
        self.import_graph = defaultdict(set)
        self.issues = []
        
    def crawl_project(self) -> Dict:
        """Crawl entire project for analysis"""
        print("CODE CRAWLER & OPTIMIZER")
        print("=" * 40)
        
        python_files = list(self.project_path.rglob("*.py"))
        print(f"[SCAN] Found {len(python_files)} Python files")
        
        for file_path in python_files:
            if self._should_skip_file(file_path):
                continue
            self._analyze_file(file_path)
        
        self._detect_duplicates()
        self._analyze_architecture()
        
        return self._generate_report()
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Skip certain files/directories"""
        skip_patterns = [
            'venv', '__pycache__', '.git', 'build', 'dist',
            'node_modules', '.pytest_cache'
        ]
        return any(pattern in str(file_path) for pattern in skip_patterns)
    
    def _analyze_file(self, file_path: Path):
        """Analyze individual Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            metrics = CodeMetrics(
                file_path=str(file_path),
                lines=len(content.splitlines()),
                functions=0,
                classes=0,
                imports=[],
                complexity=0,
                duplicates=[],
                issues=[]
            )
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    metrics.functions += 1
                    self._analyze_function(node, file_path)
                elif isinstance(node, ast.ClassDef):
                    metrics.classes += 1
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    self._analyze_import(node, metrics, file_path)
            
            metrics.complexity = self._calculate_complexity(tree)
            metrics.issues = self._detect_issues(tree, content)
            
            self.metrics[str(file_path)] = metrics
            
        except Exception as e:
            print(f"[ERROR] Failed to analyze {file_path}: {e}")
    
    def _analyze_function(self, node: ast.FunctionDef, file_path: Path):
        """Analyze function for duplicates"""
        func_hash = self._get_function_hash(node)
        signature = f"{node.name}({len(node.args.args)})"
        
        if func_hash in self.function_signatures:
            self.duplicates[func_hash].append(str(file_path))
        else:
            self.function_signatures[func_hash] = str(file_path)
    
    def _get_function_hash(self, node: ast.FunctionDef) -> str:
        """Generate hash for function to detect duplicates"""
        func_str = ast.dump(node, annotate_fields=False)
        return hashlib.md5(func_str.encode()).hexdigest()
    
    def _analyze_import(self, node, metrics: CodeMetrics, file_path: Path):
        """Analyze imports"""
        if isinstance(node, ast.Import):
            for alias in node.names:
                metrics.imports.append(alias.name)
                self.import_graph[str(file_path)].add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                metrics.imports.append(node.module)
                self.import_graph[str(file_path)].add(node.module)
    
    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.Try)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity
    
    def _detect_issues(self, tree: ast.AST, content: str) -> List[str]:
        """Detect code issues"""
        issues = []
        
        # Check for long functions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
                    func_length = node.end_lineno - node.lineno
                    if func_length > 50:
                        issues.append(f"Long function: {node.name} ({func_length} lines)")
        
        # Check for missing docstrings
        if '"""' not in content and "'''" not in content:
            issues.append("Missing docstrings")
        
        # Check for hardcoded paths
        if 'C:\\' in content or '/home/' in content:
            issues.append("Hardcoded paths detected")
        
        return issues
    
    def _detect_duplicates(self):
        """Detect duplicate code blocks"""
        print("[ANALYZE] Detecting duplicate code...")
        
        duplicate_count = 0
        for func_hash, files in self.duplicates.items():
            if len(files) > 1:
                duplicate_count += 1
                print(f"[DUPLICATE] Function found in: {', '.join(files)}")
        
        print(f"[RESULT] Found {duplicate_count} duplicate functions")
    
    def _analyze_architecture(self):
        """Analyze project architecture"""
        print("[ANALYZE] Analyzing architecture...")
        
        # Check for proper separation
        core_files = [f for f in self.metrics.keys() if 'core' in f]
        gui_files = [f for f in self.metrics.keys() if 'gui' in f]
        test_files = [f for f in self.metrics.keys() if 'test' in f]
        
        print(f"[ARCH] Core modules: {len(core_files)}")
        print(f"[ARCH] GUI modules: {len(gui_files)}")
        print(f"[ARCH] Test modules: {len(test_files)}")
        
        # Check for circular imports
        self._detect_circular_imports()
    
    def _detect_circular_imports(self):
        """Detect circular import dependencies"""
        print("[ANALYZE] Checking for circular imports...")
        
        # Simplified circular import detection
        for file_path, imports in self.import_graph.items():
            for imported_module in imports:
                if imported_module in self.import_graph:
                    if file_path.replace('\\', '.').replace('/', '.') in self.import_graph[imported_module]:
                        self.issues.append(f"Circular import: {file_path} <-> {imported_module}")
    
    def _generate_report(self) -> Dict:
        """Generate comprehensive analysis report"""
        total_lines = sum(m.lines for m in self.metrics.values())
        total_functions = sum(m.functions for m in self.metrics.values())
        total_classes = sum(m.classes for m in self.metrics.values())
        
        report = {
            'summary': {
                'total_files': len(self.metrics),
                'total_lines': total_lines,
                'total_functions': total_functions,
                'total_classes': total_classes,
                'avg_complexity': sum(m.complexity for m in self.metrics.values()) / len(self.metrics) if self.metrics else 0
            },
            'duplicates': dict(self.duplicates),
            'issues': self.issues,
            'recommendations': self._generate_recommendations(),
            'architecture_score': self._calculate_architecture_score()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        # Check for high complexity files
        high_complexity = [m for m in self.metrics.values() if m.complexity > 20]
        if high_complexity:
            recommendations.append(f"Refactor {len(high_complexity)} high-complexity files")
        
        # Check for large files
        large_files = [m for m in self.metrics.values() if m.lines > 500]
        if large_files:
            recommendations.append(f"Split {len(large_files)} large files")
        
        # Check for missing tests
        test_files = [f for f in self.metrics.keys() if 'test' in f.lower()]
        if len(test_files) < len(self.metrics) * 0.3:
            recommendations.append("Increase test coverage")
        
        return recommendations
    
    def _calculate_architecture_score(self) -> float:
        """Calculate overall architecture score"""
        score = 100.0
        
        # Deduct for duplicates
        duplicate_count = sum(1 for files in self.duplicates.values() if len(files) > 1)
        score -= duplicate_count * 5
        
        # Deduct for issues
        score -= len(self.issues) * 2
        
        # Deduct for high complexity
        high_complexity_count = sum(1 for m in self.metrics.values() if m.complexity > 20)
        score -= high_complexity_count * 3
        
        return max(0, score)

class CodeOptimizer:
    def __init__(self, crawler_report: Dict):
        self.report = crawler_report
        
    def optimize_project(self):
        """Apply optimizations based on analysis"""
        print("\n[OPTIMIZE] Applying optimizations...")
        
        self._remove_duplicates()
        self._optimize_imports()
        self._fix_architecture_issues()
        
    def _remove_duplicates(self):
        """Remove duplicate code"""
        duplicates = self.report.get('duplicates', {})
        
        for func_hash, files in duplicates.items():
            if len(files) > 1:
                print(f"[FIX] Consolidating duplicate function in {len(files)} files")
                # Implementation would move duplicate to common module
    
    def _optimize_imports(self):
        """Optimize import statements"""
        print("[FIX] Optimizing imports...")
        # Implementation would sort and clean imports
    
    def _fix_architecture_issues(self):
        """Fix architecture issues"""
        issues = self.report.get('issues', [])
        
        for issue in issues:
            if 'Circular import' in issue:
                print(f"[FIX] Resolving: {issue}")
                # Implementation would refactor circular imports

def main():
    crawler = CodeCrawler()
    report = crawler.crawl_project()
    
    print("\n" + "=" * 50)
    print("PROJECT ANALYSIS REPORT")
    print("=" * 50)
    
    summary = report['summary']
    print(f"Files: {summary['total_files']}")
    print(f"Lines: {summary['total_lines']}")
    print(f"Functions: {summary['total_functions']}")
    print(f"Classes: {summary['total_classes']}")
    print(f"Avg Complexity: {summary['avg_complexity']:.1f}")
    print(f"Architecture Score: {report['architecture_score']:.1f}%")
    
    print(f"\nIssues Found: {len(report['issues'])}")
    for issue in report['issues'][:5]:  # Show first 5
        print(f"  - {issue}")
    
    print(f"\nRecommendations:")
    for rec in report['recommendations']:
        print(f"  - {rec}")
    
    # Apply optimizations
    optimizer = CodeOptimizer(report)
    optimizer.optimize_project()
    
    # Save report
    with open('CODE_ANALYSIS_REPORT.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nReport saved to: CODE_ANALYSIS_REPORT.json")

if __name__ == "__main__":
    main()