# -*- coding: utf-8 -*-
from functools import partial

__author__ = 'maxaon'
import unittest
import os
from libraries.acl import RBAC, RBACCollection


class Tests(unittest.TestCase):
    def load(self, name):
        from yaml import load

        basepath = os.path.dirname(__file__)
        name = os.path.abspath(os.path.join(basepath, 'rules', name + ".yaml"))
        c = load(open(name))
        #        import yaml
        #        print(yaml.safe_dump(c))
        return c

    def new_acl(self, name, cls=RBAC):
        """
        :rtype : RBAC
        """
        return cls(self.load(name))

    def test_new(self):
        acl = self.new_acl('new')
        self.assertFalse(acl.isAllowed(['g2', 'g3'], 'c2', 'a1'))
        self.assertTrue(acl.isAllowed(['g2', 'g3'], 'c2', 'a2'))
        self.assertTrue(acl.isAllowed(['g2', 'g3'], 'c2', 'a3'))
        self.assertTrue(acl.isAllowed(['g2', 'g3'], 'c2', 'a4'))
        self.assertFalse(acl.isAllowed(['g1', 'g2'], 'c2', 'a1'))
        self.assertTrue(acl.isAllowed(['g1', 'g2'], 'c2', 'a2'))
        self.assertFalse(acl.isAllowed(['g1', 'g2'], 'c2', 'a3'))
        self.assertTrue(acl.isAllowed(['g1', 'g2'], 'c2', 'a4'))
        self.assertFalse(acl.isAllowed(['g3', 'g4'], 'c2', 'a3'))

    def override_in_role(self, acl=None):
        acl = acl or self.new_acl('override_in_role')
        # allowed only systems:index
        self.assertTrue(acl.isUserAllowed('uid1', 'systems', 'index'))
        self.assertTrue(acl.isUserAllowed('uid1', 'systems', 'index', 'name'))
        self.assertTrue(acl.isUserAllowed('uid1', 'systems', 'index', ['name', 'speed']))
        self.assertFalse(acl.isUserAllowed('uid1', 'systems', 'post'))
        self.assertFalse(acl.isUserAllowed('uid1', 'systems', 'post', 'password'))
        self.assertFalse(acl.isUserAllowed('uid1', 'systems', 'post', ['password', 'email']))

        self.assertFalse(acl.isUserAllowed('uid6', 'reports', 'index'))
        self.assertTrue(acl.isUserAllowed('uid6', 'reports', 'post'))
        self.assertTrue(acl.isUserAllowed('uid6', 'reports', 'patch'))
        self.assertFalse(acl.isUserAllowed('uidOther', 'systems', 'login'))
        self.assertFalse(acl.isUserAllowed('uidOther', 'systems', 'index'))

    def test_very_simple(self, acl=None):
        acl = acl or self.new_acl('very_simple')
        #allowed everything in systems
        self.assertTrue(acl.isUserAllowed('uid1', 'systems', 'index'))
        self.assertTrue(acl.isUserAllowed('uid1', 'systems', 'index', 'name'))
        self.assertTrue(acl.isUserAllowed('uid1', 'systems', 'index', ['name', 'speed']))
        self.assertTrue(acl.isUserAllowed('uid1', 'systems', 'post'))
        self.assertTrue(acl.isUserAllowed('uid1', 'systems', 'post', 'password'))
        self.assertTrue(acl.isUserAllowed('uid1', 'systems', 'login', ['password', 'email']))

        self.assertFalse(acl.isUserAllowed('uidOther', 'systems', 'login'))
        self.assertFalse(acl.isUserAllowed('uidOther', 'systems', 'index'))

    def test_simple(self, acl=None):
        acl = acl or self.new_acl('simple')
        # allowed only systems:index
        self.assertTrue(acl.isUserAllowed('uid1', 'systems', 'index'))
        self.assertTrue(acl.isUserAllowed('uid1', 'systems', 'index', 'name'))
        self.assertTrue(acl.isUserAllowed('uid1', 'systems', 'index', ['name', 'speed']))
        self.assertFalse(acl.isUserAllowed('uid1', 'systems', 'post'))
        self.assertFalse(acl.isUserAllowed('uid1', 'systems', 'post', 'password'))
        self.assertFalse(acl.isUserAllowed('uid1', 'systems', 'post', ['password', 'email']))

        self.assertFalse(acl.isUserAllowed('uidOther', 'systems', 'login'))
        self.assertFalse(acl.isUserAllowed('uidOther', 'systems', 'index'))

    def test_override_in_role(self, acl=None):
        acl = self.new_acl("override_in_role")
        self.test_simple(acl)
        self.assertTrue(acl.isUserAllowed('uid1', 'reports', 'index'))
        #denied all
        self.assertFalse(acl.isUserAllowed('uid2', 'systems', 'index'))
        self.assertFalse(acl.isUserAllowed('uid2', 'systems', 'index', 'name'))
        self.assertFalse(acl.isUserAllowed('uid2', 'systems', 'index', ['name', 'speed']))
        self.assertFalse(acl.isUserAllowed('uid2', 'reports', 'index'))
        #denied controller
        self.assertFalse(acl.isUserAllowed('uid3', 'systems', 'index'))
        self.assertFalse(acl.isUserAllowed('uid3', 'systems', 'login'))
        self.assertTrue(acl.isUserAllowed('uid3', 'reports', 'index'))
        #denied action
        self.assertFalse(acl.isUserAllowed('uid4', 'systems', 'index'))
        self.assertTrue(acl.isUserAllowed('uid4', 'systems', 'login'))
        self.assertTrue(acl.isUserAllowed('uid4', 'reports', 'index'))

    def test_rules_conflict(self, acl=None):
        acl = acl or self.new_acl("rules_conflict")
        #denied controller access to action
        self.assertFalse(acl.isUserAllowed('uid1', 'systems', 'index'))
        self.assertTrue(acl.isUserAllowed('uid1', 'systems', 'login'))
        self.assertTrue(acl.isUserAllowed('uid1', 'reports', 'index'))

    def test_fields_restrictions(self, acl=None):
        acl = acl or self.new_acl('fields_restrictions')
        a = partial(self._assert_allowed, acl, controller='systems', action='index')
        d = partial(self._assert_denied, acl)
        self.assertTrue(acl.isUserAllowed('uid1', 'systems', 'index', ['name', 'gasoline', 'speed']))
        self.assertFalse(acl.isUserAllowed('uid1', 'systems', 'index', ['name', 'gasoline', 'speed', "voltage"]))
        self.assertFalse(acl.isUserAllowed('uid1', 'systems', 'index', "voltage"))
        #extend allowed fields
        self.assertTrue(acl.isUserAllowed('uid2', 'systems', 'index', ['name', 'gasoline', 'speed', "voltage"]))
        # add denied field
        self.assertTrue(acl.isUserAllowed('uid3', 'systems', 'index', ['name', 'gasoline', "voltage"]))
        self.assertFalse(acl.isUserAllowed('uid3', 'systems', 'index', 'speed'))
        #extend denied fields
        self.assertTrue(acl.isUserAllowed('uid4', 'systems', 'index'))
        self.assertTrue(acl.isUserAllowed('uid4', 'systems', 'index', 'name'))
        self.assertFalse(acl.isUserAllowed('uid4', 'systems', 'index', ['name', 'gasoline', 'speed', "voltage"]))
        self.assertFalse(acl.isUserAllowed('uid4', 'systems', 'index', 'speed'))
        self.assertFalse(acl.isUserAllowed('uid4', 'systems', 'index', 'voltage'))
        self.assertFalse(acl.isUserAllowed('uid4', 'systems', 'index', 'gasoline'))

        r = ['inheritance_global', 'base_role', 'denied_fields']
        a(r, fields=['name'])

    def _assert_allowed(self, acl, roles, controller, action, fields=None):
        self.assertTrue(acl.isAllowed(roles, controller, action, fields))

    def _assert_denied(self, acl, roles, controller, action, fields=None):
        self.assertFalse(acl.isAllowed(roles, controller, action, fields))

    def test_global_override(self):
        acl = self.new_acl('global_override')
        a = partial(self._assert_allowed, acl)
        d = partial(self._assert_denied, acl)
        for r in (['g1', 'g2'], ['g2', 'g1']):
            d(r, 'c10', 'a')
            d(r, 'c1', 'a')
            d(r, 'c2', 'a')
            d(r, 'c3', 'a')
            a(r, 'c4', 'a')
            a(r, 'c4', 'a')

    def test_inheritance(self):
        acl = self.new_acl('inheritance')
        a = partial(self._assert_allowed, acl)
        d = partial(self._assert_denied, acl)
        r = ['g1', 'g2']
        d(r, 'c10', 'a')
        a(r, 'c1', 'a')
        d(r, 'c2', 'a')
        d(r, 'c3', 'a')
        a(r, 'c4', 'a')
        a(r, 'c4', 'index')
        d(r, 'c4', 'post')
        r = ['g1', 'g2', 'g3']
        a(r, 'c1', 'index')
        d(r, 'c1', 'post')
        d(r, 'c2', 'a')
        d(r, 'c3', 'a')
        d(r, 'c4', 'a')
        d(r, 'c4', 'index')
        a(r, 'c4', 'post')

    def test_id_field(self):
        acl = self.new_acl('fields_restrictions', RBACCollection)
        a = partial(self._assert_allowed, acl)
        d = partial(self._assert_denied, acl)
        r = ['base_role']
        a(r, 'systems', 'index', ['name', 'gasoline', '_id'])
        a(r, 'systems', 'index', ['_id'])
        r = ['base_role', 'denied_id']
        d(r, 'systems', 'index', ['_id'])
        r = ['base_role', 'inheritance_local']
        a(r, 'systems', 'index', ['_id'])
        r = ['base_role', 'denied_id', 'inheritance_local']
        a(r, 'systems', 'index', ['_id'])


if __name__ == '__main__':
    unittest.TestProgram()

