import unittest
from actionable import action, class_with_actions, Actionable

@class_with_actions
class ActionableTest(Actionable):

    @action
    def action0(self):
        pass

    @action
    def action1(self):
        pass

    @action
    def action2(self):
        pass

class ActionableTests(unittest.TestCase):

    def test_single_action(self):
        at = ActionableTest()
        at.action0()
        self.assertEqual(len(ActionableTest.actions), 3)


if __name__ == '__main__':
    unittest.main()