import re
import sys

file = sys.argv[1]

with open(file, 'r') as infile:
    text = infile.read()

header, body = re.split('\n\(\d\d*\)', text, maxsplit=1)

newtext = header + '\n'

for i, line in enumerate(re.split('\(\d\d*\)', body)):
    newtext += f'({i+1}){line}' 

with open(file, 'w') as outfile:
    outfile.write(newtext)
