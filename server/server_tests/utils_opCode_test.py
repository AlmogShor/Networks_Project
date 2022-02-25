import unittest

import server.utils




class MyTestCase(unittest.TestCase):

    def test_validate_opcode(self):
        tst_sub = server.utils.OpCode.validate_opcode("CM")
        # CM = "CM"
        # ans = test_subject.OpCode.validate_opcode(CM)
        # print(ans)
        self.assertTrue(tst_sub)


if __name__ == '__main__':
    unittest.main()