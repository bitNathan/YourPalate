from unittest import TestCase as tc


class TestDjango(tc):
    def base_test(self):
        return True
    def test_base(self):
        self.assertTrue(self.base_test(), msg='Test failed')


if __name__ == '__main__':
    TestDjango()