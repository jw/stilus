import json

from stilus.exceptions import StilusError
from stilus.nodes.boolean import Boolean
from stilus.nodes.ident import Ident
from stilus.nodes.null import null
from stilus.nodes.object_node import ObjectNode
from stilus.utils import assert_string, coerce, lookup, parse_string


# todo: this needs a cleaning
def json_function(path, local=None, name_prefix=None, evaluator=None):
    assert_string(path, 'path')

    def convert(content, options):
        ret = ObjectNode()
        leave_strings = options.get('leave-strings').to_boolean()
        for key in content:
            val = content[key]
            if isinstance(val, dict):
                ret.set(key, convert(val, options))
            else:
                val = coerce(val, raw=False)
                if val and val.node_name == 'string' and \
                        leave_strings.is_false():
                    val = parse_string(val.string)
                ret.set(key, val)
        return ret

    # lookup
    path = path.string
    found = lookup(path, evaluator.paths, evaluator.filename)
    options = None
    if local and hasattr(local, 'node_name') and \
            local.node_name == 'objectnode':
        options = local

    if not found:
        if options:
            optional = options.get('optional')
            if optional and optional.first().is_true():
                return null
        raise StilusError(f'failed to locate .json file {path}')

    # read
    with open(found, 'r') as reader:
        content = json.load(reader)

    if options:
        return convert(content, options)
    else:
        old_json_function(content, local, name_prefix, evaluator)


def old_json_function(content, local=None, name_prefix=None, evaluator=None):

    def convert(content, prefix=None):
        if prefix:
            prefix = prefix + '-'
        else:
            prefix = ''
        for key in content:
            val = content[key]
            name = prefix + key
            if isinstance(val, dict):
                convert(val, name)
            else:
                val = coerce(val, raw=False)
                if val.node_name == 'string':
                    val = parse_string(val.string)
                scope.add(Ident(name_prefix + name, val))

    if name_prefix:
        assert_string(name_prefix, 'name_prefix')
        name_prefix = name_prefix.value
    else:
        name_prefix = ''

    if local:
        local = local.to_boolean()
    else:
        local = Boolean(local)

    if local.is_true():
        scope = evaluator.get_current_scope()
    else:
        scope = evaluator.common.scope()

    convert(content)
