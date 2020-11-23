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
module: juniper_cli
short_description: Provides a CLI configuration connection to a juniper device
description:
    - This module uses netmiko to connect to a Juniper network device CLI and
enter into configure exclusive mode
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
    lines:
        description:
        - The lines sent to the device CLI
        required: True
    confirm:
        description:
        - The commit confirm timeout 
        required: False

        
"""

EXAMPLES = """

# Remove uncommited changes
- juniper_cli:
    hostname: "montevideo"
    username: "cavani"
    password: "suarez"
    lines: 
    - delete system services netconf ssh port 22

"""

from ansible.module_utils.basic import AnsibleModule, env_fallback, return_values
from netmiko import ConnectHandler
import os
import json
import time



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
        lines=dict(required=True, type='list'),
        confirm=dict(required=False, type='int',default=2)
    )
    '''
    '''
    result = dict(
        changed=False,
        message=""
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    hostname = str(module.params['hostname'])
    username = str(module.params['username'])
    password = str(module.params['password'])
    timeout = int(module.params['timeout'])
    lines = list(module.params['lines'])
    confirm = int(module.params['confirm'])


    

    
    device_dict={
        'device_type':'juniper_junos',
        'ip':hostname,
        'username': username,
        'password': password,
        'global_delay_factor': 4

    }


    #Connect to the device
    try:   
        Net_Connect=ConnectHandler(**device_dict)
    except:
        module.fail_json(msg="Could not connect to: {}".format(hostname))

    #Enter configuration mode
    try:
        output = Net_Connect.config_mode()
    except:
        module.fail_json(msg="Could not enter configuration mode on {}".format(hostname))

    #Send commands to device
    try:
        for line in lines:
            output=Net_Connect.send_command(line, auto_find_prompt=False)
    except:
        module.fail_json(msg="Could not sent commands to: {}".format(hostname))
        
    #Check if there were any changes into the device
    #try:
    #    output = Net_Connect.send_command('show configuration | compare',expect_string='')
    #    if output!='\n':
    #        result['changed']=True
    #        result['msg']=str(output)
    #except:
    #    module.fail_json(msg="Could not check changes on : {}".format(hostname))        
        
 
    #Send commit confirmed
    try:
        output=Net_Connect.send_command('commit confirmed {}'.format(confirm),expect_string='', auto_find_prompt=False)
    except:
        module.fail_json(msg="Could commit confirmed the configuration to: {}, {}".format(hostname,output))
 

    #Exit config mode
    #try:
    #    output=Net_Connect.send_command('exit',expect_string='')
    #except:
    #    module.fail_json(msg="Could not exit the configure mode in : {}".format(hostname))
     
    #Closing the connection
    #Net_Connect.disconnect()
     
    #time.sleep(30) 
    #Confirm the commit to the device
    try:   
     #   Net_Connect=ConnectHandler(**device_dict)
     #   output = Net_Connect.config_mode()
        output = Net_Connect.send_command('commit', auto_find_prompt=False)
        result['changed']=True
        result['message']=str(output)
        output=Net_Connect.send_command('exit',expect_string='', auto_find_prompt=False)
        Net_Connect.disconnect()
        
    except:
        module.fail_json(msg="Could not confirm the commit to: {}, rollback will be performed in less than: {}".format(hostname,confirm))


    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
