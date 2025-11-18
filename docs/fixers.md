# AI Fixers

This guide explains how AI-powered automatic fixes work and how to configure them.

## Overview

AI fixers automatically analyze and resolve CI/CD failures using Large Language Models (LLMs). The system supports multiple types of fixers for different failure scenarios.

## Fixer Types

### 1. AIFixer (General Purpose)

Uses LLMs to analyze any type of failure:

```python
from orchestrator.fixers.ai_fixer import AIFixer

ai_fixer = AIFixer({
    "provider": "openai",
    "model": "gpt-4",
    "api_key": "your-api-key"
})

# Analyze failure
analysis = ai_fixer.analyze_failure(failure_logs)

# Generate fix
fix = ai_fixer.generate_fix(analysis)

# Apply fix
success = ai_fixer.apply_fix(fix, target_file)

# Verify fix
verified = ai_fixer.verify_fix(original_failure)
```

### 2. BuildFixer (Build Failures)

Specialized for build-related issues:

```python
from orchestrator.fixers.build_fixer import BuildFixer

build_fixer = BuildFixer()

# Fix dependency issues
build_fixer.fix_dependency_issues(error_details)

# Fix compilation errors
build_fixer.fix_compilation_errors(error_details)

# Fix configuration issues
build_fixer.fix_configuration_issues(error_details)
```

### 3. TestFixer (Test Failures)

Specialized for test-related issues:

```python
from orchestrator.fixers.test_fixer import TestFixer

test_fixer = TestFixer()

# Fix flaky tests
test_fixer.fix_flaky_tests(test_results)

# Fix assertion failures
test_fixer.fix_assertion_failures(test_results)

# Update test data
test_fixer.update_test_data(test_name, new_data)
```

## Configuration

### LLM Configuration

```yaml
llm:
  provider: openai
  model: gpt-4
  api_key: ${OPENAI_API_KEY}
  
  # Alternative providers
  # provider: anthropic
  # model: claude-3-opus
  
  settings:
    temperature: 0.2  # Lower for more deterministic fixes
    max_tokens: 2000
    timeout: 30
    
  retry:
    max_attempts: 3
    backoff_multiplier: 2
```

### Auto-Fix Configuration

```yaml
auto_fix:
  enabled: true
  
  # Maximum number of fix attempts
  max_retries: 3
  
  # Verify fix before considering success
  verify_fixes: true
  
  # Types of failures to auto-fix
  fix_types:
    - dependency_errors
    - compilation_errors
    - test_failures
    - configuration_errors
  
  # Require approval for certain changes
  require_approval:
    - production_code
    - database_migrations
  
  # Create pull requests for fixes
  create_pr: true
  pr_labels:
    - auto-fix
    - ai-generated
```

## Fix Workflow

### 1. Failure Detection

```python
# Pipeline fails
pipeline_result = run_pipeline("build")

if not pipeline_result.success:
    # Capture failure information
    failure_data = {
        "logs": pipeline_result.logs,
        "error": pipeline_result.error,
        "stage": pipeline_result.failed_stage,
        "context": pipeline_result.context
    }
```

### 2. Analysis

```python
# AI analyzes the failure
analysis = ai_fixer.analyze_failure(failure_data["logs"])

# Analysis includes:
# - Root cause identification
# - Affected files
# - Suggested fix strategy
# - Confidence level
```

### 3. Fix Generation

```python
# Generate fix based on analysis
fix = ai_fixer.generate_fix(analysis)

# Fix includes:
# - File changes
# - Configuration updates
# - Dependency modifications
# - Code patches
```

### 4. Fix Application

```python
# Apply the fix
for file_change in fix["changes"]:
    ai_fixer.apply_fix(
        file_change["content"],
        file_change["path"]
    )

# Update dependencies if needed
if fix["dependencies"]:
    update_dependencies(fix["dependencies"])
```

### 5. Verification

```python
# Re-run the failed pipeline
verify_result = run_pipeline("build")

if verify_result.success:
    print("Fix successful!")
    commit_fix(fix)
else:
    print("Fix didn't resolve the issue")
    rollback_fix(fix)
```

## Common Fix Scenarios

### Dependency Errors

```python
# Example: Missing package
logs = """
ModuleNotFoundError: No module named 'requests'
"""

# AI fix: Add to requirements.txt
fix = {
    "type": "dependency",
    "action": "add",
    "package": "requests",
    "version": "2.31.0"
}
```

### Compilation Errors

```python
# Example: Syntax error
logs = """
SyntaxError: invalid syntax
File "app.py", line 42
  def process(data
"""

# AI fix: Add missing parenthesis
fix = {
    "type": "syntax",
    "file": "app.py",
    "line": 42,
    "change": "def process(data):"
}
```

### Test Failures

```python
# Example: Assertion error
logs = """
AssertionError: Expected 200, got 404
test_api.py::test_get_user FAILED
"""

# AI fix: Update test expectation or fix code
fix = {
    "type": "test",
    "test": "test_get_user",
    "issue": "endpoint_not_found",
    "fix": "Update route or test expectation"
}
```

## Custom Fixers

Create custom fixers for domain-specific issues:

```python
from orchestrator.fixers.ai_fixer import AIFixer

class CustomFixer(AIFixer):
    """Custom fixer for specific project needs."""
    
    def analyze_custom_failure(self, logs: str):
        """Analyze custom failure pattern."""
        # Custom analysis logic
        return analysis
    
    def generate_custom_fix(self, analysis):
        """Generate fix for custom issue."""
        # Custom fix generation
        return fix

# Register custom fixer
from orchestrator.core.orchestrator import CICDOrchestrator

orchestrator = CICDOrchestrator(config)
orchestrator.register_fixer("custom", CustomFixer(config))
```

## Safety Measures

### Code Review

Enable PR creation for AI fixes:

```yaml
auto_fix:
  create_pr: true
  require_review: true
  auto_merge: false  # Require human approval
```

### Testing

Always test fixes before applying:

```yaml
auto_fix:
  test_fix:
    enabled: true
    environment: staging
    tests:
      - unit
      - integration
```

### Rollback

Automatic rollback on verification failure:

```yaml
auto_fix:
  rollback:
    enabled: true
    on_verification_failure: true
    preserve_logs: true
```

## Monitoring Fix Success

Track fix success rates:

```python
from monitors.pipeline_monitor import PipelineMonitor

monitor = PipelineMonitor()

# Track fix attempt
monitor.track_fix_attempt(
    pipeline_id="build-123",
    fixer_type="ai",
    failure_type="dependency"
)

# Track fix result
monitor.track_fix_result(
    pipeline_id="build-123",
    success=True,
    duration=45.2
)

# Get fix success rate
fix_success_rate = monitor.get_fix_success_rate()
```

## Best Practices

1. **Start Conservative**: Begin with low confidence threshold
2. **Monitor Fix Quality**: Track success rates and patterns
3. **Use Specific Prompts**: Better analysis with context
4. **Verify Fixes**: Always re-run tests after applying fixes
5. **Create PRs**: Review AI-generated changes
6. **Set Retry Limits**: Prevent infinite fix loops
7. **Log Everything**: Track all fix attempts for analysis
8. **Human Review**: Critical changes need human approval

## Troubleshooting

### Fixes Not Working

1. Check LLM API connectivity
2. Verify API key and permissions
3. Review failure logs for completeness
4. Increase temperature for more creative fixes
5. Check fix application logs

### Poor Fix Quality

1. Provide more context in failure logs
2. Use more powerful LLM model
3. Adjust temperature settings
4. Add domain-specific prompts
5. Create custom fixers for recurring issues

## Examples

See [examples/ai_auto_fix_workflow.py](../examples/ai_auto_fix_workflow.py) for a complete example of AI-powered fixing.
