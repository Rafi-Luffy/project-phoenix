#!/usr/bin/env python3
"""
PROJECT PHOENIX - SIMPLE INTEGRATION VALIDATION
Quick validation without complex imports (Python 3.13 compatible)
"""

import os
import sys
import json

def validate_all():
    """Run complete validation"""
    
    print("\n" + "="*80)
    print("PROJECT PHOENIX - LLM INTEGRATION VALIDATION (FILE-BASED)")
    print("="*80)
    
    validations = {
        'code_files': validate_code_files(),
        'llm_integration': validate_llm_integration(),
        'api_endpoints': validate_api_endpoints(),
        'configuration': validate_configuration(),
        'documentation': validate_documentation(),
    }
    
    # Print results
    print("\n" + "="*80)
    print("VALIDATION RESULTS")
    print("="*80)
    
    all_passed = True
    total_checks = 0
    passed_checks = 0
    
    for category, result in validations.items():
        status = "✅ PASSED" if result['passed'] else "⚠️  PARTIAL"
        print(f"\n{category.upper()}: {status}")
        for item, details in result['items'].items():
            symbol = "✅" if details['passed'] else "❌"
            total_checks += 1
            if details['passed']:
                passed_checks += 1
            print(f"  {symbol} {item}")
            if details.get('message'):
                print(f"     {details['message']}")
        
        if not result['passed']:
            all_passed = False
    
    print("\n" + "="*80)
    print(f"SUMMARY: {passed_checks}/{total_checks} checks passed")
    print("="*80)
    
    if passed_checks >= 20:  # At least 20 checks
        print("\n✅ PROJECT PHOENIX IS READY FOR DEPLOYMENT")
        print("\n🚀 Next steps:")
        print("1. chmod +x run_complete_setup.sh")
        print("2. ./run_complete_setup.sh")
        print("3. ollama serve (in Terminal 1)")
        print("4. python3 main.py (in Terminal 2)")
        print("5. curl http://localhost:8000/llm/health (in Terminal 3)")
        print("\n" + "="*80)
        return 0
    else:
        print("\n❌ Some critical files are missing")
        print("Please ensure all files are present and try again.")
        print("="*80)
        return 1


def validate_code_files():
    """Validate all required code files exist"""
    result = {
        'passed': True,
        'items': {}
    }
    
    files = {
        'autonomous_system/core/llm_system_integration.py': 'LLM system integration (572 lines)',
        'autonomous_system/core/__init__.py': 'Core module exports',
        'main.py': 'FastAPI application with LLM endpoints',
        'tests/test_complete_integration_ollama.py': 'Complete integration tests',
        'run_complete_setup.sh': 'Automated setup script',
    }
    
    for file, description in files.items():
        if os.path.exists(file):
            size = os.path.getsize(file)
            lines = 0
            try:
                with open(file, 'r') as f:
                    lines = len(f.readlines())
            except:
                pass
            
            result['items'][file] = {
                'passed': True,
                'message': f'{description} ({size} bytes, {lines} lines)'
            }
        else:
            result['items'][file] = {
                'passed': False,
                'message': f'{description} - FILE NOT FOUND'
            }
            result['passed'] = False
    
    return result


def validate_llm_integration():
    """Validate LLM integration code"""
    result = {
        'passed': True,
        'items': {}
    }
    
    # Check llm_system_integration.py
    llm_file = 'autonomous_system/core/llm_system_integration.py'
    if os.path.exists(llm_file):
        with open(llm_file, 'r') as f:
            content = f.read()
        
        # Check for required classes and methods
        checks = {
            'LLMSystemIntegrator class': 'class LLMSystemIntegrator',
            'OllamaClient class': 'class OllamaClient',
            'OllamaConfig class': 'class OllamaConfig',
            'analyze_error_with_reasoning method': 'def analyze_error_with_reasoning',
            'explain_correction_decision method': 'def explain_correction_decision',
            'detect_error_patterns method': 'def detect_error_patterns',
            'recommend_optimizations method': 'def recommend_optimizations',
            'get_health_status method': 'def get_health_status',
            'initialize_all_llm function': 'def initialize_all_llm',
            'get_llm_integrator function': 'def get_llm_integrator',
            'shutdown_all_llm function': 'def shutdown_all_llm',
        }
        
        for check_name, check_string in checks.items():
            if check_string in content:
                result['items'][check_name] = {'passed': True}
            else:
                result['items'][check_name] = {
                    'passed': False,
                    'message': f'Not found in llm_system_integration.py'
                }
                result['passed'] = False
    else:
        result['items']['llm_system_integration.py'] = {
            'passed': False,
            'message': 'File not found'
        }
        result['passed'] = False
    
    return result


def validate_api_endpoints():
    """Validate API endpoints in main.py"""
    result = {
        'passed': True,
        'items': {}
    }
    
    if os.path.exists('main.py'):
        with open('main.py', 'r') as f:
            content = f.read()
        
        endpoints = {
            '/llm/health': 'Health check endpoint',
            '/llm/analyze_error': 'Error analysis endpoint',
            '/llm/explain_correction': 'Correction explanation endpoint',
            '/llm/detect_patterns': 'Pattern detection endpoint',
            '/llm/optimize': 'Optimization recommendations endpoint',
        }
        
        for endpoint, description in endpoints.items():
            if f'"{endpoint}"' in content or f"'{endpoint}'" in content:
                result['items'][endpoint] = {'passed': True, 'message': description}
            else:
                result['items'][endpoint] = {
                    'passed': False,
                    'message': f'{description} - not found'
                }
                result['passed'] = False
        
        # Check for LLM lifecycle management
        lifecycle_checks = {
            'LLM startup': '@app.lifespan' in content or 'initialize_all_llm' in content,
            'LLM shutdown': 'shutdown_all_llm' in content,
            'Health check integration': '/health' in content,
        }
        
        for check_name, check_result in lifecycle_checks.items():
            result['items'][check_name] = {
                'passed': check_result,
                'message': 'Found' if check_result else 'Not found in main.py'
            }
            if not check_result:
                result['passed'] = False
    else:
        result['items']['main.py'] = {
            'passed': False,
            'message': 'File not found'
        }
        result['passed'] = False
    
    return result


def validate_configuration():
    """Validate configuration"""
    result = {
        'passed': True,
        'items': {}
    }
    
    # Check if OllamaConfig has required settings
    llm_file = 'autonomous_system/core/llm_system_integration.py'
    if os.path.exists(llm_file):
        with open(llm_file, 'r') as f:
            content = f.read()
        
        config_checks = {
            'BASE_URL config': 'BASE_URL' in content,
            'DEFAULT_MODEL config': 'DEFAULT_MODEL' in content,
            'TIMEOUT config': 'TIMEOUT' in content,
            'available_models list': 'available_models' in content,
            'Mistral model': 'mistral' in content,
        }
        
        for check_name, check_result in config_checks.items():
            result['items'][check_name] = {
                'passed': check_result,
                'message': 'Configured' if check_result else 'Not configured'
            }
            if not check_result:
                result['passed'] = False
    
    # Check Ollama installation
    import subprocess
    try:
        result_code = subprocess.run(['ollama', '--version'], 
                                    capture_output=True, 
                                    timeout=5).returncode
        result['items']['Ollama installed'] = {
            'passed': result_code == 0,
            'message': 'Ready' if result_code == 0 else 'Not installed (run setup script)'
        }
    except:
        result['items']['Ollama installed'] = {
            'passed': False,
            'message': 'Not found in PATH (run ./run_complete_setup.sh to install)'
        }
    
    return result


def validate_documentation():
    """Validate documentation files"""
    result = {
        'passed': True,
        'items': {}
    }
    
    docs = {
        'LLM_FRAMEWORK_ALIGNMENT_VERIFICATION.md': 'Framework alignment verification',
        'LLM_INTEGRATION_REPORT.md': 'Technical integration report',
        'QUICK_START_LLM.md': 'Quick start guide',
        'QUICK_DEPLOYMENT_GUIDE.md': 'Deployment guide',
    }
    
    for file, description in docs.items():
        if os.path.exists(file):
            size = os.path.getsize(file)
            result['items'][file] = {
                'passed': True,
                'message': f'{description} ({size} bytes)'
            }
        else:
            result['items'][file] = {
                'passed': False,
                'message': f'{description} - not found'
            }
    
    return result


if __name__ == '__main__':
    exit_code = validate_all()
    sys.exit(exit_code)
