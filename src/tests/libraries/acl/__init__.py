# -*- coding: utf-8 -*-
__author__ = 'maxaon'
import  unittest
import  os
from libraries.acl import RBACL

class Test(unittest.TestCase):
    def load(self, name):
        from json import load

        basepath = os.path.dirname(__file__)
        name = os.path.abspath(os.path.join(basepath, 'rules', name + ".json"))
        return load(open(name))

    def new_acl(self, name):
        return RBACL(self.load(name))

    def test_very_simple(self, acl=None):
        acl = acl or self.new_acl('very_simple')
        #allowed everything in systems
        self.assertTrue(acl.isAllowed('uid1', 'systems', 'index'))
        self.assertTrue(acl.isAllowed('uid1', 'systems', 'index', 'name'))
        self.assertTrue(acl.isAllowed('uid1', 'systems', 'index', ['name', 'speed']))
        self.assertTrue(acl.isAllowed('uid1', 'systems', 'post'))
        self.assertTrue(acl.isAllowed('uid1', 'systems', 'post', 'password'))
        self.assertTrue(acl.isAllowed('uid1', 'systems', 'login', ['password', 'email']))

        self.assertFalse(acl.isAllowed('uidOther', 'systems', 'login'))
        self.assertFalse(acl.isAllowed('uidOther', 'systems', 'index'))

    def test_simple(self, acl=None):
        acl = acl or self.new_acl('simple')
        # allowed only systems:index
        self.assertTrue(acl.isAllowed('uid1', 'systems', 'index'))
        self.assertTrue(acl.isAllowed('uid1', 'systems', 'index', 'name'))
        self.assertTrue(acl.isAllowed('uid1', 'systems', 'index', ['name', 'speed']))
        self.assertFalse(acl.isAllowed('uid1', 'systems', 'post'))
        self.assertFalse(acl.isAllowed('uid1', 'systems', 'post', 'password'))
        self.assertFalse(acl.isAllowed('uid1', 'systems', 'post', ['password', 'email']))

        self.assertFalse(acl.isAllowed('uidOther', 'systems', 'login'))
        self.assertFalse(acl.isAllowed('uidOther', 'systems', 'index'))

    def test_override_in_role(self, acl=None):
        acl = self.new_acl("override_in_role")
        self.test_simple(acl)
        self.assertTrue(acl.isAllowed('uid1', 'reports', 'index'))
        #denied all
        self.assertFalse(acl.isAllowed('uid2', 'systems', 'index'))
        self.assertFalse(acl.isAllowed('uid2', 'systems', 'index', 'name'))
        self.assertFalse(acl.isAllowed('uid2', 'systems', 'index', ['name', 'speed']))
        self.assertFalse(acl.isAllowed('uid2', 'reports', 'index'))
        #denied controller
        self.assertFalse(acl.isAllowed('uid3', 'systems', 'index'))
        self.assertFalse(acl.isAllowed('uid3', 'systems', 'login'))
        self.assertTrue(acl.isAllowed('uid3', 'reports', 'index'))
        #denied action
        self.assertFalse(acl.isAllowed('uid4', 'systems', 'index'))
        self.assertTrue(acl.isAllowed('uid4', 'systems', 'login'))
        self.assertTrue(acl.isAllowed('uid4', 'reports', 'index'))

    def test_rules_conflict(self, acl=None):
        acl = acl or self.new_acl("rules_conflict")
        #denied controller access to action
        self.assertFalse(acl.isAllowed('uid1', 'systems', 'index'))
        self.assertFalse(acl.isAllowed('uid1', 'systems', 'login'))
        self.assertTrue(acl.isAllowed('uid1', 'reports', 'index'))

    def test_fields_restrictions(self, acl=None):
        acl = acl or self.new_acl('fields_restrictions')
        self.assertTrue(acl.isAllowed('uid1', 'systems', 'index', ['name', 'gasoline', 'speed']))
        self.assertFalse(acl.isAllowed('uid1', 'systems', 'index', ['name', 'gasoline', 'speed', "voltage"]))
        self.assertFalse(acl.isAllowed('uid1', 'systems', 'index', "voltage"))
        #extend allowed fields
        self.assertTrue(acl.isAllowed('uid2', 'systems', 'index', ['name', 'gasoline', 'speed', "voltage"]))
        # add denied field
        self.assertTrue(acl.isAllowed('uid3', 'systems', 'index', ['name', 'gasoline', "voltage"]))
        self.assertFalse(acl.isAllowed('uid3', 'systems', 'index', 'speed'))
        #extend denied fields
        self.assertTrue(acl.isAllowed('uid4', 'systems', 'index'))
        self.assertTrue(acl.isAllowed('uid4', 'systems', 'index', 'name'))
        self.assertFalse(acl.isAllowed('uid4', 'systems', 'index', ['name', 'gasoline', 'speed', "voltage"]))
        self.assertFalse(acl.isAllowed('uid4', 'systems', 'index', 'speed'))
        self.assertFalse(acl.isAllowed('uid4', 'systems', 'index', 'voltage'))
        self.assertFalse(acl.isAllowed('uid4', 'systems', 'index', 'gasoline'))


if __name__ == '__main__':
    unittest.TestProgram()

