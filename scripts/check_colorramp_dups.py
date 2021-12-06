import sys

entries = {}
for line in open(sys.argv[1]):
    tokens = line.strip().split()
    if len(tokens) != 3:
        continue
    entry = "%s,%s,%s" % (tokens[0], tokens[1], tokens[2])
    entries.setdefault(entry, 0)
    entries[entry] += 1

for entry, count in entries.iteritems():
    if count > 1:
        print(entry, count)
