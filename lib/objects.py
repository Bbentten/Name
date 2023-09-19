class Obj:
    __slots__ = ('json',)

    def __init__(self, json):
        self.json = json


class UserProfile(Obj):

    @property
    def id(self):
        return self.json.get('uid')

    @property
    def nickname(self):
        return self.json.get('nickname')


class Account(Obj):

    @property
    def email(self):
        return self.json.get('email')

    @property
    def phone(self):
        return self.json.get('phoneNumber')
