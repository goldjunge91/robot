#!/usr/bin/env python3
"""
C++ Syntax Checker Tool
Performs basic syntax validation on C++ files without full compilation.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple

class CppSyntaxChecker:
    def __init__(self):
        self.errors = []
        self.warnings = []
        
    def check_file(self, filepath: str) -> Dict:
        """Check a single C++ file for syntax issues"""
        results = {
            'file': filepath,
            'errors': [],
            'warnings': [],
            'line_count': 0
        }
        
        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()
                results['line_count'] = len(lines)
                
            # Run all checks
            self._check_braces(lines, results)
            self._check_semicolons(lines, results)
            self._check_includes(lines, results)
            self._check_namespaces(lines, results)
            self._check_basic_syntax(lines, results)
            
        except Exception as e:
            results['errors'].append(f"Failed to read file: {e}")
            
        return results
    
    def _check_braces(self, lines: List[str], results: Dict):
        """Check for unmatched braces"""
        brace_stack = []
        paren_stack = []
        bracket_stack = []
        
        for i, line in enumerate(lines, 1):
            # Skip comments and strings (basic)
            clean_line = re.sub(r'//.*', '', line)
            clean_line = re.sub(r'/\*.*?\*/', '', clean_line)
            
            for char in clean_line:
                if char == '{':
                    brace_stack.append(i)
                elif char == '}':
                    if not brace_stack:
                        results['errors'].append(f"Line {i}: Unmatched closing brace '}}' ")
                    else:
                        brace_stack.pop()
                elif char == '(':
                    paren_stack.append(i)
                elif char == ')':
                    if not paren_stack:
                        results['errors'].append(f"Line {i}: Unmatched closing parenthesis ')'")
                    else:
                        paren_stack.pop()
                elif char == '[':
                    bracket_stack.append(i)
                elif char == ']':
                    if not bracket_stack:
                        results['errors'].append(f"Line {i}: Unmatched closing bracket ']'")
                    else:
                        bracket_stack.pop()
        
        # Check for unclosed braces
        if brace_stack:
            results['errors'].append(f"Unclosed braces starting at lines: {brace_stack}")
        if paren_stack:
            results['errors'].append(f"Unclosed parentheses starting at lines: {paren_stack}")
        if bracket_stack:
            results['errors'].append(f"Unclosed brackets starting at lines: {bracket_stack}")
    
    def _check_semicolons(self, lines: List[str], results: Dict):
        """Check for missing semicolons"""
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith('//') or stripped.startswith('/*'):
                continue
                
            # Lines that should end with semicolon
            if (re.match(r'^\s*(int|float|double|char|bool|std::|class|struct)', stripped) and 
                not stripped.endswith((';', '{', '}')) and
                not re.search(r'(if|for|while|switch|else)\s*\(', stripped)):
                results['warnings'].append(f"Line {i}: Possible missing semicolon")
    
    def _check_includes(self, lines: List[str], results: Dict):
        """Check include statements"""
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('#include'):
                # Check for proper include format
                if not (re.match(r'#include\s*[<"][^<>"]+[>"]', stripped)):
                    results['errors'].append(f"Line {i}: Malformed include statement")
                
                # Check for common missing includes
                if 'std::' in stripped and 'iostream' not in stripped:
                    results['warnings'].append(f"Line {i}: Using std:: but no iostream include visible")
    
    def _check_namespaces(self, lines: List[str], results: Dict):
        """Check namespace usage"""
        namespace_stack = []
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Namespace opening
            if re.match(r'namespace\s+\w+', stripped):
                namespace_stack.append(i)
            
            # Check for proper namespace closing
            if stripped == '}' and '// namespace' not in line:
                if namespace_stack:
                    results['warnings'].append(f"Line {i}: Consider adding namespace comment")
    
    def _check_basic_syntax(self, lines: List[str], results: Dict):
        """Check basic C++ syntax patterns"""
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Check for common typos
            if re.search(r'\b(pubic|privte|proteted)\b', stripped):
                results['errors'].append(f"Line {i}: Misspelled access specifier")
            
            # Check for assignment in conditions (common mistake)
            if re.search(r'if\s*\([^=]*=[^=]', stripped):
                results['warnings'].append(f"Line {i}: Possible assignment in condition (use == for comparison)")
            
            # Check for missing const
            if re.search(r'&\s*\w+\s*\)', stripped) and 'const' not in stripped:
                results['warnings'].append(f"Line {i}: Consider const reference parameter")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 check_cpp_syntax.py <directory_or_file>")
        sys.exit(1)
    
    target = sys.argv[1]
    checker = CppSyntaxChecker()
    
    # Find C++ files
    cpp_files = []
    if os.path.isfile(target):
        if target.endswith(('.cpp', '.hpp', '.h', '.cc', '.cxx')):
            cpp_files.append(target)
    else:
        for root, dirs, files in os.walk(target):
            for file in files:
                if file.endswith(('.cpp', '.hpp', '.h', '.cc', '.cxx')):
                    cpp_files.append(os.path.join(root, file))
    
    if not cpp_files:
        print("No C++ files found!")
        sys.exit(1)
    
    print(f"🔍 Checking {len(cpp_files)} C++ files...\n")
    
    total_errors = 0
    total_warnings = 0
    
    for filepath in sorted(cpp_files):
        results = checker.check_file(filepath)
        
        if results['errors'] or results['warnings']:
            print(f"📁 {filepath} ({results['line_count']} lines)")
            
            for error in results['errors']:
                print(f"  ❌ ERROR: {error}")
                total_errors += 1
            
            for warning in results['warnings']:
                print(f"  ⚠️  WARNING: {warning}")
                total_warnings += 1
            
            print()
    
    # Summary
    print("=" * 50)
    if total_errors == 0 and total_warnings == 0:
        print("✅ No syntax issues found!")
    else:
        print(f"📊 Summary: {total_errors} errors, {total_warnings} warnings")
        if total_errors > 0:
            print("❌ Fix errors before compilation")
        else:
            print("✅ No critical errors found")

if __name__ == "__main__":
    main()