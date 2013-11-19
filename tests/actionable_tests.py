import unittest
from actionable import WithActions, Action, Actionable

@WithActions
class ActionableTest(Actionable):

    @Action("put", "write")
    def action1(self):
        return 1

    @Action("post", "edit")
    def action2(self):
        return 2

    @Action("get", "read", foo='bar')
    def action3(self):
        return 3

    @Action("get", "read")
    def action0(self):
        return 0

class ActionableTests(unittest.TestCase):

    def test_single_action(self):
        at = ActionableTest()
        at.action0()
        self.assertEqual(len(ActionableTest.actions), 4)
        self.assertEqual(at.invoke("get", "read"), 0)
        self.assertEqual(at.invoke("put", "write"), 1)
        self.assertEqual(at.invoke("post", "edit"), 2)
        self.assertEqual(at.invoke("get", "read", foo="bar"), 3)


if __name__ == '__main__':
    unittest.main()