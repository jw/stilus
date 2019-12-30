def type_function(node, evaluator=None):
    if node.node_name == "objectnode":
        res = "object"
    else:
        res = node.node_name
    return res
