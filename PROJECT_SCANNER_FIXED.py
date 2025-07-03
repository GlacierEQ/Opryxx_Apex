#!/usr/bin/env python3
"""
OPRYXX Project Scanner & Optimizer
Scans entire project for best practices, architecture, and optimization opportunities
"""

import os
import ast
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict

@dataclass
class ProjectMetrics:
    total_files: int = 0
    python_files: int = 0
    lines_of_code: int = 0
    functions: int = 0
    classes: int = 0
    imports: List[str] = None
    complexity_score: float = 0.0
    test_coverage: float = 0.0
    
    def __post_init__(self):
        if self.imports is None:
            self.imports = []

class ProjectScanner:
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.metrics = ProjectMetrics()
        self.issues = []
        self.recommendations = []
        
    def scan_project(self) -> Dict[str, Any]:
        """Complete project scan"""
        print("OPRYXX PROJECT SCANNER")
        print("=" * 40)
        
        self._scan_structure()
        self._analyze_code_quality()
        self._check_architecture()
        self._evaluate_performance()
        self._assess_ai_capabilities()
        self._review_automation()
        self._check_gpu_npu_priority()
        
        return self._generate_report()
    
    def _scan_structure(self):
        """Scan project structure"""
        print("[INFO] Scanning project structure...")
        
        for file_path in self.project_path.rglob("*"):
            if file_path.is_file():
                self.metrics.total_files += 1
                
                if file_path.suffix == '.py':
                    self.metrics.python_files += 1
                    self._analyze_python_file(file_path)
    
    def _analyze_python_file(self, file_path: Path):
        """Analyze individual Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.metrics.lines_of_code += len(content.splitlines())
                
                # Parse AST
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        self.metrics.functions += 1
                    elif isinstance(node, ast.ClassDef):
                        self.metrics.classes += 1
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            self.metrics.imports.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            self.metrics.imports.append(node.module)
                            
        except Exception as e:
            self.issues.append(f"Failed to parse {file_path}: {e}")
    
    def _analyze_code_quality(self):
        """Analyze code quality metrics"""
        print("[INFO] Analyzing code quality...")
        
        # Check for best practices
        required_files = [
            'requirements.txt', 'README.md', '.gitignore',
            'pyproject.toml', 'setup.py'
        ]
        
        for req_file in required_files:
            if not (self.project_path / req_file).exists():
                self.issues.append(f"Missing {req_file}")
        
        # Check for proper structure
        core_dirs = ['core', 'gui', 'tests', 'scripts']
        for core_dir in core_dirs:
            if not (self.project_path / core_dir).exists():
                self.issues.append(f"Missing {core_dir} directory")
        
        # Calculate complexity score
        if self.metrics.python_files > 0:
            self.metrics.complexity_score = (
                self.metrics.functions / self.metrics.python_files +
                self.metrics.classes / self.metrics.python_files
            )
    
    def _check_architecture(self):
        """Check architecture patterns"""
        print("[INFO] Checking architecture...")
        
        # Check for proper separation of concerns
        architecture_score = 0
        
        # Core modules check
        core_modules = [
            'performance_monitor.py', 'memory_optimizer.py',
            'gpu_acceleration.py', 'resilience_system.py'
        ]
        
        for module in core_modules:
            if (self.project_path / 'core' / module).exists():
                architecture_score += 1
        
        # GUI separation
        gui_modules = ['unified_gui.py', 'web_interface.py']
        for module in gui_modules:
            if (self.project_path / 'gui' / module).exists():
                architecture_score += 1
        
        if architecture_score >= 5:
            self.recommendations.append("[OK] Good architectural separation")
        else:
            self.issues.append("[ERROR] Poor architectural separation")
    
    def _evaluate_performance(self):
        """Evaluate performance optimization"""
        print("[INFO] Evaluating performance...")
        
        performance_features = [
            ('GPU acceleration', 'gpu_acceleration.py'),
            ('Memory optimization', 'memory_optimizer.py'),
            ('Performance monitoring', 'performance_monitor.py'),
            ('Caching system', 'caching.py'),
            ('Async operations', 'async_utils.py')
        ]
        
        for feature, filename in performance_features:
            if any(self.project_path.rglob(filename)):
                self.recommendations.append(f"[OK] {feature} implemented")
            else:
                self.issues.append(f"[ERROR] Missing {feature}")
    
    def _assess_ai_capabilities(self):
        """Assess AI and intelligence features"""
        print("[INFO] Assessing AI capabilities...")
        
        ai_imports = [
            'torch', 'tensorflow', 'sklearn', 'numpy',
            'pandas', 'scipy', 'transformers'
        ]
        
        found_ai = any(imp in self.metrics.imports for imp in ai_imports)
        
        if found_ai:
            self.recommendations.append("[OK] AI/ML libraries detected")
        else:
            self.issues.append("[ERROR] Limited AI capabilities")
    
    def _review_automation(self):
        """Review automation capabilities"""
        print("[INFO] Reviewing automation...")
        
        automation_files = [
            'auto_optimizer.py', 'background_monitor.py',
            'scheduler.py', 'task_manager.py'
        ]
        
        automation_score = sum(1 for f in automation_files 
                             if any(self.project_path.rglob(f)))
        
        if automation_score >= 2:
            self.recommendations.append("[OK] Good automation coverage")
        else:
            self.issues.append("[ERROR] Limited automation")
    
    def _check_gpu_npu_priority(self):
        """Check GPU/NPU prioritization"""
        print("[INFO] Checking GPU/NPU priority...")
        
        gpu_files = list(self.project_path.rglob("*gpu*.py"))
        npu_files = list(self.project_path.rglob("*npu*.py"))
        
        if gpu_files:
            self.recommendations.append(f"[OK] GPU support: {len(gpu_files)} files")
        else:
            self.issues.append("[ERROR] No GPU-specific files")
            
        if npu_files:
            self.recommendations.append(f"[OK] NPU support: {len(npu_files)} files")
        else:
            self.issues.append("[ERROR] No NPU-specific files")
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive report"""
        print("\n[INFO] GENERATING REPORT...")
        
        report = {
            'project_metrics': asdict(self.metrics),
            'issues': self.issues,
            'recommendations': self.recommendations,
            'overall_score': self._calculate_overall_score(),
            'priority_actions': self._get_priority_actions()
        }
        
        return report
    
    def _calculate_overall_score(self) -> float:
        """Calculate overall project score"""
        total_checks = len(self.issues) + len(self.recommendations)
        if total_checks == 0:
            return 0.0
        
        positive_score = len(self.recommendations)
        return (positive_score / total_checks) * 100
    
    def _get_priority_actions(self) -> List[str]:
        """Get priority actions for improvement"""
        actions = []
        
        # Critical issues first
        if "Missing core directory" in str(self.issues):
            actions.append("[CRITICAL] Restructure project architecture")
        
        if "[ERROR] No GPU-specific files" in str(self.issues):
            actions.append("[HIGH] Implement GPU acceleration")
            
        if "[ERROR] Limited AI capabilities" in str(self.issues):
            actions.append("[HIGH] Add AI/ML capabilities")
            
        if "[ERROR] Limited automation" in str(self.issues):
            actions.append("[MEDIUM] Enhance automation")
        
        return actions

def main():
    scanner = ProjectScanner()
    report = scanner.scan_project()
    
    # Print detailed report
    print("\n" + "=" * 50)
    print("PROJECT ANALYSIS REPORT")
    print("=" * 50)
    
    # Metrics
    metrics = report['project_metrics']
    print(f"Total Files: {metrics['total_files']}")
    print(f"Python Files: {metrics['python_files']}")
    print(f"Lines of Code: {metrics['lines_of_code']}")
    print(f"Functions: {metrics['functions']}")
    print(f"Classes: {metrics['classes']}")
    print(f"Unique Imports: {len(set(metrics['imports']))}")
    print(f"Overall Score: {report['overall_score']:.1f}%")
    
    # Issues
    print(f"\nISSUES ({len(report['issues'])}):")
    for issue in report['issues']:
        print(f"  {issue}")
    
    # Recommendations
    print(f"\nSTRENGTHS ({len(report['recommendations'])}):")
    for rec in report['recommendations']:
        print(f"  {rec}")
    
    # Priority Actions
    print(f"\nPRIORITY ACTIONS:")
    for action in report['priority_actions']:
        print(f"  {action}")
    
    # Save report
    with open('PROJECT_ANALYSIS_REPORT.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nReport saved to: PROJECT_ANALYSIS_REPORT.json")
    
    return report

if __name__ == "__main__":
    main()