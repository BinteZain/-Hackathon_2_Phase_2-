import sys
print("Python executable:", sys.executable)
print("\nPython path:")
for p in sys.path:
    print(" ", p)

try:
    import agents
    print("\nagents module found at:", agents.__file__)
except ImportError as e:
    print("\nagents module NOT found:", e)
