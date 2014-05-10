import unittest
from actionable import WithActions, Action, Actionable, get_distance_from_actionable, \
    get_class_that_defined_method, NoAuthorizedActionException, list_actions

@WithActions
class ActionableTest(Actionable):

    @Action("put", "editor")
    def action1(self):
        """doc action 1"""
        return 1

    @Action("post", "editor")
    def action2(self):
        """doc action 2"""
        return 2

    @Action("get", "reader")
    def action0(self):
        """doc action 0"""
        return 0

    @Action("get", "reader", foo='bar')
    def action3(self):
        """doc action 3"""
        return 3


@WithActions
class ActionableTest2(ActionableTest):

    @Action("put", "editor")
    def action4(self):
        """doc action 4"""
        return 10

    @Action("get", "reader", foo='bar', raz="woof")
    def action4(self):
        """doc action 4 - 2"""
        return 20

    @Action("post", "reader")
    def action5(self, arg):
        """doc action 5"""
        return 30

    @Action("post", "reader", foo='floop')
    def action6(self, arg):
        """doc action 6"""
        return 40

    @Action("post", "editor", foo='')
    def action7(self, foo):
        """doc action 7"""
        return foo

    @Action("delete", "editor", foo='int:3')
    def action8(self):
        """doc action 8"""
        return 3

    @Action("options", "editor", foo='int:')
    def action9(self, foo: "The foo") -> "bar":
        """doc action 9"""
        return foo

    @Action("post", "editor", foo='int:')
    def action10(self, foo: "The foo", _file_data) -> "raz":
        """doc action 10"""
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
        self.assertEqual(at.invoke("get", "reader"), (0, None))

    def test_action_with_arg(self):
        at = ActionableTest()
        self.assertEqual(len(ActionableTest.actions), 4)
        self.assertEqual(at.invoke("get", "reader", foo="bar"), (3, None))


    def test_action_subclass(self):
        at2 = ActionableTest2()
        self.assertEqual(len(ActionableTest2.actions), 11)
        self.assertEqual(at2.invoke("get", "reader"), (0, None))

    def test_action_subclass_args(self):
        at2 = ActionableTest2()
        self.assertEqual(at2.invoke("get", "reader", foo="bar"), (3, None))
        self.assertEqual(at2.invoke("get", "reader", foo="bar", raz="woof"), (20, None))

    def test_unknown_authorization(self):
        at2 = ActionableTest2()
        self.assertRaises(Exception, at2.invoke, "get", "floop")

    def test_unauthorized(self):
        at2 = ActionableTest2()
        self.assertRaises(NoAuthorizedActionException, at2.invoke, "get", "none")

    def test_positional_arg(self):
        at2 = ActionableTest2()
        self.assertEqual(at2.invoke("post", "reader", ["foo"]), (30, None))

    def test_positional_and_kw_arg(self):
        at2 = ActionableTest2()
        self.assertEqual(at2.invoke("post", "reader", ["foo"], foo="floop"), (40, None))

    def test_int_typed_kw_arg_with_expected_value(self):
        at2 = ActionableTest2()
        self.assertEqual(at2.invoke("delete", "editor", [], foo="3"), (3, None))

    def test_int_typed_kw_arg(self):
        at2 = ActionableTest2()
        self.assertEqual(at2.invoke("options", "editor", [], foo="1"), (1, "bar"))
        self.assertEqual(at2.invoke("options", "editor", [], foo="2"), (2, "bar"))

    def test_int_typed_kw_arg_bad_argument(self):
        at2 = ActionableTest2()
        with self.assertRaises(Exception) as cm:
            at2.invoke("options", "editor", [], foo="bar")
        self.assertEquals(cm.exception.args[0], "Bad int value: foo=bar")

    def test_list_actions(self):
        actions = list_actions(ActionableTest2)
        action = actions[1]
        self.assertEquals(5, len(action))
        self.assertEquals("doc action 9", action["doc"])
        self.assertEquals("options", action["http_method"])
        self.assertEquals("editor", action["auth_level"])
        self.assertEquals("bar", action["returns"])
        self.assertEquals([{"name": "foo", "doc": "The foo"}], action["params"])


if __name__ == '__main__':
    unittest.main()