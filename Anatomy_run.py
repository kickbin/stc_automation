import sys
import Anatomy as StcTest

if __name__ == "__main__":
    if StcTest.init() == 'FAILED':
        sys.exit(1)
    else:
        sys.exit(0)