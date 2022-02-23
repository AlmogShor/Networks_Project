import unittest
import server.utils as test_subject


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_init(self):
        pass

    def test_client_messages(self):
        pass

    def test_connected_clients(self):
        pass

    def test_send(self):
        pass

    def test_send_to_all(self):
        pass

    def test_on_client_doscinnected(self):
        pass

    def test_run(self):
        # Should I test it? this is my way to test bind, listen and accept client
        pass


if __name__ == '__main__':
    unittest.main()
