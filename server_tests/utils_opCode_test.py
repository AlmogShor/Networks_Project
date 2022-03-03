import unittest

import sys
import os
sys.path.append(
    os.path.abspath(os.path.join('..'))
)
from server.utils import *


class MyTestCase(unittest.TestCase):

    def test_validate_opcode(self):
        tst_sub = OpCode.validate_opcode("CM")
        # CM = "CM"
        # ans = test_subject.OpCode.validate_opcode(CM)
        # print(ans)
        self.assertTrue(tst_sub)


if __name__ == '__main__':
    unittest.main()