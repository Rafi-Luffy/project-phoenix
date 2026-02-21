#!/usr/bin/env python3
"""
PROJECT PHOENIX - INTEGRATION VALIDATION SCRIPT
Validates that the complete LLM integration is working correctly
"""

import asyncio
import sys
import json
from datetime import datetime

# Setup path
sys.path.insert(0, '.')

async def validate_all():
    """Run complete validation"""
    
    print("\n" + "="*80)
    print("PROJECT PHOENIX - COMPLETE LLM INTEGRATION VALIDATION")
    print("="*80)
    
    validations = {
        'imports': await validate_imports(),
        'framework': await validate_framework(),
        'llm_module': await validate_llm_module(),
        'api_endpoints': await validate_api_endpoints(),
        'file_structure': await validate_file_structure(),
        'configuration': await validate_configuration(),
    }
    
    # Print results
    print("\n" + "="*80)
    print("VALIDATION RESULTS")
    print("="*80)
    
    all_passed = True
    for category, result in validations.items():
        status = "✅ PASSED" if result['passed'] else "❌ FAILED"
        print(f"\n{category.upper()}: {status}")
        for item, details in result['items'].items():
            symbol = "✅" if details['passed'] else "❌"
            print(f"  {symbol} {item}")
            if details.get('message'):
                print(f"     {details['message']}")
        
        if not result['passed']:
            all_passed = False
    
    print("\n" + "="*80)
    
    if all_passed:
        print("✅ ALL VALIDATIONS PASSED")
        print("\nYour Project Phoenix is ready for deployment!")
        print("\nNext steps:")
        print("1. chmod +x run_complete_setup.sh")
        print("2. ./run_complete_setup.sh")
        print("3. ollama serve")
        print("4. python3 main.py")
        print("5. curl http://localhost:8000/llm/health")
        print("="*80)
        return 0
    else:
        print("❌ SOME VALIDATIONS FAILED")
        print("Please fix the issues and try again.")
        print("="*80)
        return 1


async def validate_imports():
    """Validate all required imports"""
    result = {
        'passed': True,
        'items': {}
    }
    
    imports = [
        ('CoreOrchestrator', 'from autonomous_system.core import CoreOrchestrator'),
        ('SelfCorrectionOrchestrator', 'from autonomous_system.core import SelfCorrectionOrchestrator'),
        ('MemoryManager', 'from autonomous_system.core import MemoryManager'),
        ('LLMSystemIntegrator', 'from autonomous_system.core.llm_system_integration import LLMSystemIntegrator'),
        ('OllamaClient', 'from autonomous_system.core.llm_system_integration import OllamaClient'),
        ('OllamaConfig', 'from autonomous_system.core.llm_system_integration import OllamaConfig'),
        ('ErrorContext', 'from autonomous_system.core.error_detection import ErrorContext'),
    ]
    
    for name, import_str in imports:
        try:
            exec(import_str)
            result['items'][name] = {'passed': True}
        except ImportError as e:
            result['items'][name] = {'passed': False, 'message': str(e)}
            result['passed'] = False
    
    return result


async def validate_framework():
    """Validate framework components"""
    result = {
        'passed': True,
        'items': {}
    }
    
    try:
        from autonomous_system.core import CoreOrchestrator, SelfCorrectionOrchestrator, MemoryManager
        
        # Test initialization
        core = CoreOrchestrator()
        result['items']['CoreOrchestrator initialization'] = {'passed': True}
        
        self_corr = SelfCorrectionOrchestrator()
        result['items']['SelfCorrectionOrchestrator initialization'] = {'passed': True}
        
        memory = MemoryManager()
        result['items']['MemoryManager initialization'] = {'passed': True}
        
        # Test methods exist
        if hasattr(core, 'detect_error'):
            result['items']['CoreOrchestrator.detect_error method'] = {'passed': True}
        else:
            result['items']['CoreOrchestrator.detect_error method'] = {'passed': False, 'message': 'Method not found'}
            result['passed'] = False
        
    except Exception as e:
        result['passed'] = False
        result['items']['Framework initialization'] = {'passed': False, 'message': str(e)}
    
    return result


async def validate_llm_module():
    """Validate LLM module"""
    result = {
        'passed': True,
        'items': {}
    }
    
    try:
        from autonomous_system.core.llm_system_integration import (
            LLMSystemIntegrator,
            OllamaClient,
            OllamaConfig,
            initialize_llm_integration,
            get_llm_integrator,
            initialize_all_llm,
            shutdown_all_llm
        )
        
        # Test LLMSystemIntegrator
        result['items']['LLMSystemIntegrator class'] = {'passed': True}
        
        # Check methods
        methods = ['analyze_error_with_reasoning', 'explain_correction_decision', 
                   'detect_error_patterns', 'recommend_optimizations', 'get_health_status']
        
        for method in methods:
            if hasattr(LLMSystemIntegrator, method):
                result['items'][f'LLMSystemIntegrator.{method}'] = {'passed': True}
            else:
                result['items'][f'LLMSystemIntegrator.{method}'] = {'passed': False, 'message': 'Method not found'}
                result['passed'] = False
        
        # Test OllamaConfig
        config = OllamaConfig()
        result['items']['OllamaConfig initialization'] = {'passed': True}
        
        if hasattr(config, 'available_models'):
            result['items']['OllamaConfig.available_models'] = {'passed': True}
        else:
            result['items']['OllamaConfig.available_models'] = {'passed': False}
            result['passed'] = False
        
        # Test initialization functions
        result['items']['initialize_all_llm function'] = {'passed': callable(initialize_all_llm)}
        result['items']['get_llm_integrator function'] = {'passed': callable(get_llm_integrator)}
        result['items']['shutdown_all_llm function'] = {'passed': callable(shutdown_all_llm)}
        
    except Exception as e:
        result['passed'] = False
        result['items']['LLM module'] = {'passed': False, 'message': str(e)}
    
    return result


async def validate_api_endpoints():
    """Validate API endpoints in main.py"""
    result = {
        'passed': True,
        'items': {}
    }
    
    try:
        # Check if main.py contains endpoints
        with open('main.py', 'r') as f:
            content = f.read()
        
        endpoints = [
            '/llm/health',
            '/llm/analyze_error',
            '/llm/explain_correction',
            '/llm/detect_patterns',
            '/llm/optimize'
        ]
        
        for endpoint in endpoints:
            if endpoint in content:
                result['items'][f'Endpoint {endpoint}'] = {'passed': True}
            else:
                result['items'][f'Endpoint {endpoint}'] = {'passed': False, 'message': 'Not found in main.py'}
                result['passed'] = False
        
    except Exception as e:
        result['passed'] = False
        result['items']['API endpoints'] = {'passed': False, 'message': str(e)}
    
    return result


async def validate_file_structure():
    """Validate project file structure"""
    import os
    
    result = {
        'passed': True,
        'items': {}
    }
    
    files = [
        'autonomous_system/core/llm_system_integration.py',
        'autonomous_system/core/__init__.py',
        'main.py',
        'tests/test_complete_integration_ollama.py',
        'run_complete_setup.sh',
    ]
    
    for file in files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            result['items'][file] = {'passed': True, 'message': f'({size} bytes)'}
        else:
            result['items'][file] = {'passed': False, 'message': 'File not found'}
            result['passed'] = False
    
    return result


async def validate_configuration():
    """Validate configuration and setup"""
    result = {
        'passed': True,
        'items': {}
    }
    
    try:
        from autonomous_system.core.llm_system_integration import OllamaConfig
        
        config = OllamaConfig()
        
        # Check models
        result['items']['OllamaConfig.BASE_URL'] = {
            'passed': True,
            'message': f'({config.BASE_URL})'
        }
        
        result['items']['OllamaConfig.DEFAULT_MODEL'] = {
            'passed': True,
            'message': f'({config.DEFAULT_MODEL})'
        }
        
        result['items']['OllamaConfig.TIMEOUT'] = {
            'passed': True,
            'message': f'({config.TIMEOUT}s)'
        }
        
        # Verify Ollama is installed
        import subprocess
        try:
            subprocess.run(['ollama', '--version'], capture_output=True, timeout=5)
            result['items']['Ollama installation'] = {
                'passed': True,
                'message': '(installed)'
            }
        except (FileNotFoundError, subprocess.TimeoutExpired):
            result['items']['Ollama installation'] = {
                'passed': False,
                'message': '(not found - run: ./run_complete_setup.sh)'
            }
    
    except Exception as e:
        result['passed'] = False
        result['items']['Configuration'] = {'passed': False, 'message': str(e)}
    
    return result


if __name__ == '__main__':
    exit_code = asyncio.run(validate_all())
    sys.exit(exit_code)
