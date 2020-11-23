#!/usr/bin/env python

DOCUMENTATION = """
---
module: decrypt
short_description: Removes the obfuscated password from the config leaving 
clear-text password on it
description:
    - Removes the obfuscated password from the config leaving 
clear-text password on it, it uses HASHES module_utils for it
author: Luciano Alvarez
requirements:
    - HASHES
options:
    configuration:
        description:
        - This is the configuration you want to de-ofuscate as a string
        required: True
    vendor:
        description:
        - The vendor for the device in which this configuration was extracted 
        from
        required: True
    
"""

EXAMPLES = """


- decryptn:
    configuration: "{{ cisco_running_config }}"
    vendor: cisco

"""

from ansible.module_utils.HASHES.HASHES import *
from ansible.module_utils.basic import *



def main():
    module = AnsibleModule(
        argument_spec=dict(
            configuration=dict(required=True),
            vendor=dict(required=True, type='str'),
        )
    )

    config = str(module.params['configuration'])
    vendor = str(module.params['vendor'])
    
    result = dict(changed=False,clear_config='')
    try:
        clear_config=decrypt_config(**dict(config=config,vendor=vendor))
    except:
        result['changed']=False        
        result['msg']='Unexpected error occured'
        module.fail_json(**result)
    result['changed']=True        
    result['clear_config']=clear_config
    module.exit_json(**result)

        result['clear_config']=decrypt_config(**dict(config=config,vendor=vendor))
        result['changed']=True
    except:
        module.fail_json(**result)
    module.exit_json(**result)

if __name__ == "__main__":
    main()
