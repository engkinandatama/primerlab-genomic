"""Script to analyze coverage and identify low-coverage modules."""
import subprocess
import sys

result = subprocess.run(
    [sys.executable, '-m', 'pytest', 'tests/', '--cov=primerlab', '--cov-report=term'],
    capture_output=True, text=True, cwd='/mnt/e/Project/primerlab-genomic'
)

lines = result.stdout.split('\n')
low_coverage = []

for line in lines:
    if 'primerlab' in line and '%' in line:
        parts = line.split()
        if len(parts) >= 4:
            try:
                pct_str = parts[-1].replace('%','')
                pct = int(pct_str)
                if pct < 60:
                    low_coverage.append((pct, line.strip()))
            except:
                pass

# Sort by coverage percentage
low_coverage.sort(key=lambda x: x[0])

print("\n=== LOW COVERAGE MODULES (<60%) ===\n")
for pct, line in low_coverage[:25]:
    print(line)
