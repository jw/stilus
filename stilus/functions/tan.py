import logging

from stilus.nodes import null

log = logging.getLogger(__name__)


def tan(evaluator=None):
    print(f'{evaluator.stack}')
    log.info(f'{evaluator.stack}')
    return null
