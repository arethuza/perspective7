import unittest
from actionable import WithActions, Action, Actionable, distance_from_actionable, get_class_that_defined_method

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

@WithActions
class ActionableTest2(ActionableTest):

    @Action("put", "write")
    def action4(self):
        return 10


class ActionableTests(unittest.TestCase):

    def test_distance_object(self):
        d = distance_from_actionable(object)
        self.assertEquals(d, -1)

    def test_distance_actionable(self):
        d = distance_from_actionable(Actionable)
        self.assertEquals(d, 0)

    def test_distance_actionable(self):
        d = distance_from_actionable(ActionableTest)
        self.assertEquals(d, 1)

    def test_distance_actionable(self):
        d = distance_from_actionable(ActionableTest2)
        self.assertEquals(d, 2)

    def test_get_class_that_defined_method(self):
        cls = get_class_that_defined_method(ActionableTest2, "action0")
        self.assertEquals(cls, ActionableTest)

    def test_get_class_that_defined_method2(self):
        cls = get_class_that_defined_method(ActionableTest2, "action4")
        self.assertEquals(cls, ActionableTest2)

    def test_single_action(self):
        at = ActionableTest()
        self.assertEqual(len(ActionableTest.actions), 4)
        self.assertEqual(at.invoke("get", "read"), 0)
        self.assertEqual(at.invoke("put", "write"), 1)
        self.assertEqual(at.invoke("post", "edit"), 2)
        self.assertEqual(at.invoke("get", "read", foo="bar"), 3)

    def test_action_subclass(self):
        at2 = ActionableTest2()
        self.assertEqual(len(ActionableTest2.actions), 5)
        self.assertEqual(at2.invoke("get", "read"), 0)
        self.assertEqual(at2.invoke("put", "write"), 10)
        self.assertEqual(at2.invoke("get", "read", foo="bar"), 3)

if __name__ == '__main__':
    unittest.main()