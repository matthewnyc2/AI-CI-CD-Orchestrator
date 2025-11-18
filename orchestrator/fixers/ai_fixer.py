"""
AI-powered fixer for automated issue resolution.
"""

import logging
import os
import re
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class AIFixer:
    """
    AI-driven fixer that uses LLMs to automatically resolve CI/CD issues.
    """

    def __init__(self, llm_config: Dict[str, Any]):
        """
        Initialize the AI fixer with LLM configuration.

        Args:
            llm_config: Configuration for the LLM backend
        """
        self.llm_config = llm_config
        self.provider = llm_config.get("provider", "anthropic")
        self.model = llm_config.get("model", "claude-3-5-sonnet-20241022")
        self.api_key = llm_config.get("api_key", "")
        self.max_tokens = llm_config.get("max_tokens", 4000)
        self.temperature = llm_config.get("temperature", 0.2)

        # Initialize LLM client
        self.client = self._init_client()

        logger.info(f"AIFixer initialized with provider: {self.provider}")

    def _init_client(self):
        """Initialize the LLM client based on provider."""
        try:
            if self.provider == "anthropic":
                import anthropic
                return anthropic.Anthropic(api_key=self.api_key)
            elif self.provider == "openai":
                import openai
                client = openai.OpenAI(api_key=self.api_key)
                return client
            else:
                raise ValueError(f"Unsupported LLM provider: {self.provider}")
        except ImportError as e:
            logger.error(f"Failed to import LLM library: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            raise

    def _call_llm(self, prompt: str, system: Optional[str] = None) -> str:
        """
        Make a call to the LLM.

        Args:
            prompt: The user prompt
            system: Optional system prompt

        Returns:
            LLM response text
        """
        try:
            if self.provider == "anthropic":
                messages = [{"role": "user", "content": prompt}]

                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    system=system if system else "You are an expert DevOps engineer specializing in CI/CD pipeline debugging and fixes.",
                    messages=messages
                )

                return response.content[0].text

            elif self.provider == "openai":
                messages = []
                if system:
                    messages.append({"role": "system", "content": system})
                messages.append({"role": "user", "content": prompt})

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )

                return response.choices[0].message.content

        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            raise

    def analyze_failure(self, failure_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze failure logs to identify root cause.

        Args:
            failure_info: Failure information including logs, context, etc.

        Returns:
            Analysis results with suggested fixes
        """
        logger.info("Analyzing failure using AI...")

        failure_logs = failure_info.get("error", "")
        pipeline_type = failure_info.get("type", "unknown")
        stage = failure_info.get("stage", "unknown")

        prompt = f"""Analyze the following CI/CD pipeline failure and provide a detailed diagnosis:

Pipeline Type: {pipeline_type}
Failed Stage: {stage}

Error Logs:
```
{failure_logs}
```

Please provide:
1. Root cause analysis
2. Specific issues identified
3. Suggested fixes (up to 3 approaches)
4. Priority level (high/medium/low)

Format your response as:

ROOT CAUSE:
[Your analysis]

ISSUES:
- [Issue 1]
- [Issue 2]

SUGGESTED FIXES:
1. [Fix approach 1]
2. [Fix approach 2]
3. [Fix approach 3]

PRIORITY: [high/medium/low]
"""

        try:
            response = self._call_llm(prompt)

            # Parse response
            analysis = self._parse_analysis(response)
            analysis["raw_response"] = response
            analysis["status"] = "analyzed"

            logger.info(f"Analysis complete. Priority: {analysis.get('priority', 'unknown')}")

            return analysis

        except Exception as e:
            logger.error(f"Failure analysis failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "suggestions": []
            }

    def _parse_analysis(self, response: str) -> Dict[str, Any]:
        """Parse the LLM analysis response."""
        analysis = {
            "root_cause": "",
            "issues": [],
            "suggestions": [],
            "priority": "medium"
        }

        # Extract sections using regex
        root_cause_match = re.search(r"ROOT CAUSE:\s*\n(.*?)\n\n", response, re.DOTALL)
        if root_cause_match:
            analysis["root_cause"] = root_cause_match.group(1).strip()

        issues_match = re.search(r"ISSUES:\s*\n(.*?)\n\n", response, re.DOTALL)
        if issues_match:
            issues_text = issues_match.group(1)
            analysis["issues"] = [
                issue.strip("- ").strip()
                for issue in issues_text.split("\n")
                if issue.strip().startswith("-")
            ]

        fixes_match = re.search(r"SUGGESTED FIXES:\s*\n(.*?)\n\n", response, re.DOTALL)
        if fixes_match:
            fixes_text = fixes_match.group(1)
            analysis["suggestions"] = [
                fix.strip("0123456789. ").strip()
                for fix in fixes_text.split("\n")
                if re.match(r"^\d+\.", fix.strip())
            ]

        priority_match = re.search(r"PRIORITY:\s*(\w+)", response, re.IGNORECASE)
        if priority_match:
            analysis["priority"] = priority_match.group(1).lower()

        return analysis

    def generate_fix(self, analysis: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a fix based on failure analysis.

        Args:
            analysis: Analysis results from analyze_failure
            context: Additional context (file paths, code, etc.)

        Returns:
            Generated fix with code changes
        """
        logger.info("Generating fix using AI...")

        root_cause = analysis.get("root_cause", "Unknown")
        suggestions = analysis.get("suggestions", [])
        repo_path = context.get("repo_path", "")

        prompt = f"""Based on the following failure analysis, generate a specific fix:

ROOT CAUSE:
{root_cause}

SUGGESTED APPROACHES:
{chr(10).join(f"{i+1}. {s}" for i, s in enumerate(suggestions))}

Repository Path: {repo_path}

Generate a concrete fix including:
1. Files that need to be modified
2. Exact code changes or configuration updates
3. Commands to run (if any)

Format your response as:

FILES TO MODIFY:
- path/to/file1.py: [brief description]
- path/to/file2.yaml: [brief description]

CHANGES:
```
file: path/to/file1.py
---
[exact code or diff]
```

COMMANDS:
```bash
[commands to run]
```

EXPLANATION:
[Brief explanation of the fix]
"""

        try:
            response = self._call_llm(prompt)

            fix = self._parse_fix(response)
            fix["raw_response"] = response
            fix["status"] = "generated"

            logger.info(f"Fix generated for {len(fix.get('files', {}))} files")

            return fix

        except Exception as e:
            logger.error(f"Fix generation failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "files": {},
                "commands": []
            }

    def _parse_fix(self, response: str) -> Dict[str, Any]:
        """Parse the LLM fix response."""
        fix = {
            "files": {},
            "commands": [],
            "explanation": ""
        }

        # Extract file changes
        changes_match = re.findall(
            r"```\s*\nfile:\s*(.+?)\s*\n---\s*\n(.*?)\n```",
            response,
            re.DOTALL
        )
        for file_path, content in changes_match:
            fix["files"][file_path.strip()] = content.strip()

        # Extract commands
        commands_match = re.search(r"COMMANDS:\s*\n```(?:bash)?\s*\n(.*?)\n```", response, re.DOTALL)
        if commands_match:
            commands_text = commands_match.group(1)
            fix["commands"] = [
                cmd.strip()
                for cmd in commands_text.split("\n")
                if cmd.strip() and not cmd.strip().startswith("#")
            ]

        # Extract explanation
        explanation_match = re.search(r"EXPLANATION:\s*\n(.*?)(?:\n\n|$)", response, re.DOTALL)
        if explanation_match:
            fix["explanation"] = explanation_match.group(1).strip()

        return fix

    def apply_fix(self, fix: Dict[str, Any], repo_path: str) -> Dict[str, Any]:
        """
        Apply the generated fix to the repository.

        Args:
            fix: Generated fix from generate_fix
            repo_path: Path to the repository

        Returns:
            Application result
        """
        logger.info(f"Applying fix to {repo_path}")

        results = {
            "success": True,
            "files_modified": [],
            "commands_executed": [],
            "errors": []
        }

        try:
            # Apply file changes
            files = fix.get("files", {})
            for file_path, content in files.items():
                full_path = os.path.join(repo_path, file_path)

                try:
                    # Create directory if it doesn't exist
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)

                    # Write the file
                    with open(full_path, 'w') as f:
                        f.write(content)

                    results["files_modified"].append(file_path)
                    logger.info(f"Modified file: {file_path}")

                except Exception as e:
                    error_msg = f"Failed to modify {file_path}: {e}"
                    results["errors"].append(error_msg)
                    logger.error(error_msg)
                    results["success"] = False

            # Execute commands
            import subprocess
            commands = fix.get("commands", [])
            for cmd in commands:
                try:
                    result = subprocess.run(
                        cmd,
                        shell=True,
                        cwd=repo_path,
                        capture_output=True,
                        text=True,
                        timeout=300
                    )

                    results["commands_executed"].append({
                        "command": cmd,
                        "returncode": result.returncode,
                        "output": result.stdout
                    })

                    if result.returncode != 0:
                        results["errors"].append(f"Command failed: {cmd}\n{result.stderr}")
                        logger.warning(f"Command returned non-zero: {cmd}")

                except Exception as e:
                    error_msg = f"Failed to execute {cmd}: {e}"
                    results["errors"].append(error_msg)
                    logger.error(error_msg)

            if results["errors"]:
                results["success"] = False

            return results

        except Exception as e:
            logger.error(f"Fix application failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "files_modified": results["files_modified"],
                "commands_executed": results["commands_executed"]
            }

    def verify_fix(self, original_failure: Dict[str, Any], repo_path: str) -> Dict[str, Any]:
        """
        Verify that the fix resolves the original issue.

        Args:
            original_failure: Original failure information
            repo_path: Path to repository

        Returns:
            Verification result
        """
        logger.info("Verifying fix...")

        # Re-run the failed stage to verify
        # This is a simplified verification - in production, you'd re-run the actual pipeline
        verification = {
            "verified": False,
            "message": "Fix verification not yet implemented",
            "recommendation": "Manually re-run the pipeline to verify the fix"
        }

        # In a complete implementation, this would:
        # 1. Re-run the failed pipeline stage
        # 2. Compare results with original failure
        # 3. Return success/failure status

        return verification
