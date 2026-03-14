"""
Python Script Executor Tools

This module provides safe execution of Python scripts from the scripts directory.
"""

import subprocess
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional
import time

def get_scripts_directory() -> Path:
    """
    Get the path to the scripts directory.
    
    Returns:
        Path object pointing to scripts directory
    """
    current_file = Path(__file__).resolve()
    scripts_dir = current_file.parent / "scripts"
    
    # Create directory if it doesn't exist
    scripts_dir.mkdir(exist_ok=True)
    
    return scripts_dir

def list_available_scripts() -> List[str]:
    """
    List all available Python scripts in the scripts directory.
    
    Returns:
        List of script filenames
    """
    scripts_dir = get_scripts_directory()
    
    scripts = [
        f.name for f in scripts_dir.iterdir()
        if f.is_file() and f.suffix == '.py'
    ]
    
    return sorted(scripts)

def execute_python_script(
    script_name: str,
    args: Optional[List[str]] = None,
    timeout: int = 10,
    capture_output: bool = True
) -> Dict[str, any]:
    """
    Execute a Python script from the scripts directory.
    
    Args:
        script_name: Name of the script to execute (e.g., "hello.py")
        args: Optional list of command-line arguments
        timeout: Maximum execution time in seconds
        capture_output: Whether to capture stdout and stderr
        
    Returns:
        Dictionary containing:
            - stdout: Standard output from the script
            - stderr: Error output from the script
            - returncode: Exit code (0 = success)
            - execution_time: Time taken to execute
            - script_path: Full path to the executed script
            
    Raises:
        FileNotFoundError: If script doesn't exist
        subprocess.TimeoutExpired: If execution exceeds timeout
    """
    scripts_dir = get_scripts_directory()
    script_path = scripts_dir / script_name
    
    # Verify script exists
    if not script_path.exists():
        available = list_available_scripts()
        raise FileNotFoundError(
            f"Script '{script_name}' not found in {scripts_dir}\n"
            f"Available scripts: {', '.join(available)}"
        )
    
    # Build command
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)
    
    # Execute script
    start_time = time.time()
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            timeout=timeout,
            cwd=scripts_dir
        )
        
        execution_time = time.time() - start_time
        
        return {
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode,
            'execution_time': execution_time,
            'script_path': str(script_path),
            'success': result.returncode == 0
        }
        
    except subprocess.TimeoutExpired:
        execution_time = time.time() - start_time
        return {
            'stdout': '',
            'stderr': f'Script execution timed out after {timeout} seconds',
            'returncode': -1,
            'execution_time': execution_time,
            'script_path': str(script_path),
            'success': False
        }
    
    except Exception as e:
        execution_time = time.time() - start_time
        return {
            'stdout': '',
            'stderr': f'Error executing script: {str(e)}',
            'returncode': -1,
            'execution_time': execution_time,
            'script_path': str(script_path),
            'success': False
        }

def format_execution_result(result: Dict[str, any]) -> str:
    """
    Format script execution results for display.
    
    Args:
        result: Dictionary from execute_python_script()
        
    Returns:
        Formatted string for display
    """
    script_name = Path(result['script_path']).name
    
    output = []
    output.append("═" * 60)
    output.append(f"Executing: {script_name}")
    output.append("═" * 60)
    output.append("")
    
    # Standard output
    if result['stdout']:
        output.append("📤 Output:")
        output.append(result['stdout'].rstrip())
        output.append("")
    
    # Error output
    if result['stderr']:
        output.append("⚠️ Errors:")
        output.append(result['stderr'].rstrip())
        output.append("")
    
    # No output message
    if not result['stdout'] and not result['stderr']:
        output.append("ℹ️ Script executed but produced no output")
        output.append("")
    
    # Execution info
    output.append(f"⏱️ Execution Time: {result['execution_time']:.2f} seconds")
    
    if result['success']:
        output.append("✅ Exit Code: 0 (Success)")
    else:
        output.append(f"❌ Exit Code: {result['returncode']} (Error)")
    
    output.append("═" * 60)
    
    return "\n".join(output)

def get_script_info(script_name: str) -> Optional[Dict[str, str]]:
    """
    Get information about a script (docstring, etc.).
    
    Args:
        script_name: Name of the script
        
    Returns:
        Dictionary with script info or None if not found
    """
    scripts_dir = get_scripts_directory()
    script_path = scripts_dir / script_name
    
    if not script_path.exists():
        return None
    
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract docstring if present
        docstring = None
        lines = content.split('\n')
        in_docstring = False
        docstring_lines = []
        
        for line in lines:
            if '"""' in line or "'''" in line:
                if not in_docstring:
                    in_docstring = True
                    # Check if docstring is on same line
                    if line.count('"""') == 2 or line.count("'''") == 2:
                        docstring = line.split('"""')[1] if '"""' in line else line.split("'''")[1]
                        break
                else:
                    break
            elif in_docstring:
                docstring_lines.append(line.strip())
        
        if docstring_lines:
            docstring = ' '.join(docstring_lines)
        
        return {
            'name': script_name,
            'path': str(script_path),
            'description': docstring or 'No description available',
            'size': script_path.stat().st_size,
        }
        
    except Exception as e:
        return {
            'name': script_name,
            'path': str(script_path),
            'description': f'Error reading script: {str(e)}',
            'size': 0
        }

# Example usage
if __name__ == "__main__":
    print("Available scripts:")
    for script in list_available_scripts():
        print(f"  - {script}")
        info = get_script_info(script)
        if info and info['description'] != 'No description available':
            print(f"    {info['description']}")