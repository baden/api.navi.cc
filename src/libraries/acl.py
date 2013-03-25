from __future__ import unicode_literals
from copy import deepcopy
from functools import partial


def and_ternary(a, b):
    """\
    Logical 'and' for ternary values: True, None, False
    :param a: First operand
    :param b: Second operand
    :return: Result of operation
    """
    if a is None:
        return b
    elif b is None:
        return a
    else:
        return a and b


def _merge(a, b):
    """recursively merges dict's. not just simple a['key'] = b['key'], if
    both a and bhave a key who's value is a dict then dict_merge is called
    on both values and the result stored in the returned dictionary."""
    if isinstance(a, list) or isinstance(b, list):
        a = deepcopy(a or [])
        a.extend(deepcopy(b or []))
        return a

    if not isinstance(b, dict):
        return a
    if not isinstance(a, dict):
        return b
    result = deepcopy(a)
    for k, v in b.iteritems():
        if k in result and isinstance(result[k], dict):
            result[k] = _merge(result[k], v)
        elif k in result and isinstance(result[k], list):
            result[k].extend(deepcopy(v))
        elif k in result and isinstance(v, list):
            result[k] = deepcopy(v).insert(0, result[k])
        else:
            result[k] = deepcopy(v)
    return result


class RBAC(object):
    GUEST = '$guest'
    AK = 'access'
    ALLOW = "allow"
    DENY = "deny"
    BASE = {
        'systems': {
            'filter_by': ['devices'],
            'index': {'fields': [], 'filter_by': []},
            'patch': {'fields': [], 'filter_by': []},
        },
        'reports': {
            'filter_by': ['devices']
        },
        'accounts': {
            'filter_by': ['account']
        }
    }

    def __init__(self, settings=None, compiled_rules=None):
        self.compiled_rules = compiled_rules or {}
        if settings:
            self.roles = settings['roles']
            self.parse(settings['rules'])
            self.expand_roles(self.compiled_rules)

    def parse(self, rules):
        for i, rule in enumerate(rules):
            type = rule['type']
            if type == 'group':
                self.add_group_rule(rule)
                pass
            elif type == 'user':
                self.add_user_rule(rule)
            else:
                raise TypeError("Wrong type in rule #{}".format(i))

    def add_group_rule(self, rule, roles=None, filter_by=None):
        roles = _merge(roles, rule.get('roles'))
        filter_by = _merge(filter_by, rule.get('filter_by'))
        users = rule.get('users')
        sub_groups = rule.get('sub-groups')
        if sub_groups:
            if isinstance(sub_groups, list):
                for sub_group in sub_groups:
                    self.add_group_rule(sub_group, roles, filter_by)
            else:
                raise TypeError("Wrong format")
        for user in users:
            self.add_user_rule(user, roles, filter_by)


    def add_user_rule(self, rule, roles=None, filter_by=None):
        user_id = rule['$id']
        roles = _merge(roles, rule.get('roles'))
        filter_by = _merge(filter_by, rule.get('filter_by'))
        if self.compiled_rules.get(user_id) is None:
            self.compiled_rules[user_id] = {}
        if self.compiled_rules[user_id].get('roles') is None:
            self.compiled_rules[user_id]['roles'] = list()
        user_roles = self.compiled_rules[user_id]['roles']
        #        user_roles=[]
        if self.compiled_rules[user_id].get('objects') is None:
            self.compiled_rules[user_id]['objects'] = {}
        for role in roles:
            if role not in user_roles:
                user_roles.append(role)
            if self.compiled_rules[user_id]['objects'].get(role) is None:
                self.compiled_rules[user_id]['objects'][role] = {}

            for controller in self.roles[role]:
                try:
                    filter_object_names = self.BASE[controller]['filter_by']
                    for filter_object_name in filter_object_names:
                        if filter_by and filter_object_name in filter_by:
                            self.compiled_rules[user_id]['objects'][role][filter_object_name] = filter_by[
                                filter_object_name]
                except KeyError:
                    pass

    def expand_roles(self, rules):
        self.expanded_roles = {}
        for user_id, rule in self.compiled_rules.iteritems():
            new_rules = {}
            if not user_id in self.expanded_roles:
                self.expanded_roles[user_id] = {}
            user_acl = self.expanded_roles[user_id]
            for role in rule['roles']:
                role = self.roles[role]
                access = role.get('access')
                if access:
                    user_acl[self.AK] = access
                    continue
                for controller, controllerParams in role.iteritems():
                    if str(controller).startswith("$"):
                        continue
                    access = controllerParams.get('access')
                    if controller not in user_acl:
                        user_acl[controller] = {}
                    if access:
                        user_acl[controller][self.AK] = access
                        continue
                    for action, actionParams in controllerParams.iteritems():
                        access = actionParams.get('access')
                        if action not in user_acl[controller]:
                            user_acl[controller][action] = actionParams
                        else:
                            user_acl[controller][action] = _merge(user_acl[controller][action], actionParams)


    def get_field_recurrent(self, role, controller_name, action_name, field_name):
        r1 = role.get(controller_name, {}).get(field_name, [])
        r2 = role.get(controller_name, {}).get(action_name, {}).get(field_name, [])
        return _merge(r1, r2)

    def isAllowed(self, roles, controller_name, action_name, fields=None):
        res_global, res_controller, res_action = None, None, None
        allowed_fields, denied_fields = [], []
        disable_merge = False

        for role_name in roles:
            if role_name in self.roles:
                role = self.roles[role_name]
                get_field_recurrent = partial(self.get_field_recurrent, role, controller_name, action_name)

                inherit_global_rules = role.get("$inherit", True)
                inherit_controller_rules = inherit_global_rules and role.get(controller_name, {}).get("$inherit", True)

                global_rule = self.__get_access_action(role)
                controller_rule = self.__get_access_action(role.get(controller_name))
                action_rule = self.__get_access_action(role.get(controller_name, {}).get(action_name))

                if not inherit_global_rules:
                    res_global = global_rule
                if not inherit_controller_rules:
                    res_controller = controller_rule
                    res_action = action_rule
                    allowed_fields = get_field_recurrent('allowed_fields')
                    denied_fields = get_field_recurrent('denied_fields')
                    disable_merge = True

                if not disable_merge:
                    res_global = and_ternary(res_global, global_rule)
                    res_controller = and_ternary(res_controller, controller_rule)
                    res_action = and_ternary(res_action, action_rule)
                    allowed_fields = _merge(allowed_fields, get_field_recurrent('allowed_fields'))
                    denied_fields = _merge(denied_fields, get_field_recurrent('denied_fields'))
            else:
                raise ValueError("Role '{}' not found in roles".format(role_name))

        result = res_action if res_action is not None else res_controller if res_controller is not None else res_global or False
        if result is False:
            return False
        result_field = self.isFieldsAllowed(fields, allowed_fields, denied_fields)
        result = and_ternary(result, result_field)

        return result

    def getFieldAccess(self, roles, controller_name, action_name):
        allowed_fields, denied_fields = [], []
        disable_merge = False

        for role_name in roles:
            if role_name not in self.roles:
                raise ValueError("Role '{}' not found in roles".format(role_name))

            role = self.roles[role_name]
            get_field_recurrent = partial(self.get_field_recurrent, role, controller_name, action_name)

            inherit_global_rules = role.get("$inherit", True)
            inherit_controller_rules = inherit_global_rules and role.get(controller_name, {}).get("$inherit", True)

            if not inherit_global_rules:
                pass
            if not inherit_controller_rules:
                allowed_fields = get_field_recurrent('allowed_fields')
                denied_fields = get_field_recurrent('denied_fields')
                disable_merge = True

            if not disable_merge:
                allowed_fields = _merge(allowed_fields, get_field_recurrent('allowed_fields'))
                denied_fields = _merge(denied_fields, get_field_recurrent('denied_fields'))

        return {"allow": allowed_fields, "deny": denied_fields}

    def getAllowedFields(self, roles, controller_name, action_name):
        field_rules = self.getFieldAccess(roles, controller_name, action_name)
        allowed_fields = set(field_rules['allow']).difference(field_rules['deny'])
        return allowed_fields

    def isUserAllowed(self, user_id, controller_name, action_name, fields=None):
        return self.isAllowed(self.compiled_rules.get(user_id, {}).get('roles', []), controller_name, action_name,
                              fields)

    def isFieldsAllowed(self, fields, allowed_fields, denied_fields):
        #if no fields are supplied return result
        if not fields:
            return None

        if not isinstance(fields, list):
            fields = [fields]

        #get allowed and denied
        if allowed_fields is None and denied_fields is None:
            # no field rules
            return None
        for field in fields:
            #check field. Because merging field can be in both filters
            if allowed_fields and (field not in allowed_fields and "$all" not in allowed_fields):
                return False
            if denied_fields and (field in denied_fields or '$all' in denied_fields):
                return False
        return True

    def __get_access_action(self, rule):
        if rule is None:
            return None
        access = rule.get(self.AK)
        if access is not None:
            return True if access == self.ALLOW else False

        #undefined from this scope
        return None

    def __get_filter_data(self, rule):
        if rule is None:
            return None
        filter_by = rule.sget("filter_by")
        return filter_by

    def getFilterRules(self, roles, controller_name, action_name, filter_name):

        res_global, res_controller, res_action = [], [], []
        disable_merge = False
        for role_name in roles:
            if role_name in self.roles:
                role = self.roles[role_name]
                get_field_recurrent = partial(self.get_field_recurrent, role, controller_name, action_name)

                inherit_global_rules = role.get("$inherit", True)
                inherit_controller_rules = inherit_global_rules and role.get(controller_name, {}).get("$inherit", True)

                global_rule = role.get("filter_by", {}).get(filter_name)
                controller_rule = role.get(controller_name, {}).get("filter_by", {}).get(filter_name)
                action_rule = role.get(controller_name, {}).get(action_name, {}).get("filter_by", {}).get(filter_name)

                if not inherit_global_rules:
                    res_global = [global_rule]
                if not inherit_controller_rules:
                    res_controller = [controller_rule]
                    res_action = [action_rule]
                    disable_merge = True

                if not disable_merge:
                    if global_rule:
                        res_global.append(global_rule)
                    if controller_rule:
                        res_controller.append(controller_rule)
                    if action_rule:
                        res_action.append(action_rule)
            else:
                raise ValueError("Role '{}' not found in roles".format(role_name))
        assert isinstance(res_global, list)
        assert isinstance(res_controller, list)
        assert isinstance(res_action, list)
        return res_global, res_controller, res_action


class RBACCollection(RBAC):
    def isFieldsAllowed(self, fields, allowed_fields, denied_fields):
        #if no fields are supplied return result
        if not fields:
            return None

        if not isinstance(fields, list):
            fields = [fields]

        #get allowed and denied
        if allowed_fields is None and denied_fields is None:
            # no field rules
            return None
        for field in fields:
            if field == '_id' and (not denied_fields or denied_fields and field not in denied_fields):
                continue

            #check field. Because merging field can be in both filters
            if allowed_fields and (field not in allowed_fields and "$all" not in allowed_fields):
                return False
            if denied_fields and (field in denied_fields or '$all' in denied_fields):
                return False
        return True


class ACMixinToCollection(object):
    _rbac = RBAC()

    @property
    def rbac(self):
        """
        :rtype : RBAC
        :return:
        """
        return self._rbac


    def is_allowed(self, action):
        self.sess
        self.rbac.isAllowed()

        pass


if __name__ == '__main__':
    pass
