#!/usr/bin/env python

DOCUMENTATION = """
---
module: decrypt a correct false compliances
short_description: Removes the obfuscated password from the config leaving 
clear-text password on it
description:
    - Removes the obfuscated password from the config leaving 
clear-text password on it, it uses HASHES module_utils for it. Parses the de-ofucasted difference config and determines
whether there is actually a non-compliance.
author: Luciano Alvarez 
requirements:
    - decryp module
options:
    diff_config:
        description:
        - This is difference configuration provided by NAPALM you want to de-ofuscate, parse and recognize the 
        diff commands that are equal. 
        required: True
    
"""

EXAMPLES = """


- decrypt_and_clean_diff:
    diff_config: "{{ napalm_diff_config }}"
"""

#from ansible.module_utils.HASHES.HASHES import *
#from ansible.module_utils.clean_diff import clean_diff 
#from ansible.module_utils.clean_diff import decrypt
from ansible.module_utils.basic import AnsibleModule, env_fallback, return_values
from ansible.module_utils.clean_diff import clean_diff
import os.path
import yaml


def main():
    module = AnsibleModule(
        argument_spec=dict(
            diff_config=dict(required=True),
            vendor=dict(required=True, type='str'),
        )
    )

    config = module.params['diff_config']
    vendor = str(module.params['vendor'])
    
    result = dict(changed=False,compliance=True)
    
    try:
        result['compliance']=clean_diff.decrypt_and_clean_diff(config, vendor)
        result['changed']=True
    except Exception as e:
        module.fail_json(msg="Exception was {}".format(e))
    #    module.fail_json(**result)
    
    module.exit_json(**result)


if __name__ == "__main__":
    main()
