import unittest
import server.utils as test_subject


class MyTestCase(unittest.TestCase):

    def test_validate_opcode(self):
        CM = "CM"
        ans = test_subject.OpCode.validate_opcode(CM)
        self.assertTrue(ans)


if __name__ == '__main__':
    unittest.main()
