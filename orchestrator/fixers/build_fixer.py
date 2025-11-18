"""
Specialized fixer for build failures.
"""

import logging
import re
from typing import Dict, Any
from .ai_fixer import AIFixer

logger = logging.getLogger(__name__)


class BuildFixer:
    """
    Specialized fixer for common build-related issues.
    Extends AIFixer with build-specific knowledge.
    """

    def __init__(self, ai_fixer: AIFixer = None):
        """
        Initialize the build fixer.

        Args:
            ai_fixer: Optional AIFixer instance for AI-powered fixes
        """
        self.ai_fixer = ai_fixer
        logger.info("BuildFixer initialized")

    def analyze_build_failure(self, error_logs: str) -> Dict[str, Any]:
        """
        Analyze build failure to determine the type.

        Args:
            error_logs: Build error logs

        Returns:
            Analysis with error type and details
        """
        error_type = "unknown"
        details = {}

        # Detect dependency issues
        if any(keyword in error_logs.lower() for keyword in [
            "modulenotfounderror", "importerror", "no module named",
            "cannot find package", "package not found", "npm err!"
        ]):
            error_type = "dependency"
            details = self._extract_missing_dependencies(error_logs)

        # Detect compilation errors
        elif any(keyword in error_logs.lower() for keyword in [
            "syntaxerror", "compilation failed", "build failed",
            "error:", "undefined reference"
        ]):
            error_type = "compilation"
            details = self._extract_compilation_errors(error_logs)

        # Detect configuration issues
        elif any(keyword in error_logs.lower() for keyword in [
            "configuration", "config", "invalid option",
            "permission denied", "file not found"
        ]):
            error_type = "configuration"
            details = self._extract_config_issues(error_logs)

        return {
            "error_type": error_type,
            "details": details,
            "logs": error_logs
        }

    def _extract_missing_dependencies(self, error_logs: str) -> Dict[str, Any]:
        """Extract missing dependency names from error logs."""
        dependencies = []

        # Python dependencies
        python_pattern = r"ModuleNotFoundError: No module named '([^']+)'"
        dependencies.extend(re.findall(python_pattern, error_logs))

        # npm dependencies
        npm_pattern = r"Cannot find module '([^']+)'"
        dependencies.extend(re.findall(npm_pattern, error_logs))

        return {"missing_packages": list(set(dependencies))}

    def _extract_compilation_errors(self, error_logs: str) -> Dict[str, Any]:
        """Extract compilation error details."""
        errors = []

        # Extract file:line:error patterns
        error_pattern = r"([^\s]+):(\d+):(?:\d+:)?\s*error:\s*(.+)"
        matches = re.findall(error_pattern, error_logs)

        for file_path, line, error_msg in matches:
            errors.append({
                "file": file_path,
                "line": int(line),
                "message": error_msg.strip()
            })

        return {"compilation_errors": errors}

    def _extract_config_issues(self, error_logs: str) -> Dict[str, Any]:
        """Extract configuration issue details."""
        issues = []

        # Look for configuration file mentions
        config_pattern = r"(config[^\s]*|[^\s]*\.conf|[^\s]*\.ini|[^\s]*\.yaml)"
        config_files = re.findall(config_pattern, error_logs, re.IGNORECASE)

        return {"config_files": list(set(config_files))}

    def fix_dependency_issues(self, error_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fix dependency-related build failures.

        Args:
            error_details: Details about the dependency error

        Returns:
            Fix result
        """
        logger.info("Fixing dependency issues...")

        missing_packages = error_details.get("details", {}).get("missing_packages", [])

        if not missing_packages:
            return {"success": False, "message": "No missing packages identified"}

        # If AI fixer is available, use it for complex dependency resolution
        if self.ai_fixer and len(missing_packages) > 3:
            return self._ai_fix_dependencies(error_details)

        # Simple fix: suggest adding packages to requirements
        fix_suggestions = []
        for package in missing_packages:
            fix_suggestions.append(f"Add '{package}' to requirements.txt or install with: pip install {package}")

        return {
            "success": True,
            "fix_type": "dependency",
            "suggestions": fix_suggestions,
            "commands": [f"pip install {' '.join(missing_packages)}"]
        }

    def _ai_fix_dependencies(self, error_details: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to fix complex dependency issues."""
        if not self.ai_fixer:
            return {"success": False, "message": "AI fixer not available"}

        analysis = self.ai_fixer.analyze_failure(error_details)
        return self.ai_fixer.generate_fix(analysis, error_details.get("context", {}))

    def fix_compilation_errors(self, error_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fix compilation errors in the build.

        Args:
            error_details: Details about the compilation error

        Returns:
            Fix result
        """
        logger.info("Fixing compilation errors...")

        compilation_errors = error_details.get("details", {}).get("compilation_errors", [])

        if not compilation_errors:
            return {"success": False, "message": "No compilation errors identified"}

        # For compilation errors, AI assistance is usually required
        if self.ai_fixer:
            return self._ai_fix_compilation(error_details)

        # Provide basic suggestions
        suggestions = []
        for error in compilation_errors:
            suggestions.append(
                f"Fix error in {error['file']} at line {error['line']}: {error['message']}"
            )

        return {
            "success": False,
            "fix_type": "compilation",
            "message": "Compilation errors require manual review or AI assistance",
            "suggestions": suggestions
        }

    def _ai_fix_compilation(self, error_details: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to fix compilation errors."""
        if not self.ai_fixer:
            return {"success": False, "message": "AI fixer not available"}

        analysis = self.ai_fixer.analyze_failure(error_details)
        return self.ai_fixer.generate_fix(analysis, error_details.get("context", {}))

    def fix_configuration_issues(self, error_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fix build configuration issues.

        Args:
            error_details: Details about the configuration error

        Returns:
            Fix result
        """
        logger.info("Fixing configuration issues...")

        config_files = error_details.get("details", {}).get("config_files", [])

        suggestions = []
        for config_file in config_files:
            suggestions.append(f"Check configuration in {config_file}")

        return {
            "success": True,
            "fix_type": "configuration",
            "suggestions": suggestions,
            "message": "Review and update configuration files"
        }
