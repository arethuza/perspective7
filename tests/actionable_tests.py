import unittest
from actionable import WithActions, Action, Actionable, get_distance_from_actionable, \
    get_class_that_defined_method, NoAuthorizedActionException

@WithActions
class ActionableTest(Actionable):

    @Action("put", "editor")
    def action1(self):
        return 1

    @Action("post", "editor")
    def action2(self):
        return 2

    @Action("get", "reader")
    def action0(self):
        return 0

    @Action("get", "reader", foo='bar')
    def action3(self):
        return 3


@WithActions
class ActionableTest2(ActionableTest):

    @Action("put", "editor")
    def action4(self):
        return 10

    @Action("get", "reader", foo='bar', raz="woof")
    def action4(self):
        return 20

    @Action("post", "reader")
    def action5(self, arg):
        return 30

    @Action("post", "reader", foo='floop')
    def action6(self, arg):
        return 40

    @Action("post", "editor", foo='')
    def action7(self, foo):
        return foo


class ActionableTests(unittest.TestCase):

    def test_distance_object(self):
        d = get_distance_from_actionable(object)
        self.assertEquals(d, -1)

    def test_distance_actionable(self):
        d = get_distance_from_actionable(Actionable)
        self.assertEquals(d, 0)

    def test_distance_actionable1(self):
        d = get_distance_from_actionable(ActionableTest)
        self.assertEquals(d, 1)

    def test_distance_actionable2(self):
        d = get_distance_from_actionable(ActionableTest2)
        self.assertEquals(d, 2)

    def test_get_class_that_defined_method(self):
        cls = get_class_that_defined_method(ActionableTest2, "action0")
        self.assertEquals(cls, ActionableTest)

    def test_get_class_that_defined_method2(self):
        cls = get_class_that_defined_method(ActionableTest2, "action4")
        self.assertEquals(cls, ActionableTest2)

    def test_action_no_args(self):
        at = ActionableTest()
        self.assertEqual(len(ActionableTest.actions), 4)
        self.assertEqual(at.invoke("get", "reader"), 0)

    def test_action_with_arg(self):
        at = ActionableTest()
        self.assertEqual(len(ActionableTest.actions), 4)
        self.assertEqual(at.invoke("get", "reader", foo="bar"), 3)


    def test_action_subclass(self):
        at2 = ActionableTest2()
        self.assertEqual(len(ActionableTest2.actions), 8)
        self.assertEqual(at2.invoke("get", "reader"), 0)

    def test_action_subclass_args(self):
        at2 = ActionableTest2()
        self.assertEqual(len(ActionableTest2.actions), 8)
        self.assertEqual(at2.invoke("get", "reader", foo="bar"), 3)
        self.assertEqual(at2.invoke("get", "reader", foo="bar", raz="woof"), 20)

    def test_unknown_authorization(self):
        at2 = ActionableTest2()
        self.assertRaises(Exception, at2.invoke, "get", "floop")

    def test_unauthorized(self):
        at2 = ActionableTest2()
        self.assertRaises(NoAuthorizedActionException, at2.invoke, "get", "none")

    def test_positional_arg(self):
        at2 = ActionableTest2()
        self.assertEqual(at2.invoke("post", "reader", ["foo"]), 30)

    def test_positional_and_kw_arg(self):
        at2 = ActionableTest2()
        self.assertEqual(at2.invoke("post", "reader", ["foo"], foo="floop"), 40)

    def test_wildcard_kw_arg(self):
        at2 = ActionableTest2()
        self.assertEqual(at2.invoke("post", "editor", [], foo="floop"), "floop")

if __name__ == '__main__':
    unittest.main()