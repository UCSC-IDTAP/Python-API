#!/usr/bin/env python3
"""
Simple version bumper for patch-only increments.
Usage: python scripts/bump_version.py [--minor] [--major]
"""
import re
import sys
from pathlib import Path

def get_current_version():
    """Get current version from __init__.py"""
    init_file = Path("idtap/__init__.py")
    content = init_file.read_text()
    match = re.search(r'__version__ = "(\d+\.\d+\.\d+)"', content)
    if not match:
        raise ValueError("Could not find version in __init__.py")
    return match.group(1)

def bump_version(current_version, bump_type="patch"):
    """Bump version based on type"""
    major, minor, patch = map(int, current_version.split("."))
    
    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    else:  # patch
        return f"{major}.{minor}.{patch + 1}"

def update_file(filepath, old_version, new_version):
    """Update version in a file"""
    path = Path(filepath)
    if not path.exists():
        print(f"Warning: {filepath} does not exist, skipping")
        return
    
    content = path.read_text()
    # Different patterns for different files
    if filepath.endswith("__init__.py"):
        pattern = f'__version__ = "{old_version}"'
        replacement = f'__version__ = "{new_version}"'
    elif filepath.endswith("pyproject.toml"):
        pattern = f'version = "{old_version}"'
        replacement = f'version = "{new_version}"'
    elif filepath.endswith("README.md"):
        pattern = f"### v{old_version} (Latest)"
        replacement = f"### v{new_version} (Latest)"
    elif filepath.endswith("conf.py"):
        # Handle both single and double quotes, and any version number
        original_content = content
        content = re.sub(r"release = ['\"][\d\.]+['\"]", f"release = '{new_version}'", content)
        content = re.sub(r"version = ['\"][\d\.]+['\"]", f"version = '{new_version}'", content)
        if content != original_content:
            path.write_text(content)
            print(f"Updated {filepath} to version {new_version}")
        else:
            print(f"Warning: No version pattern found in {filepath}")
        return
    else:
        return
    
    if pattern in content:
        content = content.replace(pattern, replacement)
        path.write_text(content)
        print(f"Updated {filepath}: {old_version} → {new_version}")
    else:
        print(f"Warning: Pattern not found in {filepath}")

def main():
    # Parse arguments
    bump_type = "patch"
    if "--major" in sys.argv:
        bump_type = "major"
    elif "--minor" in sys.argv:
        bump_type = "minor"
    
    # Get current version
    current = get_current_version()
    print(f"Current version: {current}")
    
    # Calculate new version
    new = bump_version(current, bump_type)
    print(f"New version: {new}")
    
    # Update all files
    files_to_update = [
        "idtap/__init__.py",
        "pyproject.toml",
        "README.md",
        "docs/conf.py",
    ]
    
    for filepath in files_to_update:
        update_file(filepath, current, new)
    
    print(f"\n✅ Version bumped from {current} to {new}")
    return new

if __name__ == "__main__":
    new_version = main()
    # Output the version for GitHub Actions  
    print(f"::set-output name=version::{new_version}")