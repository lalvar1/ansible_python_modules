#!/usr/bin/env python

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


DOCUMENTATION = """
---
module: handles two way auth with azure ad
description:
    - returns token to access to final resource
requirements:
    - requests
options:
    azure_ad_auth:
        description:
        - This module will handle azure ad mondern auth and return the
        access token for the final and protected resource.
        required: True

"""

EXAMPLES = """


- azure_ad_auth:
    client_id: "{{ client_id }}"
    client_secret: "{{ client_secret }}"
    target_client_id: "{{ target_client_id }}"
    tenant_id: "{{ tenant_id }}"
"""

from ansible.module_utils.basic import AnsibleModule, env_fallback, return_values
import os.path
import yaml
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            client_id=dict(required=True, type='str'),
            target_client_id=dict(required=True, type='str'),
            client_secret=dict(required=True, type='str'),
            tenant_id=dict(required=True, type='str'),
            # resource=dict(required=True, type='str'),
        )
    )

    CLIENT_ID = str(module.params['client_id'])
    RESOURCE = str(module.params['target_client_id'])
    CLIENT_SECRET = str(module.params['client_secret'])
    TENANT_ID = str(module.params['tenant_id'])
    # FINAL_RESOURCE = str(module.params['resource'])
    AUTHORITY_URL = 'https://login.microsoftonline.com/'
    AUTH_ENDPOINT = '/oauth2/v2.0/authorize'
    TOKEN_ENDPOINT = '/oauth2/token'
    GRANT_TYPE = 'client_credentials'
    body = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'resource': RESOURCE,
        'grant_type': GRANT_TYPE
    }
    url = AUTHORITY_URL + TENANT_ID + TOKEN_ENDPOINT
    result = dict(changed=False, token="Undefined")

    try:

        result['token'] = get_token(url, body)
        result['changed'] = True

    except Exception as e:
        module.fail_json(msg="Exception was {}".format(e))
    #    module.fail_json(**result)

    module.exit_json(**result)


def get_token(url, body):
    SESSION = requests.Session()
    response = requests.post(url, body)
    access_token = response.json()['access_token']
    # auth_state = str(uuid.uuid4())
    # SESSION.auth_state = auth_state
    # SESSION.headers.update({'Authorization': "Bearer {" + access_token + "}",
    #                        'User-Agent': 'adal-sample',
    #                        'Accept': 'application/json',
    #                        'Content-Type': 'application/json',
    #                        'SdkVersion': 'sample-python-adal',
    #                        'return-client-request-id': 'true'})
    # RESOURCE = 'https://domain.com/api/historical_compliance'
    return access_token


if __name__ == "__main__":
    main()