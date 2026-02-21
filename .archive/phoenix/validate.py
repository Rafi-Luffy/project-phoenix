#!/usr/bin/env python3
"""
Phoenix Framework - Complete Validation & Health Check
Ensures all components are properly installed and functional
"""

import sys
from pathlib import Path


def print_section(title):
  """Print a formatted section header."""
  print()
  print("=" * 70)
  print(f" {title}")
  print("=" * 70)


def check_python_version():
  """Check Python version."""
  print_section(" Python Version Check")
  version = sys.version_info
  print(f"Python {version.major}.{version.minor}.{version.micro}")
  
  if version.major == 3 and version.minor >= 10:
    print(" Python version is compatible (3.10+)")
    return True
  else:
    print(f" Python {version.major}.{version.minor} is not supported")
    print("  Phoenix requires Python 3.10 or higher")
    return False


def check_dependencies():
  """Check all required dependencies."""
  print_section(" Dependency Check")
  
  required_packages = {
    'fastapi': 'FastAPI (Web Framework)',
    'sqlalchemy': 'SQLAlchemy (ORM)',
    'pydantic': 'Pydantic (Data Validation)',
    'pytest': 'Pytest (Testing)',
    'openai': 'OpenAI SDK',
    'anthropic': 'Anthropic SDK',
    'git': 'GitPython',
    'docker': 'Docker SDK',
    'structlog': 'Structlog (Logging)',
    'httpx': 'HTTPX (HTTP Client)',
    'dotenv': 'Python-dotenv',
  }
  
  missing = []
  installed = []
  
  for module, description in required_packages.items():
    try:
      __import__(module)
      print(f" {description}")
      installed.append(module)
    except ImportError:
      print(f" {description} - NOT INSTALLED")
      missing.append(module)
  
  print()
  if missing:
    print(f" Missing {len(missing)} packages:")
    print("  Install with: python -m pip install -r requirements.txt")
    return False
  else:
    print(f" All {len(installed)} required packages installed!")
    return True


def check_phoenix_imports():
  """Check Phoenix framework imports."""
  print_section(" Phoenix Framework Module Check")
  
  modules = [
    ('phoenix.core.models', 'Core Models'),
    ('phoenix.core.config', 'Configuration'),
    ('phoenix.core.logging', 'Logging'),
    ('phoenix.observer.test_runner', 'Observer - TestRunner'),
    ('phoenix.observer.failure_detector', 'Observer - FailureDetector'),
    ('phoenix.critic.llm_client', 'Critic - LLM Client'),
    ('phoenix.critic.critic_agent', 'Critic Agent'),
    ('phoenix.programmer.code_editor', 'Programmer - CodeEditor'),
    ('phoenix.programmer.programmer_agent', 'Programmer Agent'),
    ('phoenix.validator.sandbox', 'Validator - Sandbox'),
    ('phoenix.validator.validator', 'Validator'),
    ('phoenix.integrator.integrator', 'Integrator'),
    ('phoenix.orchestrator.orchestrator', 'Orchestrator'),
  ]
  
  failed = []
  success = []
  
  for module_name, description in modules:
    try:
      __import__(module_name)
      print(f" {description}")
      success.append(module_name)
    except Exception as e:
      print(f" {description} - {str(e)[:50]}")
      failed.append((module_name, str(e)))
  
  print()
  if failed:
    print(f" {len(failed)} modules failed to import")
    return False
  else:
    print(f" All {len(success)} Phoenix modules imported successfully!")
    return True


def check_example_project():
  """Check example project exists."""
  print_section(" Example Project Check")
  
  example_path = Path(__file__).parent / "examples" / "calculator-buggy"
  
  if not example_path.exists():
    print(f" Example project not found at: {example_path}")
    return False
  
  required_files = ['calculator.py', 'test_calculator.py', 'pytest.ini']
  missing = []
  
  for file in required_files:
    file_path = example_path / file
    if file_path.exists():
      print(f" {file}")
    else:
      print(f" {file} - NOT FOUND")
      missing.append(file)
  
  print()
  if missing:
    print(f" Missing {len(missing)} required files")
    return False
  else:
    print(f" Example project is complete!")
    return True


def check_configuration():
  """Check configuration files."""
  print_section(" Configuration Check")
  
  project_root = Path(__file__).parent
  
  config_files = {
    '.env': 'Environment configuration (Optional for demo)',
    'requirements.txt': 'Python dependencies',
    'pyproject.toml': 'Project configuration',
    'docker-compose.yml': 'Docker orchestration',
  }
  
  for file, description in config_files.items():
    file_path = project_root / file
    if file_path.exists():
      print(f" {file} - {description}")
    else:
      if file == '.env':
        print(f" {file} - {description} (use .env.example as template)")
      else:
        print(f" {file} - {description} - NOT FOUND")
  
  print()
  env_file = project_root / '.env'
  if not env_file.exists():
    print(" TIP: Create .env file for LLM features:")
    print("  cp .env.example .env")
    print("  Then add your API keys (OPENAI_API_KEY, etc.)")
  
  return True


def check_documentation():
  """Check documentation files."""
  print_section(" Documentation Check")
  
  project_root = Path(__file__).parent
  
  docs = [
    'README.md',
    'QUICKSTART.md',
    'USAGE.md',
    'ARCHITECTURE.md',
    'STATUS.md',
  ]
  
  found = 0
  for doc in docs:
    doc_path = project_root / doc
    if doc_path.exists():
      print(f" {doc}")
      found += 1
    else:
      print(f" {doc} - NOT FOUND")
  
  print()
  print(f" Found {found}/{len(docs)} documentation files")
  return found >= 3 # At least README, QUICKSTART, and one other


def run_quick_test():
  """Run a quick functional test."""
  print_section(" Quick Functional Test")
  
  try:
    from phoenix.observer.test_runner import TestRunner
    from pathlib import Path
    
    example_path = Path(__file__).parent / "examples" / "calculator-buggy"
    
    if not example_path.exists():
      print(" Example project not found - skipping test")
      return False
    
    print("Running tests on calculator-buggy...")
    runner = TestRunner(project_path=example_path)
    result = runner.run_tests()
    
    print(f" Test execution successful!")
    print(f"  Total tests: {result.total_tests}")
    print(f"  Passed: {result.passed}")
    print(f"  Failed: {result.failed}")
    
    if result.total_tests > 0:
      print()
      print(" Phoenix Observer is working correctly!")
      return True
    else:
      print(" No tests found")
      return False
      
  except Exception as e:
    print(f" Test failed: {e}")
    return False


def main():
  """Run all checks."""
  print()
  print("" * 35)
  print(" " * 20 + "PHOENIX FRAMEWORK")
  print(" " * 15 + "Complete System Validation")
  print("" * 35)
  
  checks = [
    ("Python Version", check_python_version),
    ("Dependencies", check_dependencies),
    ("Phoenix Modules", check_phoenix_imports),
    ("Example Project", check_example_project),
    ("Configuration", check_configuration),
    ("Documentation", check_documentation),
    ("Quick Test", run_quick_test),
  ]
  
  results = []
  
  for name, check_func in checks:
    try:
      success = check_func()
      results.append((name, success))
    except Exception as e:
      print(f" {name} check failed with error: {e}")
      results.append((name, False))
  
  # Summary
  print_section(" Validation Summary")
  
  passed = sum(1 for _, success in results if success)
  total = len(results)
  
  for name, success in results:
    status = " PASS" if success else " FAIL"
    print(f"{status:12} {name}")
  
  print()
  print("=" * 70)
  
  if passed == total:
    print(f" ALL CHECKS PASSED ({passed}/{total})")
    print("=" * 70)
    print()
    print("Phoenix is READY for your final year project!")
    print()
    print("Next steps:")
    print(" 1. Run demo: python demo.py")
    print(" 2. Read docs: cat QUICKSTART.md")
    print(" 3. Start API: python -m phoenix.api.main")
    print()
    return 0
  else:
    failed = total - passed
    print(f" {failed} CHECK(S) FAILED ({passed}/{total} passed)")
    print("=" * 70)
    print()
    print("Please fix the failed checks and run this script again.")
    print()
    return 1


if __name__ == "__main__":
  sys.exit(main())
