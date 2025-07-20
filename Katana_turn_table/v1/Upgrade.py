import logging

import Utils


__all__ = ['Upgrade']

log = logging.getLogger("TurnTable.Upgrade")


def Upgrade(node):
    Utils.UndoStack.DisableCapture()
    try:
        pass
        # This is where you would detect an out-of-date version:
        #    node.getParameter('version')
        # and upgrade the internal network.
    except Exception as exception:
        log.exception('Error upgrading TurnTable node "%s": %s'
                      % (node.getName(), str(exception)))
    finally:
        Utils.UndoStack.EnableCapture()