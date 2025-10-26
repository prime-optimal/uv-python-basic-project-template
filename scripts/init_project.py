#!/usr/bin/env python3
"""
Project initialization script for Python repository template.

This script provides an interactive CLI to set up a new Python project
with different structure options and integrates Towncrier for changelog management.
"""

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional


class ProjectInitializer:
    """Handles the project initialization process."""

    def __init__(self):
        self.project_dir = Path.cwd()
        self.sentinel_file = self.project_dir / ".project_initialized"

    def run(self) -> None:
        """Main entry point for the initialization process."""
        print("🚀 Python Project Initializer")
        print("=" * 40)

        # Check if already initialized
        if self.is_already_initialized():
            print("✅ Project appears to be already initialized.")
            if not self.confirm("Do you want to re-initialize anyway?"):
                return

        # Get project configuration
        config = self.gather_project_config()
        if not config:
            print("❌ Initialization cancelled.")
            return

        # Initialize the project
        self.initialize_project(config)

        print("\n🎉 Project initialization complete!")
        self.print_next_steps(config)

    def is_already_initialized(self) -> bool:
        """Check if project has already been initialized."""
        return (
            self.sentinel_file.exists()
            or (self.project_dir / "pyproject.toml").exists()
            and self.get_project_name() != "python-repo-template"
        )

    def get_project_name(self) -> str:
        """Extract project name from pyproject.toml if it exists."""
        pyproject_path = self.project_dir / "pyproject.toml"
        if not pyproject_path.exists():
            return ""

        try:
            with open(pyproject_path, "r") as f:
                content = f.read()
                # Simple regex to extract name from [project] section
                match = re.search(
                    r'^name\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE
                )
                if match:
                    return match.group(1)
        except Exception:
            pass
        return ""

    def confirm(self, message: str) -> bool:
        """Ask for user confirmation."""
        while True:
            response = input(f"{message} [y/N]: ").strip().lower()
            if response in ("y", "yes"):
                return True
            elif response in ("n", "no", ""):
                return False
            else:
                print("Please enter 'y' or 'n'.")

    def gather_project_config(self) -> Optional[Dict[str, str]]:
        """Gather project configuration from user input."""
        config = {}

        # Project name
        default_name = self.suggest_project_name()
        config["name"] = self.prompt_with_default("Project name", default_name).strip()
        if not config["name"]:
            print("❌ Project name is required.")
            return None

        # Package name (if different from project name)
        package_suggestion = self.slugify(config["name"])
        config["package_name"] = self.prompt_with_default(
            "Package name (leave empty to use slugified project name)",
            package_suggestion,
            allow_empty=True,
        ).strip()
        if not config["package_name"]:
            config["package_name"] = package_suggestion

        # Project structure
        print("\nAvailable project structures:")
        print("  1. default - Simple script-based project")
        print("  2. package  - Package-based project with src/ layout")
        print("  3. library  - Library-style project with full structure")

        while True:
            structure = input("Choose structure (1-3) [1]: ").strip()
            if not structure:
                structure = "1"
            if structure in ("1", "2", "3"):
                break
            print("Please enter 1, 2, or 3.")

        structure_map = {"1": "default", "2": "package", "3": "library"}
        config["structure"] = structure_map[structure]

        # Python version
        config["python_version"] = self.get_python_version()

        # Author information
        config["author"] = self.prompt_with_default("Author name", "").strip()

        config["email"] = self.prompt_with_default(
            "Author email", "", allow_empty=True
        ).strip()

        # Project description
        config["description"] = self.prompt_with_default(
            "Project description", ""
        ).strip()

        return config

    def suggest_project_name(self) -> str:
        """Suggest a project name based on current directory."""
        return self.project_dir.name.replace("-", " ").replace("_", " ").title()

    def prompt_with_default(
        self, prompt: str, default: str, allow_empty: bool = False
    ) -> str:
        """Prompt user for input with a default value."""
        if default:
            full_prompt = f"{prompt} [{default}]: "
        else:
            full_prompt = f"{prompt}: "

        while True:
            response = input(full_prompt).strip()
            if response:
                return response
            elif default:
                return default
            elif allow_empty:
                return ""
            else:
                print("This field is required.")

    def slugify(self, text: str) -> str:
        """Convert text to a slug-friendly format for Python package names."""
        # Convert to lowercase and replace spaces/special chars with hyphens
        slug = re.sub(r"[^a-zA-Z0-9\-_]+", "-", text.lower())
        # Remove leading/trailing hyphens
        slug = slug.strip("-")
        # Ensure it starts with a letter or underscore (Python package name requirement)
        if slug and not re.match(r"^[a-zA-Z_]", slug):
            # Remove leading non-alphabetic characters
            slug = re.sub(r"^[^a-zA-Z_]+", "", slug)
        return slug

    def pythonize_package_name(self, package_name: str) -> str:
        """Convert package name to valid Python identifier for imports."""
        # Use the same logic as slugify but ensure it's a valid Python identifier
        pythonized = self.slugify(package_name)
        return pythonized

    def get_python_version(self) -> str:
        """Get and validate Python version."""
        # Get current Python version
        current_version = f"{sys.version_info.major}.{sys.version_info.minor}"

        print(f"\nDetected Python version: {current_version}")
        print("Common versions: 3.11, 3.12, 3.13")

        version = self.prompt_with_default(
            "Minimum Python version", current_version
        ).strip()

        # Validate version format
        if not re.match(r"^3\.\d+$", version):
            print("⚠️  Invalid version format, using 3.12")
            return "3.12"

        return version

    def initialize_project(self, config: Dict[str, str]) -> None:
        """Initialize the project with the given configuration."""
        print(f"\n🔧 Initializing project: {config['name']}")

        # Run uv init if pyproject.toml doesn't exist
        if not (self.project_dir / "pyproject.toml").exists():
            print("📦 Running uv init...")
            try:
                subprocess.run(["uv", "init"], check=True, cwd=self.project_dir)
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to run uv init: {e}")
                return

        # Update pyproject.toml
        self.update_pyproject_toml(config)

        # Create project structure
        self.create_project_structure(config)

        # Set up Towncrier
        self.setup_towncrier()

        # Create .envrc.example
        self.create_envrc_example()

        # Create sentinel file
        self.sentinel_file.touch()

    def update_pyproject_toml(self, config: Dict[str, str]) -> None:
        """Update pyproject.toml with project configuration."""
        pyproject_path = self.project_dir / "pyproject.toml"

        try:
            with open(pyproject_path, "r") as f:
                content = f.read()

            # DEBUG: Log the package name values
            print(f"🔍 DEBUG: Original project name: '{config['name']}'")
            print(f"🔍 DEBUG: Package name: '{config['package_name']}'")
            print(f"🔍 DEBUG: Slugified package name: '{self.slugify(config['name'])}'")

            # Update project metadata - FIX: Use slugified package name instead of raw project name
            slugified_name = self.slugify(config["name"])
            content = re.sub(
                r'^name\s*=\s*["\'][^"\']+["\']',
                f'name = "{slugified_name}"',
                content,
                flags=re.MULTILINE,
            )

            # DEBUG: Log the updated name
            updated_match = re.search(
                r'^name\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE
            )
            if updated_match:
                print(
                    f"🔍 DEBUG: Updated pyproject.toml name to: '{updated_match.group(1)}'"
                )

            content = re.sub(
                r'^description\s*=\s*["\'][^"\']*["\']',
                f'description = "{config["description"]}"',
                content,
                flags=re.MULTILINE,
            )

            content = re.sub(
                r'^requires-python\s*=\s*["\'][^"\']+["\']',
                f'requires-python = ">={config["python_version"]}"',
                content,
                flags=re.MULTILINE,
            )

            # Update authors section
            if config["author"]:
                # FIX: Use author name instead of project name
                author_line = config["author"]

                # DEBUG: Log the corrected author line
                print(f"🔍 DEBUG: Corrected author_line: '{author_line}'")

                content = re.sub(
                    r"authors\s*=\s*\[.*?\]",
                    f'authors = [ {{ name = "{author_line}", email = "{config["email"]}" }} ]',
                    content,
                    flags=re.DOTALL,
                )

                # DEBUG: Log the final authors section
                authors_match = re.search(
                    r"authors\s*=\s*\[(.*?)\]", content, re.DOTALL
                )
                if authors_match:
                    print(
                        f"🔍 DEBUG: Updated authors section: {authors_match.group(0)}"
                    )

            # FIX: Update towncrier package setting to match the new package name
            content = re.sub(
                r'package\s*=\s*["\'][^"\']+["\']',
                f'package = "{config["package_name"]}"',
                content,
                flags=re.MULTILINE,
            )

            # DEBUG: Log the updated towncrier package setting
            updated_towncrier_match = re.search(
                r'package\s*=\s*["\']([^"\']+)["\']', content
            )
            if updated_towncrier_match:
                print(
                    f"🔍 DEBUG: Updated towncrier package to: {updated_towncrier_match.group(1)}"
                )

            # Update packages configuration for package structure
            if config["structure"] == "package":
                # Find and update the packages configuration
                if "packages = [" not in content:
                    # Add packages configuration after [project] section
                    content = re.sub(
                        r"(\[project\][^\[]*?)(\n\[|\Z)",
                        f'\\1packages = [{{include = "{config["package_name"]}"}}]\\2',
                        content,
                        flags=re.DOTALL,
                    )
                else:
                    content = re.sub(
                        r"packages\s*=\s*\[.*?\]",
                        f'packages = [{{include = "{config["package_name"]}"}}]',
                        content,
                        flags=re.DOTALL,
                    )

            with open(pyproject_path, "w") as f:
                f.write(content)

            print("✅ Updated pyproject.toml")

        except Exception as e:
            print(f"❌ Failed to update pyproject.toml: {e}")

    def create_project_structure(self, config: Dict[str, str]) -> None:
        """Create the project directory structure."""
        structure = config["structure"]
        package_name = config["package_name"]
        python_package_name = self.pythonize_package_name(package_name)

        if structure == "default":
            self.create_default_structure(package_name, python_package_name)
        elif structure == "package":
            self.create_package_structure(package_name, python_package_name)
        elif structure == "library":
            self.create_library_structure(package_name, python_package_name)

        # Remove template-specific files
        self.cleanup_template_files(config)

    def create_default_structure(
        self, package_name: str, python_package_name: str
    ) -> None:
        """Create a simple default structure."""
        print("📁 Creating default structure...")

        # Create a simple package using Python-compatible name
        pkg_dir = self.project_dir / python_package_name
        pkg_dir.mkdir(exist_ok=True)

        # Create __init__.py
        (pkg_dir / "__init__.py").write_text(f'"""{package_name.title()} package."""\n')

        # Create a simple module
        (pkg_dir / "main.py").write_text(f'''"""Main module for {package_name}."""

def hello() -> str:
    """Return a greeting message."""
    return "Hello from {package_name}!"

if __name__ == "__main__":
    print(hello())
''')

        # Update main.py to use the new package
        main_py = self.project_dir / "main.py"
        if main_py.exists():
            main_py.write_text(f'''"""Main entry point for {package_name}."""

from {python_package_name}.main import hello

if __name__ == "__main__":
    print(hello())
''')

    def create_package_structure(
        self, package_name: str, python_package_name: str
    ) -> None:
        """Create a package-based structure with src/ layout."""
        print("📁 Creating package structure...")

        # Create src directory
        src_dir = self.project_dir / "src"
        src_dir.mkdir(exist_ok=True)

        # Create package directory using Python-compatible name
        pkg_dir = src_dir / python_package_name
        pkg_dir.mkdir(exist_ok=True)

        # Create __init__.py
        (pkg_dir / "__init__.py").write_text(
            f'"""{package_name.title()} package."""\n\n__version__ = "0.1.0"\n'
        )

        # Create main module
        (pkg_dir / "__main__.py").write_text(f'''"""Main module for {package_name}."""

def main() -> None:
    """Main entry point."""
    print("Hello from {package_name}!")

if __name__ == "__main__":
    main()
''')

        # Create a utils module
        (
            pkg_dir / "utils.py"
        ).write_text(f'''"""Utility functions for {package_name}."""

def greet(name: str = "World") -> str:
    """Return a greeting message."""
    return f"Hello, {{name}}!"
''')

        # Update main.py to use the new package
        main_py = self.project_dir / "main.py"
        if main_py.exists():
            main_py.write_text(f'''"""Main entry point for {package_name}."""

from {python_package_name} import main

if __name__ == "__main__":
    main()
''')

    def create_library_structure(
        self, package_name: str, python_package_name: str
    ) -> None:
        """Create a library-style structure."""
        print("📁 Creating library structure...")

        # Create src directory
        src_dir = self.project_dir / "src"
        src_dir.mkdir(exist_ok=True)

        # Create package directory using Python-compatible name
        pkg_dir = src_dir / python_package_name
        pkg_dir.mkdir(exist_ok=True)

        # Create package structure
        (pkg_dir / "__init__.py").write_text(
            f'"""{package_name.title()} library."""\n\n__version__ = "0.1.0"\n'
        )

        # Create core module
        core_dir = pkg_dir / "core"
        core_dir.mkdir(exist_ok=True)
        (core_dir / "__init__.py").write_text('"""Core functionality."""\n')
        (core_dir / "api.py").write_text(f'''"""Core API for {package_name}."""

class {package_name.title()}API:
    """Main API class."""
    
    def __init__(self):
        """Initialize the API."""
        self._initialized = True
    
    def process(self, data) -> any:
        """Process some data."""
        return f"Processed: {{data}}"
''')

        # Create utils module
        utils_dir = pkg_dir / "utils"
        utils_dir.mkdir(exist_ok=True)
        (utils_dir / "__init__.py").write_text('"""Utility functions."""\n')
        (
            utils_dir / "helpers.py"
        ).write_text(f'''"""Helper functions for {package_name}."""

def format_output(data: str) -> str:
    """Format output data."""
    return f"[{package_name.upper()}] {{data}}"
''')

        # Ensure tests directory exists
        tests_dir = self.project_dir / "tests"
        tests_dir.mkdir(exist_ok=True)

        # Create a basic test
        (tests_dir / "test_api.py").write_text(f'''"""Tests for the core API."""

import pytest
from {python_package_name}.core.api import {package_name.title()}API


def test_api_initialization():
    """Test API initialization."""
    api = {package_name.title()}API()
    assert api._initialized is True


def test_api_process():
    """Test API processing."""
    api = {package_name.title()}API()
    result = api.process("test")
    assert "test" in result
''')

        # Update main.py
        main_py = self.project_dir / "main.py"
        if main_py.exists():
            main_py.write_text(f'''"""Main entry point for {package_name} library."""

from {python_package_name}.core.api import {package_name.title()}API

def main() -> None:
    """Main entry point."""
    api = {package_name.title()}API()
    result = api.process("example")
    print(f"Result: {{result}}")

if __name__ == "__main__":
    main()
''')

    def cleanup_template_files(self, config: Dict[str, str]) -> None:
        """Remove template-specific files and directories."""
        # Remove the template package
        template_pkg = self.project_dir / "python_repo_template"
        if template_pkg.exists():
            shutil.rmtree(template_pkg)
            print("🗑️  Removed template package")

        # Update test imports to use new package
        test_file = self.project_dir / "tests" / "test_func.py"
        if test_file.exists():
            python_package_name = self.pythonize_package_name(config["package_name"])
            test_content = f'''"""Tests for the main functionality."""

from {python_package_name}.func import random_sum


def test_random_sum():
    """Test random_sum function."""
    assert random_sum(1) < 101
    assert random_sum(100) < 200
'''
            test_file.write_text(test_content)
            print("✅ Updated test imports")

    def setup_towncrier(self) -> None:
        """Set up Towncrier configuration and files."""
        print("📝 Setting up Towncrier...")

        # Create newsfragments directory
        newsfragments_dir = self.project_dir / "newsfragments"
        newsfragments_dir.mkdir(exist_ok=True)

        # Create newsfragments README
        (newsfragments_dir / "README.md").write_text("""# News Fragments

This directory contains news fragments for Towncrier.

## Fragment Types

- `feature`: New features
- `bugfix`: Bug fixes
- `doc`: Documentation improvements
- `removal`: Deprecations and removals
- `misc`: Miscellaneous changes

## Format

File names should follow the pattern: `<type>.<ticket_id>.md`

Example: `feature.123.added-new-feature.md`

## Content

Each fragment should contain a brief description of the change:

```markdown
Added a new feature that allows users to customize the output format.
```
""")

        # Create sample fragment
        (newsfragments_dir / "feature.1.initial-setup.md").write_text(
            "Initial project setup with automated bootstrap.\n"
        )

        # Create docs/changelog directory and template
        changelog_dir = self.project_dir / "docs" / "changelog"
        changelog_dir.mkdir(parents=True, exist_ok=True)

        template_path = changelog_dir / "_template.jinja"
        if not template_path.exists():
            template_path.write_text("""{% for section, _ in sections.items() %}
{% if sections[section] %}
## {{ section }}

{% for category, val in definitions.items() if category in sections[section] %}
### {{ definitions[category]['name'] }}

{% for text, changeslist in sections[section][category].items() %}
- {{ text }} ({{ changeslist|join(', ') }})
{% endfor %}

{% endfor %}
{% endif %}
{% endfor %}
""")

        print("✅ Towncrier setup complete")

    def create_envrc_example(self) -> None:
        """Create .envrc.example file."""
        envrc_example = self.project_dir / ".envrc.example"

        if not envrc_example.exists():
            envrc_example.write_text("""# direnv .envrc generated by setup-direnv
# This file:
#   - Exposes Git metadata
#   - Optionally activates a Python uv venv
#   - Optionally sets up a Bun-based Node.js workspace

# -------------------------
# Git information
# -------------------------
if has git; then
    if git rev-parse --git-dir > /dev/null 2>&1; then
        git_remote=$(git remote get-url origin 2>/dev/null || echo "No remote")
        git_branch=$(git branch --show-current 2>/dev/null || echo "No branch")
        git_commit=$(git rev-parse --short HEAD 2>/dev/null || echo "No commit")

        export GIT_REMOTE="$git_remote"
        export GIT_BRANCH="$git_branch"
        export GIT_COMMIT="$git_commit"

        watch_file "$(git rev-parse --absolute-git-dir)/HEAD"
        watch_file "$(git rev-parse --absolute-git-dir)/refs/remotes/origin/HEAD" 2>/dev/null || true
    fi
fi

# -------------------------
# Python (uv) environment
# -------------------------
layout_uv() {
    local uv_python=${1:-python3}
    [[ $# -gt 0 ]] && shift
    unset PYTHONHOME

    if [ -f .python-version ]; then
        uv_python=$(cat .python-version)
    fi

    if [ ! -d .venv ]; then
        log_status "Creating uv virtual environment with ${uv_python}"
        uv venv
    fi

    export VIRTUAL_ENV="$(pwd)/.venv"
    export UV_ACTIVE=1
    PATH_add "$VIRTUAL_ENV/bin"

    if [ -f pyproject.toml ] && { [ ! -f .venv/pyvenv.cfg ] || [ pyproject.toml -nt .venv/pyvenv.cfg ]; }; then
        log_status "Installing dependencies with uv"
        uv sync
    fi
}

# Auto-activate per project type
if [ -f pyproject.toml ] || [ -f requirements.txt ]; then
    layout_uv
fi

# Load variables from .env if present
if [ -f .env ]; then
    dotenv .env
fi
""")
            print("✅ Created .envrc.example")

    def print_next_steps(self, config: Dict[str, str]) -> None:
        """Print next steps for the user."""
        print("\n📋 Next Steps:")
        print("1. Review and customize your project structure")
        print("2. Set up direnv (optional but recommended):")
        print("   cp .envrc.example .envrc")
        print("   direnv allow")
        print("3. Install dependencies:")
        print("   just dev-sync")
        print("4. Install pre-commit hooks:")
        print("   just install-hooks")
        print("5. Start developing!")

        if config["structure"] in ["package", "library"]:
            print(f"\n💡 Your package is available as: {config['package_name']}")

        print("\n📝 For changelog management:")
        print("- Add news fragments to newsfragments/")
        print("- Run 'uv run towncrier build --version X.Y.Z --draft' to preview")
        print("- Run 'uv run towncrier build --version X.Y.Z' to generate changelog")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Initialize a Python project with customizable structure"
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Run in non-interactive mode (uses defaults)",
    )

    args = parser.parse_args()

    if args.non_interactive:
        print("Non-interactive mode not yet implemented")
        sys.exit(1)

    initializer = ProjectInitializer()
    initializer.run()


if __name__ == "__main__":
    main()
