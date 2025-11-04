#!/usr/bin/env python3
"""
Analyzes a project directory to suggest CLAUDE.md content.
Detects frameworks, languages, patterns, and generates recommendations.
"""

import os
import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Optional
import argparse

class ProjectAnalyzer:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.findings = {
            "languages": set(),
            "frameworks": set(),
            "build_tools": set(),
            "test_frameworks": set(),
            "databases": set(),
            "dependencies": {},
            "scripts": {},
            "structure": {}
        }
        
    def analyze(self) -> Dict:
        """Run all analysis methods"""
        self.detect_languages()
        self.detect_package_files()
        self.analyze_project_structure()
        self.detect_docker()
        self.detect_ci_cd()
        return self.generate_claude_md()
    
    def detect_languages(self):
        """Detect programming languages used"""
        extensions_map = {
            ".js": "JavaScript",
            ".jsx": "React",
            ".ts": "TypeScript", 
            ".tsx": "TypeScript/React",
            ".py": "Python",
            ".java": "Java",
            ".go": "Go",
            ".rs": "Rust",
            ".rb": "Ruby",
            ".php": "PHP",
            ".cs": "C#",
            ".swift": "Swift",
            ".kt": "Kotlin"
        }
        
        for ext, lang in extensions_map.items():
            if list(self.project_path.rglob(f"*{ext}")):
                self.findings["languages"].add(lang)
    
    def detect_package_files(self):
        """Analyze package.json, requirements.txt, etc."""
        # Node.js projects
        package_json_path = self.project_path / "package.json"
        if package_json_path.exists():
            with open(package_json_path) as f:
                package_data = json.load(f)
                
            # Detect scripts
            if "scripts" in package_data:
                self.findings["scripts"] = package_data["scripts"]
                
            # Detect dependencies and frameworks
            deps = {**package_data.get("dependencies", {}), 
                   **package_data.get("devDependencies", {})}
            
            # Framework detection
            framework_indicators = {
                "react": "React",
                "next": "Next.js",
                "vue": "Vue.js",
                "angular": "Angular",
                "express": "Express.js",
                "fastify": "Fastify",
                "nestjs": "NestJS",
                "@remix-run": "Remix",
                "gatsby": "Gatsby",
                "astro": "Astro"
            }
            
            for dep in deps:
                for indicator, framework in framework_indicators.items():
                    if indicator in dep.lower():
                        self.findings["frameworks"].add(framework)
            
            # Test framework detection
            test_indicators = {
                "jest": "Jest",
                "mocha": "Mocha",
                "vitest": "Vitest",
                "cypress": "Cypress",
                "playwright": "Playwright",
                "@testing-library": "React Testing Library"
            }
            
            for dep in deps:
                for indicator, test_framework in test_indicators.items():
                    if indicator in dep.lower():
                        self.findings["test_frameworks"].add(test_framework)
            
            # Database/ORM detection
            db_indicators = {
                "mongoose": "MongoDB with Mongoose",
                "prisma": "Prisma ORM",
                "typeorm": "TypeORM",
                "sequelize": "Sequelize",
                "knex": "Knex.js",
                "pg": "PostgreSQL",
                "mysql": "MySQL",
                "redis": "Redis"
            }
            
            for dep in deps:
                for indicator, db in db_indicators.items():
                    if indicator in dep.lower():
                        self.findings["databases"].add(db)
        
        # Python projects
        requirements_path = self.project_path / "requirements.txt"
        if requirements_path.exists():
            with open(requirements_path) as f:
                requirements = f.read()
                
            python_frameworks = {
                "django": "Django",
                "flask": "Flask",
                "fastapi": "FastAPI",
                "pytest": "pytest",
                "unittest": "unittest",
                "sqlalchemy": "SQLAlchemy",
                "pandas": "Pandas",
                "numpy": "NumPy",
                "tensorflow": "TensorFlow",
                "torch": "PyTorch",
                "scikit-learn": "scikit-learn"
            }
            
            for framework, name in python_frameworks.items():
                if framework in requirements.lower():
                    self.findings["frameworks"].add(name)
        
        # Look for Pipfile, poetry.lock, etc.
        if (self.project_path / "Pipfile").exists():
            self.findings["build_tools"].add("Pipenv")
        if (self.project_path / "poetry.lock").exists():
            self.findings["build_tools"].add("Poetry")
        if (self.project_path / "pnpm-lock.yaml").exists():
            self.findings["build_tools"].add("pnpm")
        if (self.project_path / "yarn.lock").exists():
            self.findings["build_tools"].add("Yarn")
    
    def analyze_project_structure(self):
        """Analyze directory structure"""
        common_dirs = {
            "src": "Source code directory",
            "tests": "Test files",
            "test": "Test files",
            "__tests__": "Test files",
            "docs": "Documentation",
            "public": "Public assets",
            "static": "Static files",
            "assets": "Asset files",
            "components": "Component files",
            "pages": "Page components",
            "routes": "Route definitions",
            "api": "API endpoints",
            "models": "Data models",
            "controllers": "Controllers",
            "services": "Service layer",
            "utils": "Utility functions",
            "lib": "Library code",
            "config": "Configuration files"
        }
        
        for dir_name, description in common_dirs.items():
            if (self.project_path / dir_name).exists():
                self.findings["structure"][dir_name] = description
    
    def detect_docker(self):
        """Check for Docker configuration"""
        if (self.project_path / "Dockerfile").exists():
            self.findings["build_tools"].add("Docker")
        if (self.project_path / "docker-compose.yml").exists() or \
           (self.project_path / "docker-compose.yaml").exists():
            self.findings["build_tools"].add("Docker Compose")
    
    def detect_ci_cd(self):
        """Detect CI/CD configuration"""
        ci_files = {
            ".github/workflows": "GitHub Actions",
            ".gitlab-ci.yml": "GitLab CI",
            ".circleci": "CircleCI",
            "Jenkinsfile": "Jenkins",
            ".travis.yml": "Travis CI",
            "azure-pipelines.yml": "Azure DevOps"
        }
        
        for ci_path, ci_name in ci_files.items():
            if (self.project_path / ci_path).exists():
                self.findings["build_tools"].add(ci_name)
    
    def generate_claude_md(self) -> str:
        """Generate CLAUDE.md content based on analysis"""
        content = []
        
        # Header
        project_name = self.project_path.name
        content.append(f"# Project: {project_name} - [Add brief description]")
        content.append("")
        
        # Architecture section
        content.append("## Architecture")
        
        if self.findings["frameworks"]:
            frameworks = ", ".join(sorted(self.findings["frameworks"]))
            content.append(f"- Framework: {frameworks}")
        
        if self.findings["languages"]:
            languages = ", ".join(sorted(self.findings["languages"]))
            content.append(f"- Languages: {languages}")
        
        if self.findings["databases"]:
            databases = ", ".join(sorted(self.findings["databases"]))
            content.append(f"- Database: {databases}")
        else:
            content.append("- Database: [Specify database and ORM]")
        
        if self.findings["test_frameworks"]:
            test_frameworks = ", ".join(sorted(self.findings["test_frameworks"]))
            content.append(f"- Testing: {test_frameworks}")
        
        content.append("- State management: [Specify approach]")
        content.append("")
        
        # Development commands
        content.append("## Development Commands")
        
        if self.findings["scripts"]:
            # Common script patterns
            script_descriptions = {
                "dev": "Start development server",
                "start": "Start application",
                "build": "Build for production",
                "test": "Run test suite",
                "lint": "Run linter",
                "format": "Format code",
                "test:watch": "Run tests in watch mode",
                "test:coverage": "Run tests with coverage"
            }
            
            for script, command in self.findings["scripts"].items():
                desc = script_descriptions.get(script, "[Add description]")
                # Use npm run for Node projects
                if "package.json" in str(package_json_path):
                    content.append(f"- `npm run {script}`: {desc}")
                else:
                    content.append(f"- `{command}`: {desc}")
        else:
            content.append("- `npm run dev`: Start development server")
            content.append("- `npm run build`: Build for production")
            content.append("- `npm run test`: Run test suite")
        
        content.append("")
        
        # Code style guidelines
        content.append("## Code Style Guidelines")
        
        if "TypeScript" in self.findings["languages"]:
            content.append("- Use TypeScript for all new files")
            content.append("- Enable strict mode")
        
        if "React" in str(self.findings["frameworks"]):
            content.append("- Functional components with hooks")
            content.append("- Co-locate styles with components")
        
        content.append("- [Add more style guidelines]")
        content.append("")
        
        # Project structure (if detected)
        if self.findings["structure"]:
            content.append("## Project Structure")
            for dir_name, description in sorted(self.findings["structure"].items()):
                content.append(f"- `/{dir_name}`: {description}")
            content.append("")
        
        # Testing conventions
        content.append("## Testing Conventions")
        content.append("- Unit tests: [Specify location and naming]")
        content.append("- Integration tests: [Specify location]")
        content.append("- [Add test execution strategy]")
        content.append("")
        
        # Workflow rules
        content.append("## Workflow Rules")
        content.append("- Branch naming: feature/*, fix/*, hotfix/*")
        content.append("- Commit format: [Specify format]")
        content.append("- PR requirements: [List requirements]")
        content.append("")
        
        # Add detected build tools
        if self.findings["build_tools"]:
            content.append("## Build Tools")
            for tool in sorted(self.findings["build_tools"]):
                content.append(f"- {tool}")
            content.append("")
        
        # Placeholders for important sections
        content.append("## TODO: Complete these sections")
        content.append("- [ ] Add project-specific gotchas")
        content.append("- [ ] Document security patterns")
        content.append("- [ ] Specify performance targets")
        content.append("- [ ] Add deployment process")
        content.append("- [ ] Document environment variables")
        
        return "\n".join(content)

def main():
    parser = argparse.ArgumentParser(
        description="Analyze a project and generate CLAUDE.md suggestions"
    )
    parser.add_argument(
        "path",
        help="Path to the project directory",
        default=".",
        nargs="?"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: print to stdout)",
        default=None
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.path):
        print(f"Error: Path '{args.path}' does not exist", file=sys.stderr)
        sys.exit(1)
    
    print(f"Analyzing project at: {args.path}", file=sys.stderr)
    
    analyzer = ProjectAnalyzer(args.path)
    claude_md_content = analyzer.analyze()
    
    if args.output:
        with open(args.output, "w") as f:
            f.write(claude_md_content)
        print(f"CLAUDE.md content written to: {args.output}", file=sys.stderr)
    else:
        print(claude_md_content)
    
    print("\n✅ Analysis complete! Remember to:", file=sys.stderr)
    print("1. Fill in the [bracketed] placeholders", file=sys.stderr)
    print("2. Add project-specific details", file=sys.stderr)
    print("3. Test with Claude Code", file=sys.stderr)
    print("4. Update regularly as project evolves", file=sys.stderr)

if __name__ == "__main__":
    main()
