import logging

from stilus.nodes.null import null

log = logging.getLogger(__name__)


def trace(evaluator=None):
    print(f'{evaluator.stack}')
    log.info(f'{evaluator.stack}')
    return null
