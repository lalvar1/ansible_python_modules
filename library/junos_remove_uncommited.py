#!/usr/bin/env python

# Copyright 2018 Facundo Pablo Casares <facundo.p.casares@exxonmobil.com>
#
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
module: junos_remove_uncommited
short_description: Provides a CLI connection to a juniper device
description:
    - This module uses netmiko to connect to a Juniper network device CLI to 
    remove uncommited changes if any, and send and optional broadcast message 
    before doing that
author: Facundo Pablo Casares <facundo.p.casares@exxonmobil.com>
requirements:
    - netmiko
options:
    hostname:
        description:
        - This is the hostname of the Juniper device that the module will 
        connect to 
        required: True
    username:
        description:
        - The username required to authenticate the connection to the Juniper 
        device
        required: True
    password:
        description:
        - The password required to authenticate the connection
        required: True
    timeout:
        description:
        - The connection timeout (default 30 s)
        required: False    
    broadcast_message:
        description:
        - The broadcast message that will be sent to all users logged into
        the device
        required: False

        
"""

EXAMPLES = """

# Remove uncommited changes
- junos_remove_uncommited:
    hostname: "Juniper_router"
    username: "johnconnor"
    password: "illbeback"
    message: "AWX Auto-remediation is in progress, all uncommited changes will be discarded"

"""

from ansible.module_utils.basic import AnsibleModule, env_fallback, return_values
from netmiko import ConnectHandler
import os
import json



def run_module():
    '''
    define the available arguments/parameters that a user can pass to
    the module
    '''
    module_args = dict(
        hostname=dict(required=True, type='str'),
        username=dict(fallback=(env_fallback, ['AD_USERNAME'])),
        password=dict(fallback=(env_fallback, ['AD_PASSWORD']), no_log=True),
        timeout=dict(required=False, type='int', default=30),
        broadcast_message=dict(required=False, type='str',default="AWX Auto-remediation is in progress, all uncommited changes will be discarded")
    )
    '''
    seed the result dict in the object
    we primarily care about changed and state
    change is if this module effectively modified the target
    state will include any data that you want your module to pass back
    for consumption, for example, in a subsequent task
    '''
    result = dict(
        changed=False,
        message=""
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    hostname = str(module.params['hostname'])
    username = str(module.params['username'])
    password = str(module.params['password'])
    timeout = int(module.params['timeout'])
    broadcast_message = str(module.params['broadcast_message'])



    

    
    device_dict={
        'device_type':'juniper_junos',
        'ip':hostname,
        'username': username,
        'password': password
        }


    #Connect to the device
    try:   
        Net_Connect=ConnectHandler(**device_dict)
    except:
        module.fail_json(msg="Could not connect to: {}".format(hostname))

    #Send broadcast message to all connected users
    try:
        output=Net_Connect.send_command('request message all message "{}"'.format(broadcast_message))
    except:
        module.fail_json(msg="Could not sent broadcast message on {}".format(hostname))
            
    #Enter configuration mode
    try:
        output = Net_Connect.config_mode()
    except:
        module.fail_json(msg="Could not enter configuration mode on {}".format(hostname))
        
        
    
    #Check if there are pending commits
    if 'The configuration has been changed but not committed' in output:
        uncommited=True
    else:
        uncommited=False


    #Remove uncommited configurations and if successfull exit the configuration
    if uncommited:
        try: 
            output = Net_Connect.send_command('rollback')
            if 'load complete' in output:
                output = Net_Connect.exit_config_mode()
                Net_Connect.disconnect()
                result['message']='The uncommited changes were removed from {}'.format(hostname)
                result['changed']=True
        except:  
            module.fail_json(msg="Could not remove uncommited config on {}".format(hostname))
    
    if not uncommited:
        result['message']='The device has not uncommited changes'
        Net_Connect.disconnect()

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
