from stilus.nodes.group import Group
from stilus.nodes.string import String


def currentMedia(*args, evaluator=None):

    def look_for_media(node):
        if node.node_name == 'media':
            node.value = evaluator.visit(node.value)
            return str(node)
        else:
            # todo: fix the block getter/setter in Group
            if isinstance(node, Group):
                block = node.get_block()
            elif hasattr(node, 'block'):
                block = node.block
            if block and block.parent and hasattr(block.parent, 'node'):
                return look_for_media(block.parent.node)
        return None

    media = look_for_media(evaluator.closest_block().node)
    if media:
        return String(media)
    else:
        return String('')
