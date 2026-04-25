#!/usr/bin/env python3
"""Fix UniqueConstraint definitions to include max_name_length."""
from pathlib import Path

def fix_model_file(filepath):
    """Fix a model file by adding max_name_length only to UniqueConstraint."""
    content = filepath.read_text()
    
    lines = content.split('\n')
    result_lines = []
    in_unique_constraint = False
    paren_depth = 0
    
    for line in lines:
        stripped = line.strip()
        
        # Detect start of UniqueConstraint
        if 'models.UniqueConstraint(' in line or ('UniqueConstraint(' in line and 'models.' not in line):
            in_unique_constraint = True
            paren_depth = 1
            result_lines.append(line)
            continue
        
        if in_unique_constraint:
            # Count parentheses to track depth
            for char in line:
                if char == '(':
                    paren_depth += 1
                elif char == ')':
                    paren_depth -= 1
            
            # Check if this is the name= line and we haven't added max_name_length yet
            if 'name=' in stripped and 'max_name_length' not in content and stripped.endswith('),'):
                # This is the last field before closing, add max_name_length
                indent = len(line) - len(line.lstrip())
                result_lines.append(line.rstrip().rstrip(','))
                result_lines.append(' ' * indent + 'max_name_length=30,')
            elif 'name=' in stripped and 'max_name_length' not in content:
                # name= is followed by more fields, add max_name_length after it
                indent = len(line) - len(line.lstrip())
                result_lines.append(line.rstrip().rstrip(','))
                result_lines.append(' ' * indent + 'max_name_length=30,')
            else:
                result_lines.append(line)
            
            # End of UniqueConstraint block
            if paren_depth == 0:
                in_unique_constraint = False
        else:
            result_lines.append(line)
    
    new_content = '\n'.join(result_lines)
    
    # Only write if we made actual changes
    if content != new_content:
        filepath.write_text(new_content)
        return True
    return False

# Find all models.py files
backend_dir = Path('/Users/emi/Desktop/projects/medisoft/backend')
models_files = list(backend_dir.glob('apps/**/models.py'))

fixed_count = 0
for f in sorted(models_files):
    if fix_model_file(f):
        print(f"Fixed: {f}")
        fixed_count += 1

print(f"\nTotal files fixed: {fixed_count}")
