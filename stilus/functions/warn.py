from stilus.nodes import null
from stilus.utils import assert_type

import logging
log = logging.getLogger(__name__)


def warn(msg, evaluator=None):
    assert_type(msg, 'string', 'msg')
    print(f'Warning: {msg.value}')
    log.warning(f'Warning: {msg.value}')
    return null
