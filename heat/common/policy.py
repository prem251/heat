# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2011 OpenStack, LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

# Based on glance/api/policy.py
"""Policy Engine For Heat"""

import json
import os.path

from oslo.config import cfg

from heat.common import exception
import heat.openstack.common.log as logging
from heat.openstack.common import policy

logger = logging.getLogger(__name__)

policy_opts = [
    cfg.StrOpt('policy_file', default='policy.json'),
    cfg.StrOpt('policy_default_rule', default='default'),
]

CONF = cfg.CONF
CONF.register_opts(policy_opts)


DEFAULT_RULES = {
    'default': policy.TrueCheck(),
}


class Enforcer(object):
    """Responsible for loading and enforcing rules."""

    def __init__(self, scope='heat', exc=exception.Forbidden):
        self.scope = scope
        self.exc = exc
        self.default_rule = CONF.policy_default_rule
        self.policy_path = self._find_policy_file()
        self.policy_file_mtime = None
        self.policy_file_contents = None

    def set_rules(self, rules):
        """Create a new Rules object based on the provided dict of rules."""
        rules_obj = policy.Rules(rules, self.default_rule)
        policy.set_rules(rules_obj)

    def load_rules(self):
        """Set the rules found in the json file on disk."""
        if self.policy_path:
            rules = self._read_policy_file()
            rule_type = ""
        else:
            rules = DEFAULT_RULES
            rule_type = "default "

        text_rules = dict((k, str(v)) for k, v in rules.items())

        self.set_rules(rules)

    @staticmethod
    def _find_policy_file():
        """Locate the policy json data file."""
        policy_file = CONF.find_file(CONF.policy_file)
        if policy_file:
            return policy_file
        else:
            logger.warn(_('Unable to find policy file'))
            return None

    def _read_policy_file(self):
        """Read contents of the policy file

        This re-caches policy data if the file has been changed.
        """
        mtime = os.path.getmtime(self.policy_path)
        if not self.policy_file_contents or mtime != self.policy_file_mtime:
            logger.debug(_("Loading policy from %s") % self.policy_path)
            with open(self.policy_path) as fap:
                raw_contents = fap.read()
                rules_dict = json.loads(raw_contents)
                self.policy_file_contents = dict(
                    (k, policy.parse_rule(v))
                    for k, v in rules_dict.items())
            self.policy_file_mtime = mtime
        return self.policy_file_contents

    def _check(self, context, rule, target, *args, **kwargs):
        """Verifies that the action is valid on the target in this context.

           :param context: Heat request context
           :param rule: String representing the action to be checked
           :param object: Dictionary representing the object of the action.
           :raises: self.exc (defaults to heat.common.exception.Forbidden)
           :returns: A non-False value if access is allowed.
        """
        self.load_rules()

        credentials = {
            'roles': context.roles,
            'user': context.username,
            'tenant': context.tenant,
        }

        return policy.check(rule, target, credentials, *args, **kwargs)

    def enforce(self, context, action, target):
        """Verifies that the action is valid on the target in this context.

           :param context: Heat request context
           :param action: String representing the action to be checked
           :param object: Dictionary representing the object of the action.
           :raises: self.exc (defaults to heat.common.exception.Forbidden)
           :returns: A non-False value if access is allowed.
        """
        _action = '%s:%s' % (self.scope, action)
        return self._check(context, _action, target, self.exc, action=action)

    def check(self, context, action, target):
        """Verifies that the action is valid on the target in this context.

           :param context: Heat request context
           :param action: String representing the action to be checked
           :param object: Dictionary representing the object of the action.
           :returns: A non-False value if access is allowed.
        """
        return self._check(context, action, target)
