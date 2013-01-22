from __future__ import unicode_literals
from copy import deepcopy


def _merge(a, b):
    '''recursively merges dict's. not just simple a['key'] = b['key'], if
    both a and bhave a key who's value is a dict then dict_merge is called
    on both values and the result stored in the returned dictionary.'''
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


class RBACL(object):
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

    def __init__(self, settings):
        self.compiled_rules = {}
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
        if self.compiled_rules.get(user_id) == None:
            self.compiled_rules[user_id] = {}
        if self.compiled_rules[user_id].get('roles') == None:
            self.compiled_rules[user_id]['roles'] = list()
        user_roles = self.compiled_rules[user_id]['roles']
        #        user_roles=[]
        if self.compiled_rules[user_id].get('objects') == None:
            self.compiled_rules[user_id]['objects'] = {}
        for role in roles:
            if role not in user_roles:
                user_roles.append(role)
            if self.compiled_rules[user_id]['objects'].get(role) == None:
                self.compiled_rules[user_id]['objects'][role] = {}

            for controller in self.roles[role]:
                try:
                    filterobjectname = self.BASE[controller]['filter_by']
                    for finame in filterobjectname:
                        if filter_by and finame in filter_by:
                            self.compiled_rules[user_id]['objects'][role][finame] = filter_by[finame]
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
                    access = controllerParams.get('access')
                    if controller not in user_acl: user_acl[controller] = {}
                    if access:
                        user_acl[controller][self.AK] = access
                        continue
                    for action, actionParams in controllerParams.iteritems():
                        access = actionParams.get('access')
                        if action not in user_acl[controller]:
                            user_acl[controller][action] = actionParams
                        else:
                            user_acl[controller][action] = _merge(user_acl[controller][action], actionParams)


    def isAllowed(self, user_id, controller_name, action_name, fields=None):
        user_acl = self.expanded_roles.get(user_id)
        #check global level access action
        global_rule = self.__get_access_action(user_acl)
        if global_rule != None: return global_rule
        #check controller level access action
        controller_rule = user_acl.get(controller_name)
        controller_access = self.__get_access_action(controller_rule)
        if  controller_access != None: return controller_access
        #check action level access action
        action_rule = controller_rule.get(action_name)
        action_access = self.__get_access_action(action_rule)
        if action_access != True: return False

        #check fields access
        are_fields_allowed = self.isFieldsAllowed(fields, action_rule.get('allowed_fields'),
                                                  action_rule.get('denied_fields'))
        if are_fields_allowed: return True
        return False

    def isFieldsAllowed(self, fields, allowed_fields, denied_fields):
        #if no fields are supplied return result
        if not fields:
            return True

        if not isinstance(fields, list): fields = [fields]

        #get allowed and denied
        if allowed_fields and  '$all' in allowed_fields: return  True
        if allowed_fields == None and denied_fields == None:
            # no field rules
            return True
        for field in fields:
            #check field. Because merging field can be in both filters
            if allowed_fields and field not in allowed_fields:
                return False
            if denied_fields and field in denied_fields:
                return False
        return True


    def __get_access_action(self, rule):
        if rule == None:
            return False
        access = rule.get(self.AK)
        if access != None:
            return  True if access == self.ALLOW else False

        #undefined from this scope
        return None


if __name__ == '__main__':
    pass
