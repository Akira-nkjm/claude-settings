"""既存の justfile に新しいレシピだけをマージする"""
import re, sys

src = open('justfile').read()
dst_path = sys.argv[1]
dst = open(dst_path).read()

blocks = re.split(r'\n{2,}', src.strip())
to_append = []
for block in blocks:
    m = re.match(r'^([a-zA-Z][a-zA-Z0-9_-]*)', block.strip())
    if m and not re.search(r'^' + re.escape(m.group(1)) + r'[\s:]', dst, re.MULTILINE):
        to_append.append(block)

if to_append:
    open(dst_path, 'a').write('\n\n' + '\n\n'.join(to_append) + '\n')
    print('Merged', len(to_append), 'recipe(s) into justfile')
else:
    print('justfile up to date')
