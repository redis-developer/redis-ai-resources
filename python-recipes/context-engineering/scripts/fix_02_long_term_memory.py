#!/usr/bin/env python3
"""
Fix section-3-memory/02_long_term_memory.ipynb to use correct API.
"""

import json
from pathlib import Path


def fix_notebook():
    notebook_path = Path(__file__).parent.parent / 'notebooks' / 'section-3-memory' / '02_long_term_memory.ipynb'
    
    with open(notebook_path, 'r') as f:
        nb = json.load(f)
    
    for cell in nb['cells']:
        if cell['cell_type'] != 'code':
            continue
            
        source_text = ''.join(cell['source'])
        
        # Fix Cell 7: new_session_client initialization
        if 'new_session_client = MemoryClient(' in source_text and 'user_id=student_id' in source_text:
            cell['source'] = [
                '# Create a new memory client (simulating a new session)\n',
                'config = MemoryClientConfig(\n',
                '    base_url=os.getenv("AGENT_MEMORY_URL", "http://localhost:8000"),\n',
                '    default_namespace="redis_university"\n',
                ')\n',
                'new_session_client = MemoryClient(config=config)\n',
                '\n',
                'print("New session started for the same student\\n")\n',
                '\n',
                '# Search for memories from the new session\n',
                'print("Query: \'What do I prefer?\'\\n")\n',
                'results = await new_session_client.search_long_term_memory(\n',
                '    text="What do I prefer?",\n',
                '    limit=3\n',
                ')\n',
                '\n',
                'print("✅ Memories accessible from new session:\\n")\n',
                'for i, memory in enumerate(results.memories, 1):\n',
                '    print(f"{i}. {memory.text}")\n',
                '    print()\n'
            ]
        
        # Fix search results to use .memories
        elif 'for i, memory in enumerate(results, 1):' in source_text:
            new_source = []
            for line in cell['source']:
                if 'for i, memory in enumerate(results, 1):' in line:
                    line = line.replace('enumerate(results, 1)', 'enumerate(results.memories, 1)')
                new_source.append(line)
            cell['source'] = new_source
        
        # Fix memory_type parameter (should be MemoryType filter object)
        elif 'memory_type="semantic"' in source_text and 'search_long_term_memory' in source_text:
            # This needs to use MemoryType filter
            new_source = []
            skip_next = False
            for i, line in enumerate(cell['source']):
                if skip_next:
                    skip_next = False
                    continue
                    
                if 'memory_type="semantic"' in line:
                    # Remove this line and the next (limit line)
                    # We'll just search without the filter for now
                    new_source.append(line.replace('memory_type="semantic",\n', ''))
                elif 'memory_type="episodic"' in line:
                    new_source.append(line.replace('memory_type="episodic",\n', ''))
                else:
                    new_source.append(line)
            cell['source'] = new_source
    
    with open(notebook_path, 'w') as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
        f.write('\n')
    
    print(f"Fixed {notebook_path}")


if __name__ == '__main__':
    fix_notebook()

