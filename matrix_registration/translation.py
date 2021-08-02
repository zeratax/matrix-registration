import os
import re

import yaml

from .constants import __location__


replace_pattern = re.compile(r"{{\s*(?P<name>.[a-zA-Z_\-]+)\s*}}")


def get_translations(lang="en", replacements={}):
    default = _get_translations(replacements=replacements)
    try:
        selected = _get_translations(lang=lang, replacements=replacements)
        return {**default, **selected}
    except IOError:
        return default


def _get_translations(lang="en", replacements={}):
    path = os.path.join(__location__, f"translations/messages.{lang}.yaml")

    with open(path, "r") as stream:
        translations = yaml.load(stream, Loader=yaml.SafeLoader)

    interpolated_translations = {}
    for key, value in translations["weblate"].items():
        match = re.search(replace_pattern, value)
        while match:
            value = value.replace(
                match.group(0), str(replacements[match.group("name")])
            )
            match = re.search(replace_pattern, value)

        interpolated_translations[key] = value

    return interpolated_translations
