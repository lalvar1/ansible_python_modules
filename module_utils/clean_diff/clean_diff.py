import os
import decrypt
import re
import string
import copy

def decrypt_and_clean_diff(config, vendor):

    parents = {}
    parents_commands = {}
    commands = []
    compliance = "Pass"
    if not config:
        return  compliance
    clear_config = decrypt.decrypt_config(**dict(config=config, vendor=vendor))
    #clear_config = clear_config.splitlines()
    #print(clear_config)

    if vendor == 'Juniper':

        clear_config = clear_config.splitlines()
        for line in clear_config:
            line=line.strip('-').strip('+').strip().strip('"')
            #line= re.sub('.*(\$9\$\S+)\\";.*','',line)
            if 'edit' in line:
                dict_init={line: []}
                parents.update(dict_init)
                parent=line
                commands = []
                continue
            commands += [line]
            load_commands={ parent: commands}
            parents.update(load_commands)
        #parents = ''.join(parents)
        #print(parents)
        parents_before= dict(parents)
        for key in parents.keys():
            parents[key] = list(filter(lambda x: parents[key].count(x) == 1, parents[key]))
            if key == "[edit system services]" \
                    and parents[key] == ['netconf {', 'ssh;', '}']:
                continue
            if parents[key] and parents[key] != ['port 22;']:
                 compliance = "Fail"
        return compliance

    elif vendor == 'Cisco':

        clear_config = clear_config.strip('"')
        clear_config = clear_config.splitlines()
        parent = 'commands'
        #print(clear_config)
        for line in clear_config:
            line = line.strip('"').strip()
            line = re.sub('no ', '', line)
            commands += [line]
            load_commands = {parent: commands}
            parents.update(load_commands)

        for key in parents.keys():
            parents[key] = list(filter(lambda x: parents[key].count(x) == 1, parents[key]))
        if not parents['commands']:
            compliance = "Pass"
            return compliance

        for line in clear_config:
            if not line.startswith(' '):
                if 'no' in line:
                    line = re.sub('no ', '', line)
                    line = line.lstrip()
                dict_init = {line: []}
                parents_commands.update({line: []})
                parent = line
                commands = []
                continue
            line = re.sub('no ', '', line)
            line = line.lstrip()
            commands += [line]
            load_commands = {parent: commands}
            parents_commands.update(load_commands)

        keys_to_remove = []
        for key in parents_commands.keys():
            parents_commands[key] = list(filter(lambda x: parents_commands[key].count(x) == 1, parents_commands[key]))

            if parents_commands[key]:
                compliance = "Fail"
                return compliance
            elif not parents_commands[key] and ('group server' in key or 'tacacs server' in key):
                keys_to_remove.append(key)
               #regex = re.compile('tacacs server (NDA-NA|NDA-AP|NDA-EAME)')
               #diff_tacacs_servers = list(filter(regex.match, parents_commands[key]))
               #if diff_tacacs_servers:
               #     compliance = "Pass"
                    #continue
               #compliance = "Fail"
        for key in keys_to_remove:
            parents_commands.pop(key)
        if parents_commands.keys():
            compliance = "Fail"
        else:
            compliance = "Pass"
        return compliance
