#!/usr/bin/env python3
"""
Shell Configuration Deduplicator
================================
Removes duplicate PATH exports and cleans up shell configuration files.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Set, Dict, Tuple

class ShellDeduplicator:
    def __init__(self, user_home: str, platform: str, backup_suffix: str):
        self.home = Path(user_home)
        self.platform = platform
        self.backup_suffix = backup_suffix
        self.stats = {
            'files_processed': 0,
            'duplicates_removed': 0,
            'lines_cleaned': 0,
            'errors': []
        }
        
    def find_duplicates(self, lines: List[str]) -> Tuple[List[str], int]:
        """Find and remove duplicate PATH exports"""
        seen_exports = set()
        cleaned_lines = []
        duplicates_found = 0
        
        for line in lines:
            # Skip comments and empty lines
            if not line.strip() or line.strip().startswith('#'):
                cleaned_lines.append(line)
                continue
                
            # Check for PATH exports
            path_match = re.match(r'^\s*export\s+PATH=', line)
            if path_match:
                # Normalize the export for comparison
                normalized = re.sub(r'\s+', ' ', line.strip())
                if normalized in seen_exports:
                    duplicates_found += 1
                    cleaned_lines.append(f"# REMOVED DUPLICATE: {line}")
                    continue
                seen_exports.add(normalized)
                
            # Check for other problematic patterns
            problematic_patterns = [
                r'export PATH.*\.local/bin.*export PATH.*\.local/bin',  # Double UV path exports
                r'export.*PYENV_ROOT.*export.*PYENV_ROOT',  # Double PYENV_ROOT
                r'export.*NVM_DIR.*export.*NVM_DIR',      # Double NVM_DIR
            ]
            
            is_problematic = False
            for pattern in problematic_patterns:
                if re.search(pattern, line):
                    is_problematic = True
                    break
                    
            if is_problematic:
                duplicates_found += 1
                cleaned_lines.append(f"# REMOVED PROBLEMATIC: {line}")
                continue
                
            cleaned_lines.append(line)
            
        return cleaned_lines, duplicates_found
        
    def clean_file(self, file_path: Path) -> bool:
        """Clean a single shell configuration file"""
        if not file_path.exists():
            return False
            
        try:
            # Read original content
            with open(file_path, 'r') as f:
                original_lines = f.readlines()
                
            # Find and remove duplicates
            cleaned_lines, duplicates = self.find_duplicates(original_lines)
            
            # Only write if changes were made
            if duplicates > 0:
                with open(file_path, 'w') as f:
                    f.writelines(cleaned_lines)
                    
                self.stats['duplicates_removed'] += duplicates
                self.stats['lines_cleaned'] += len(original_lines) - len([l for l in cleaned_lines if not l.strip().startswith('# REMOVED')])
                print(f"Cleaned {file_path.name}: removed {duplicates} duplicates")
                return True
            else:
                print(f"No duplicates found in {file_path.name}")
                return False
                
        except Exception as e:
            error_msg = f"Error processing {file_path}: {str(e)}"
            self.stats['errors'].append(error_msg)
            print(error_msg)
            return False
            
    def deduplicate_all(self) -> Dict:
        """Process all shell configuration files"""
        files_to_process = [
            '.zshrc',
            '.zprofile', 
            '.bash_profile',
            '.bashrc'
        ]
        
        print(f"Starting shell deduplication for platform: {self.platform}")
        print(f"Home directory: {self.home}")
        
        for filename in files_to_process:
            file_path = self.home / filename
            if self.clean_file(file_path):
                self.stats['files_processed'] += 1
                
        return self.stats
        
    def generate_report(self) -> str:
        """Generate a summary report"""
        report = f"""
Shell Deduplication Summary:
===========================
Files Processed: {self.stats['files_processed']}
Duplicates Removed: {self.stats['duplicates_removed']}
Lines Cleaned: {self.stats['lines_cleaned']}
"""
        
        if self.stats['errors']:
            report += f"\nErrors Encountered:\n"
            for error in self.stats['errors']:
                report += f"- {error}\n"
        else:
            report += "\nNo errors encountered.\n"
            
        return report

def main():
    """Main execution function"""
    user_home = os.environ.get('USER_HOME', os.path.expanduser('~'))
    platform = os.environ.get('PLATFORM', 'unknown')
    backup_suffix = os.environ.get('BACKUP_SUFFIX', '.cleanup_backup')
    
    deduplicator = ShellDeduplicator(user_home, platform, backup_suffix)
    stats = deduplicator.deduplicate_all()
    
    print(deduplicator.generate_report())
    
    # Exit with error code if there were issues
    if stats['errors']:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == '__main__':
    main()