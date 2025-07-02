"""
OPRYXX Project Best Practices Analysis
"""

import os
from pathlib import Path

class ProjectAnalyzer:
    def __init__(self):
        self.project_root = Path(".")
        self.issues = []
        self.recommendations = []
        
    def analyze_project_structure(self):
        """Analyze current project structure"""
        print("📁 ANALYZING PROJECT STRUCTURE...")
        
        # Check for proper organization
        expected_dirs = ['ai', 'recovery', 'api', 'tests', 'docs', 'config']
        missing_dirs = []
        
        for dir_name in expected_dirs:
            if not (self.project_root / dir_name).exists():
                missing_dirs.append(dir_name)
        
        if missing_dirs:
            self.issues.append(f"Missing directories: {', '.join(missing_dirs)}")
        else:
            print("✅ Good directory structure")
    
    def analyze_testing(self):
        """Analyze testing coverage and structure"""
        print("🧪 ANALYZING TESTING...")
        
        test_files = list(self.project_root.glob("tests/**/*.py"))
        
        if len(test_files) < 5:
            self.issues.append("Insufficient test coverage")
            self.recommendations.append("Add comprehensive test suite")
        
        # Check for pytest.ini
        if not (self.project_root / "pytest.ini").exists():
            self.issues.append("Missing pytest configuration")
        
        print(f"Found {len(test_files)} test files")
    
    def analyze_ci_cd(self):
        """Analyze CI/CD setup"""
        print("🔄 ANALYZING CI/CD...")
        
        github_workflows = self.project_root / ".github" / "workflows"
        
        if not github_workflows.exists():
            self.issues.append("No CI/CD pipeline")
            self.recommendations.append("Add GitHub Actions workflow")
        else:
            workflow_files = list(github_workflows.glob("*.yml"))
            print(f"✅ Found {len(workflow_files)} workflow files")
    
    def analyze_documentation(self):
        """Analyze documentation quality"""
        print("📚 ANALYZING DOCUMENTATION...")
        
        doc_files = ['README.md', 'CONTRIBUTING.md', 'docs/API_DOCUMENTATION.md']
        missing_docs = []
        
        for doc in doc_files:
            if not (self.project_root / doc).exists():
                missing_docs.append(doc)
        
        if missing_docs:
            self.issues.append(f"Missing documentation: {', '.join(missing_docs)}")
        else:
            print("✅ Good documentation coverage")
    
    def analyze_security(self):
        """Analyze security practices"""
        print("🔒 ANALYZING SECURITY...")
        
        security_files = ['security/security_config.py', '.pre-commit-config.yaml']
        security_score = 0
        
        for file in security_files:
            if (self.project_root / file).exists():
                security_score += 1
        
        if security_score < len(security_files):
            self.issues.append("Incomplete security configuration")
        else:
            print("✅ Good security practices")
    
    def generate_recommendations(self):
        """Generate specific recommendations"""
        print("\n📋 GENERATING RECOMMENDATIONS...")
        
        recommendations = {
            "HIGH_PRIORITY": [
                "Add comprehensive error handling",
                "Implement request ID tracking",
                "Add performance monitoring",
                "Create deployment automation"
            ],
            "MEDIUM_PRIORITY": [
                "Improve test coverage to 90%+",
                "Add API rate limiting",
                "Implement caching strategy",
                "Add health check endpoints"
            ],
            "LOW_PRIORITY": [
                "Add code coverage reporting",
                "Implement feature flags",
                "Add monitoring dashboards",
                "Create user documentation"
            ]
        }
        
        return recommendations
    
    def run_analysis(self):
        """Run complete project analysis"""
        print("🔍 OPRYXX PROJECT ANALYSIS")
        print("=" * 50)
        
        self.analyze_project_structure()
        self.analyze_testing()
        self.analyze_ci_cd()
        self.analyze_documentation()
        self.analyze_security()
        
        recommendations = self.generate_recommendations()
        
        print(f"\n📊 ANALYSIS RESULTS:")
        print(f"Issues found: {len(self.issues)}")
        print(f"Recommendations: {len(self.recommendations)}")
        
        if self.issues:
            print(f"\n❌ ISSUES:")
            for issue in self.issues:
                print(f"  • {issue}")
        
        print(f"\n🎯 RECOMMENDATIONS:")
        for priority, items in recommendations.items():
            print(f"\n{priority}:")
            for item in items:
                print(f"  • {item}")
        
        return {
            'issues': self.issues,
            'recommendations': recommendations,
            'score': max(0, 100 - len(self.issues) * 10)
        }

def main():
    """Run project analysis"""
    analyzer = ProjectAnalyzer()
    results = analyzer.run_analysis()
    
    print(f"\n🏆 PROJECT SCORE: {results['score']}/100")
    
    if results['score'] >= 80:
        print("✅ EXCELLENT - Production ready")
    elif results['score'] >= 60:
        print("⚡ GOOD - Minor improvements needed")
    else:
        print("⚠️ NEEDS WORK - Address critical issues")

if __name__ == "__main__":
    main()