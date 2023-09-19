import os
import time
import hmac
import hashlib
import base64
import datetime
import pytz

from . import defaults


__all__ = (
    'activity_gen',
    'clear_screen',
    'device_gen',
    'get_timezone',
    'signature_gen',
    'update_device'
)


def device_gen(id=os.urandom(20)):
    info = bytes.fromhex(defaults.prefix) + id
    device = (info + hmac.new(
        bytes.fromhex(defaults.dev_key),
        info, hashlib.sha1
    ).digest()).hex().upper()
    return device


def signature_gen(data):
    info = bytes.fromhex(defaults.prefix) + hmac.new(
        bytes.fromhex(defaults.sig_key),
        data.encode("utf-8"),
        hashlib.sha1
    ).digest()
    signature = base64.b64encode(info).decode('utf-8')
    return signature


def update_device(device):
    id = bytes.fromhex(device)[1:21]
    return device_gen(id)


def activity_gen():
    return list(dict(start=int(time.time()), end=int(time.time()+300)) for _ in range(50))


def get_timezone(hour=23, gmt=None):
    zones = ('Etc/GMT' + (f'+{i}' if i > 0 else str(i)) for i in range(-12, 12))
    for _ in (['Etc/GMT' + (f'+{gmt}' if gmt > 0 else str(gmt))] if isinstance(gmt, int) else zones):
        zone = datetime.datetime.now(pytz.timezone(_))
        if not gmt and int(zone.strftime('%H')) != hour:
            continue
        return int(zone.strftime('%Z').replace('GMT', '00')) * 60


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
