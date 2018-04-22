import yaml


class DictWithRecursion:
    def __init__(self, data=None):
        self._data = data or CommentedMap()

    def _recursive_get(self, data, key, default_value):
        if '.' in key:
            key, next_key = key.split('.', 1)
            next_data = data.get(key, CommentedMap())
            return self._recursive_get(next_data, next_key, default_value)
        return data.get(key, default_value)

    def get(self, key, default_value, allow_recursion=True):
        if allow_recursion and '.' in key:
            return self._recursive_get(self._data, key, default_value)
        return self._data.get(key, default_value)

    def __getitem__(self, key):
        return self.get(key, None)

    def __contains__(self, key):
        return self[key] is not None

    def _recursive_set(self, data, key, value):
        if '.' in key:
            key, next_key = key.split('.', 1)
            if key not in data:
                data[key] = CommentedMap()
            next_data = data.get(key, CommentedMap())
            self._recursive_set(next_data, next_key, value)
            return
        data[key] = value

    def set(self, key, value, allow_recursion=True):
        if allow_recursion and '.' in key:
            self._recursive_set(self._data, key, value)
            return
        self._data[key] = value

    def __setitem__(self, key, value):
        self.set(key, value)

    def _recursive_del(self, data, key):
        if '.' in key:
            key, next_key = key.split('.', 1)
            if key not in data:
                return
            next_data = data[key]
            self._recursive_del(next_data, next_key)
            return
        try:
            del data[key]
            del data.ca.items[key]
        except KeyError:
            pass

    def delete(self, key, allow_recursion=True):
        if allow_recursion and '.' in key:
            self._recursive_del(self._data, key)
            return
        try:
            del self._data[key]
            del self._data.ca.items[key]
        except KeyError:
            pass

    def __delitem__(self, key):
        self.delete(key)


class Config(DictWithRecursion):
    def __init__(self, path)
        super().__init__()
        self.path = path
        self.options = None
    
    def load(self)
        try:
            with open(self.path, 'r') as stream:
                self._data = yaml.load(stream)
        except IOError as e:
            sys.exit('no config found at: "{}"'.format(self.path))
