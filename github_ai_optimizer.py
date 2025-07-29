"""
GitHub AI Repository Optimizer
Advanced AI-powered repository enhancement and automation
"""
import os
import json
import subprocess
from pathlib import Path
import ast
import re

class GitHubAIOptimizer:
    def __init__(self):
        self.optimization_rules = {
            'python': self.optimize_python_project,
            'javascript': self.optimize_js_project,
            'typescript': self.optimize_ts_project,
            'java': self.optimize_java_project,
            'cpp': self.optimize_cpp_project
        }
    
    def analyze_code_quality(self, repo_path):
        """AI-powered code quality analysis"""
        quality_score = 100
        issues = []
        
        for file_path in Path(repo_path).rglob('*.py'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for code smells
                if len(content.split('\n')) > 1000:
                    issues.append(f"Large file: {file_path.name}")
                    quality_score -= 5
                
                # Check for proper documentation
                if 'def ' in content and '"""' not in content:
                    issues.append(f"Missing docstrings: {file_path.name}")
                    quality_score -= 3
                
                # Check for error handling
                if 'try:' not in content and 'except' not in content:
                    issues.append(f"No error handling: {file_path.name}")
                    quality_score -= 2
                    
            except Exception:
                continue
        
        return max(0, quality_score), issues
    
    def generate_smart_tests(self, repo_path):
        """Generate intelligent test files"""
        test_dir = Path(repo_path, 'tests')
        test_dir.mkdir(exist_ok=True)
        
        # Find Python files to test
        for py_file in Path(repo_path).rglob('*.py'):
            if 'test' not in py_file.name and py_file.parent.name != 'tests':
                try:
                    with open(py_file, 'r') as f:
                        content = f.read()
                    
                    # Extract functions
                    tree = ast.parse(content)
                    functions = [node.name for node in ast.walk(tree) 
                               if isinstance(node, ast.FunctionDef)]
                    
                    if functions:
                        test_content = f"""import unittest
from {py_file.stem} import *

class Test{py_file.stem.title()}(unittest.TestCase):
"""
                        for func in functions:
                            test_content += f"""
    def test_{func}(self):
        # TODO: Implement test for {func}
        pass
"""
                        test_content += """
if __name__ == '__main__':
    unittest.main()
"""
                        
                        test_file = test_dir / f'test_{py_file.stem}.py'
                        if not test_file.exists():
                            with open(test_file, 'w') as f:
                                f.write(test_content)
                                
                except Exception:
                    continue
    
    def optimize_python_project(self, repo_path):
        """Python-specific optimizations"""
        optimizations = []
        
        # Create virtual environment setup
        setup_py = Path(repo_path, 'setup.py')
        if not setup_py.exists():
            setup_content = '''from setuptools import setup, find_packages

setup(
    name="project",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[],
    python_requires=">=3.8",
)'''
            with open(setup_py, 'w') as f:
                f.write(setup_content)
            optimizations.append("Created setup.py")
        
        # Add requirements.txt if missing
        req_file = Path(repo_path, 'requirements.txt')
        if not req_file.exists():
            with open(req_file, 'w') as f:
                f.write("# Add your dependencies here\n")
            optimizations.append("Created requirements.txt")
        
        # Add pytest configuration
        pytest_ini = Path(repo_path, 'pytest.ini')
        if not pytest_ini.exists():
            pytest_content = """[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
"""
            with open(pytest_ini, 'w') as f:
                f.write(pytest_content)
            optimizations.append("Added pytest config")
        
        return optimizations
    
    def optimize_js_project(self, repo_path):
        """JavaScript-specific optimizations"""
        optimizations = []
        
        # Add package.json if missing
        package_json = Path(repo_path, 'package.json')
        if not package_json.exists():
            package_content = {
                "name": Path(repo_path).name,
                "version": "1.0.0",
                "description": "",
                "main": "index.js",
                "scripts": {
                    "start": "node index.js",
                    "test": "jest",
                    "dev": "nodemon index.js"
                },
                "devDependencies": {
                    "jest": "^29.0.0",
                    "nodemon": "^2.0.0"
                }
            }
            with open(package_json, 'w') as f:
                json.dump(package_content, f, indent=2)
            optimizations.append("Created package.json")
        
        # Add ESLint config
        eslint_config = Path(repo_path, '.eslintrc.json')
        if not eslint_config.exists():
            eslint_content = {
                "env": {"node": True, "es2021": True},
                "extends": ["eslint:recommended"],
                "rules": {
                    "no-console": "warn",
                    "no-unused-vars": "error"
                }
            }
            with open(eslint_config, 'w') as f:
                json.dump(eslint_content, f, indent=2)
            optimizations.append("Added ESLint config")
        
        return optimizations
    
    def optimize_ts_project(self, repo_path):
        """TypeScript-specific optimizations"""
        optimizations = []
        
        # Add tsconfig.json
        tsconfig = Path(repo_path, 'tsconfig.json')
        if not tsconfig.exists():
            tsconfig_content = {
                "compilerOptions": {
                    "target": "ES2020",
                    "module": "commonjs",
                    "outDir": "./dist",
                    "rootDir": "./src",
                    "strict": True,
                    "esModuleInterop": True
                },
                "include": ["src/**/*"],
                "exclude": ["node_modules", "dist"]
            }
            with open(tsconfig, 'w') as f:
                json.dump(tsconfig_content, f, indent=2)
            optimizations.append("Added TypeScript config")
        
        return optimizations
    
    def optimize_java_project(self, repo_path):
        """Java-specific optimizations"""
        optimizations = []
        
        # Add Maven pom.xml if missing
        pom_xml = Path(repo_path, 'pom.xml')
        if not pom_xml.exists():
            pom_content = '''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>project</artifactId>
    <version>1.0.0</version>
    <properties>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
    </properties>
</project>'''
            with open(pom_xml, 'w') as f:
                f.write(pom_content)
            optimizations.append("Added Maven config")
        
        return optimizations
    
    def optimize_cpp_project(self, repo_path):
        """C++ specific optimizations"""
        optimizations = []
        
        # Add CMakeLists.txt
        cmake_file = Path(repo_path, 'CMakeLists.txt')
        if not cmake_file.exists():
            cmake_content = '''cmake_minimum_required(VERSION 3.10)
project(Project)

set(CMAKE_CXX_STANDARD 17)

add_executable(main main.cpp)
'''
            with open(cmake_file, 'w') as f:
                f.write(cmake_content)
            optimizations.append("Added CMake config")
        
        return optimizations
    
    def create_automation_scripts(self, repo_path):
        """Create automation scripts for the repository"""
        scripts_dir = Path(repo_path, 'scripts')
        scripts_dir.mkdir(exist_ok=True)
        
        # Build script
        build_script = scripts_dir / 'build.py'
        build_content = '''#!/usr/bin/env python3
"""Automated build script"""
import subprocess
import sys

def build():
    print("🔨 Building project...")
    # Add build commands here
    print("✅ Build complete!")

if __name__ == "__main__":
    build()
'''
        with open(build_script, 'w') as f:
            f.write(build_content)
        
        # Deploy script
        deploy_script = scripts_dir / 'deploy.py'
        deploy_content = '''#!/usr/bin/env python3
"""Automated deployment script"""
import subprocess
import sys

def deploy():
    print("🚀 Deploying project...")
    # Add deployment commands here
    print("✅ Deployment complete!")

if __name__ == "__main__":
    deploy()
'''
        with open(deploy_script, 'w') as f:
            f.write(deploy_content)
    
    def optimize_repository(self, repo_path):
        """Apply comprehensive AI optimizations"""
        print(f"🤖 AI-optimizing {Path(repo_path).name}...")
        
        all_optimizations = []
        
        # Detect primary language
        languages = self.detect_languages(repo_path)
        
        # Apply language-specific optimizations
        for lang in languages:
            if lang in self.optimization_rules:
                opts = self.optimization_rules[lang](repo_path)
                all_optimizations.extend(opts)
        
        # Generate smart tests
        self.generate_smart_tests(repo_path)
        all_optimizations.append("Generated intelligent tests")
        
        # Create automation scripts
        self.create_automation_scripts(repo_path)
        all_optimizations.append("Created automation scripts")
        
        # Analyze code quality
        quality_score, issues = self.analyze_code_quality(repo_path)
        all_optimizations.append(f"Code quality: {quality_score}%")
        
        print(f"✅ Applied {len(all_optimizations)} optimizations")
        return all_optimizations
    
    def detect_languages(self, repo_path):
        """Detect programming languages in repository"""
        languages = []
        
        extensions = {
            '.py': 'python',
            '.js': 'javascript', 
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'cpp',
            '.hpp': 'cpp',
            '.h': 'cpp'
        }
        
        for file_path in Path(repo_path).rglob('*'):
            if file_path.suffix in extensions:
                lang = extensions[file_path.suffix]
                if lang not in languages:
                    languages.append(lang)
        
        return languages

def optimize_all_repos(base_path="C:\\GitHub-Pro"):
    """Optimize all repositories in the base path"""
    optimizer = GitHubAIOptimizer()
    
    for repo_dir in Path(base_path).iterdir():
        if repo_dir.is_dir() and (repo_dir / '.git').exists():
            try:
                optimizer.optimize_repository(repo_dir)
            except Exception as e:
                print(f"❌ Failed to optimize {repo_dir.name}: {e}")

if __name__ == "__main__":
    base_path = input("Repository base path (default C:\\GitHub-Pro): ") or "C:\\GitHub-Pro"
    optimize_all_repos(base_path)