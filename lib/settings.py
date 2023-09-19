from contextlib import suppress
import json
import os

__all__ = ('Settings',)


class Settings:

    __slots__ = (
        'acc_file',
        'community_link',
        'lambda_format',
        'language',
        'path',
        'proxy'
    )

    def __init__(self, __filename='settings.json', /):
        self.path = os.path.abspath(__filename)
        self.acc_file = 'accounts.json'
        self.language = 'en'
        self.proxy = None
        self.community_link = None
        self.lambda_format = 'lambda dict_array: (dict(' \
                             'email=a.get(\'email\'), ' \
                             'password=a.get(\'password\'), ' \
                             'device=a.get(\'device\'), ' \
                             'sid=a.get(\'sid\')' \
                             ') for a in dict_array)'

    def load(self, filename: str = None):
        if not filename:
            filename = self.path
        if os.path.exists(filename):
            with suppress(json.JSONDecodeError), open(filename, 'r') as f:
                content = json.loads(f.read())
                self.loads(content)
        else:
            self.save()

    def loads(self, config: dict):
        if 'path' in config:
            self.path = config['path']
        if 'language' in config:
            self.language = config['language']
        if 'acc_file' in config:
            self.acc_file = config['acc_file']
        if 'proxy' in config:
            self.proxy = config['proxy']
        if 'community_link' in config:
            self.community_link = config['community_link']
        if 'lambda_format' in config:
            self.lambda_format = config['lambda_format']

    def save(self, filename: str = None):
        if not filename:
            filename = self.path
        with open(filename, mode='w') as f:
            f.write(self.dumps(indent=4))

    def dumps(self, **kwargs) -> str:
        return json.dumps(self.to_dict(), **kwargs)

    def to_dict(self):
        return dict(
            path=self.path,
            acc_file=self.acc_file,
            lambda_format=self.lambda_format,
            language=self.language,
            proxy=self.proxy,
            community_link=self.community_link
        )

    def get_accounts(self):
        assert os.path.exists(self.acc_file), '%r no exists.' % self.acc_file
        with open(self.acc_file, 'r') as f:
            try:
                content = json.loads(f.read())
            except json.JSONDecodeError:
                content = f.readlines()
        try:
            decode = eval(self.lambda_format)
        except SyntaxError:
            decode = eval(Settings().lambda_format)
        return decode(content)
