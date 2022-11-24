import base64 as b


def is_int(x):
    try:
        int(x)
        return True
    except:
        return False


def is_hex(x):
    try:
        int(x, 16)
        return True
    except:
        return False


bounceable_tag, non_bounceable_tag = b'\x11', b'\x51'
b64_abc = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890+/')
b64_abc_urlsafe = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890_-')


def calcCRC(message):
    poly = 0x1021
    reg = 0
    message += b'\x00\x00'
    for byte in message:
        mask = 0x80
        while (mask > 0):
            reg <<= 1
            if byte & mask:
                reg += 1
            mask >>= 1
            if reg > 0xffff:
                reg &= 0xffff
                reg ^= poly
    return reg.to_bytes(2, "big")


def account_forms(raw_form, test_only=False):
    if raw_form:
        workchain, address = raw_form.split(":")
        raw_form = f"{workchain}:{address.zfill(64)}"
        workchain, address = int(workchain), int(address, 16)
        address = address.to_bytes(32, "big")
        workchain_tag = b'\xff' if workchain == -1 else workchain.to_bytes(1, "big")
        btag = bounceable_tag
        nbtag = non_bounceable_tag
        # if test_only:
        #  btag = (btag[0] | 0x80).to_bytes(1,'big')
        #  nbtag = (nbtag[0] | 0x80).to_bytes(1,'big')
        preaddr_b = btag + workchain_tag + address
        preaddr_u = nbtag + workchain_tag + address
        b64_b = b.b64encode(preaddr_b + calcCRC(preaddr_b)).decode('utf8')
        b64_u = b.b64encode(preaddr_u + calcCRC(preaddr_u)).decode('utf8')
        b64_b_us = b.urlsafe_b64encode(preaddr_b + calcCRC(preaddr_b)).decode('utf8')
        b64_u_us = b.urlsafe_b64encode(preaddr_u + calcCRC(preaddr_u)).decode('utf8')
        return {'raw_form': raw_form.lower(),
                'bounceable': {'b64': b64_b, 'b64url': b64_b_us},
                'non_bounceable': {'b64': b64_u, 'b64url': b64_u_us},
                'given_type': 'raw_form',
                'test_only': test_only}


def read_friendly_address(address):
    urlsafe = False
    if set(address).issubset(b64_abc):
        address_bytes = b.b64decode(address.encode('utf8'))
    elif set(address).issubset(b64_abc_urlsafe):
        urlsafe = True
        address_bytes = b.urlsafe_b64decode(address.encode('utf8'))
    else:
        raise Exception("Not an address")
    if not calcCRC(address_bytes[:-2]) == address_bytes[-2:]:
        raise Exception("Wrong checksum")
    tag = address_bytes[0]
    if tag & 0x80:
        test_only = True
        tag = tag ^ 0x80
    else:
        test_only = False
    tag = tag.to_bytes(1, 'big')
    if tag == bounceable_tag:
        bounceable = True
    elif tag == non_bounceable_tag:
        bounceable = False
    else:
        raise Exception("Unknown tag")
    if address_bytes[1:2] == b'\xff':
        workchain = -1
    else:
        workchain = address_bytes[1]
    raw_form = str(workchain) + ":" + hex(int.from_bytes(address_bytes[2:-2], "big"))[2:]
    account = account_forms(raw_form, test_only)
    account['given_type'] = "friendly_" + ("bounceable" if bounceable else "non_bounceable")
    return account


def detect_address(unknown_form):
    try:
        if not unknown_form or len(unknown_form) < 2:
            return None

        if is_hex(unknown_form):
            return account_forms("-1:" + unknown_form)
        elif (":" in unknown_form) and is_int(unknown_form.split(":")[0]) and is_hex(unknown_form.split(":")[1]):
            return account_forms(unknown_form)
        else:
            return read_friendly_address(unknown_form)
    except:
        return None


def prepare_address(unknown_form):
    address = detect_address(unknown_form)
    if 'non_bounceable' in address['given_type']:
        return address["non_bounceable"]["b64"]
    return address["bounceable"]["b64"]
