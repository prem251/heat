# vim: tabstop=4 shiftwidth=4 softtabstop=4

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

from heat.engine import resource

from heat.openstack.common import log as logging

logger = logging.getLogger(__name__)


class GenericResource(resource.Resource):
    '''
    Dummy resource for use in tests
    '''
    properties_schema = {}

    def handle_create(self):
        logger.warning('Creating generic resource (Type "%s")' % self.type())

    def handle_update(self, json_snippet, tmpl_diff, prop_diff):
        logger.warning('Updating generic resource (Type "%s")' % self.type())
