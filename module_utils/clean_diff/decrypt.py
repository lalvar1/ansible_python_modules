import string
import re

#################################################################
## globals

MAGIC = "$9$"

###################################
## letter families

FAMILY = ["QzF3n6/9CAtpu0O", "B1IREhcSyrleKvMW8LXx", "7N-dVbwsY2g4oaJZGUDj", "iHkq.mPf5T"]
EXTRA = dict()
for x, item in enumerate(FAMILY):
    for c in item:
        EXTRA[c] = 3 - x

###################################
## forward and reverse dictionaries

NUM_ALPHA = [x for x in "".join(FAMILY)]
ALPHA_NUM = {NUM_ALPHA[x]: x for x in range(0, len(NUM_ALPHA))}

###################################
## encoding moduli by position

ENCODING = [[1, 4, 32], [1, 16, 32], [1, 8, 32], [1, 64], [1, 32], [1, 4, 16, 128], [1, 32, 64]]


def _nibble(cref, length):
    nib = cref[0:length]
    rest = cref[length:]
    if len(nib) != length:
        print("Ran out of characters: hit '%s', expecting %s chars" % (nib, length))
        sys.exit(1)
    return nib, rest


def _gap(c1, c2):
    return (ALPHA_NUM[str(c2)] - ALPHA_NUM[str(c1)]) % (len(NUM_ALPHA)) - 1


def _gap_decode(gaps, dec):
    num = 0
    if len(gaps) != len(dec):
        print("Nibble and decode size not the same!")
        sys.exit(1)
    for x in range(0, len(gaps)):
        num += gaps[x] * dec[x]
    return chr(num % 256)


def juniper9(crypt="$9$DMk5Ftu1rK80OvLXxdVHq.fz6B1heK80ORSeW-dUjH"):
    chars = crypt.split("$9$", 1)[1]
    first, chars = _nibble(chars, 1)
    toss, chars = _nibble(chars, EXTRA[first])
    prev = first
    decrypt = ""
    while chars:
        decode = ENCODING[len(decrypt) % len(ENCODING)]
        nibble, chars = _nibble(chars, len(decode))
        gaps = []
        for i in nibble:
            g = _gap(prev, i)
            prev = i
            gaps += [g]
        decrypt += _gap_decode(gaps, decode)
    return (decrypt)


def cisco7(hash="075D78181D5B405146"):
    V = [0x64, 0x73, 0x66, 0x64, 0x3b, 0x6b, 0x66, 0x6f, 0x41, 0x2c, 0x2e,
         0x69, 0x79, 0x65, 0x77, 0x72, 0x6b, 0x6c, 0x64, 0x4a, 0x4b, 0x44,
         0x48, 0x53, 0x55, 0x42, 0x73, 0x67, 0x76, 0x63, 0x61, 0x36, 0x39,
         0x38, 0x33, 0x34, 0x6e, 0x63, 0x78, 0x76, 0x39, 0x38, 0x37, 0x33,
         0x32, 0x35, 0x34, 0x6b, 0x3b, 0x66, 0x67, 0x38, 0x37]

    i = hash[0:2]
    c = 2
    result = ""
    j = int(i, 10)
    while (c < len(hash)):
        result += chr(int(hash[c:c + 2], 16) ^ V[j])
        j += 1
        c += 2
        j = j % 53
    return (result)


# --------------MAIN FUNCTIONS---------------------------------------------------

def Decrypt(**kwargs):
    '''
    **kwargs=(vendor="Cisco","Juniper", hashed = Hashed password)
    '''
    if not kwargs.get("hashed"):
        return ("")
    if "$9$" not in kwargs.get("hashed") and kwargs.get("vendor") == 'Juniper' or kwargs.get(
            "hashed") == "" and kwargs.get("Vendor") == 'Cisco':
        return ("")
    if kwargs.get("vendor") == "Cisco":
        password = cisco7(kwargs.get("hashed"))
    elif kwargs.get("vendor") == "Juniper":
        password = juniper9(kwargs.get("hashed"))
    else:
        print("Please select either Cisco or Juniper")
        return ("")

    return (password)


def Validate_Md5(**kwargs):
    '''
    **kwargs=(
    password= Clean text password,
    hashed= Hashed Md5 password)

    Return string containing status
    '''
    if not kwargs.get("hashed"):
        return ("Error,hash not provided")
    if "$1$" not in kwargs.get('hashed'):
        return ("Error, hash not well defined")
    try:
        from passlib.hash import md5_crypt
    except:
        return ("This module requires passlib module")
    try:
        salt = re.search('\$\d\$(.*)\$', kwargs.get("hashed")).group(1)
        try:
            h = md5_crypt.hash(kwargs.get("password"), salt=salt)
        except:
            return ("Error, password not defined")
    except:
        return ("Error, hash not defined")
    if h == kwargs.get("hashed"):
        return ("Match")
    else:
        return ("Not Match")


def hashing(hash='', plain=''):
    if hash.startswith("$1$"):
        return (Validate_Md5(password=plain, hashed=hash))
    elif hash.startswith("$9$"):
        return (Decrypt(hashed=hash, vendor="Juniper"))
    else:
        return (Decrypt(hashed=hash, vendor="Cisco"))


def decrypt_config(**kwargs):
    '''
    **kwargs=dict(
    config= Configuration as string,
    vendor= Cisco or Juniper
    )

    Return configuration decrypted
    '''

    if not kwargs.get("config"):
        return ("")
    config_string = kwargs.get('config').replace('\\n', '\n')

    if kwargs.get("vendor") == "Cisco":
        hash_list = re.findall('(?:(?:key|password) 7|-key \\S+ md5) (\\S+)', config_string)
        clean_config = config_string
        for h in hash_list:
            replacement = hashing(h)
            clean_config = clean_config.replace(h, replacement)
        return (clean_config)
    elif kwargs.get("vendor") == "Juniper":
        hash_list = re.findall('.*(\\$9\\$\\S+)\\";.*', config_string)
        clean_config = config_string
        for h in hash_list:
            replacement = hashing(h)
            clean_config = clean_config.replace(h, replacement)
        return (clean_config)
    else:
        return ("")


# ---------------------------------------------------------------------




def main():
    print(hashing("075D78181D5B405146"))
    #print(hashing("$9$DMk5Ftu1rK80OvLXxdVHq.fz6B1heK80ORSeW-dUjH"))
    #print(hashing("$1$o/3C$e.lNwP28.0/h8ZAq6a6OZ1", "cisco"))
    #print(hashing("$1$o/3C$e.lNwP28.0/h8ZAq6a6OZ1", "cosco"))

if __name__ == '__main__':
    main()


