import sublime_plugin

def plugin_loaded():
    """
    Called whenever the plugin is loaded and ensures to import the actual plugin
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.debug("Plugin loaded.")
    from .python import word_navigate

def plugin_unloaded():
    """
    Called whenever the plugin is unloaded and ensures to unload the actual plugin
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.debug("Plugin unloaded.")
    from .python import word_navigate
    word_navigate.plugin_unloaded()

# Make sure to define commands here as it is only the top level python file that sublime will find
# commands in
class WordNavigatePreviousCommand(sublime_plugin.WindowCommand):
    """
    Navigates to the previous same word
    """
    def run(self):
        import logging
        logger = logging.getLogger(__name__)

        from .python import word_navigate
        from .python.sublime_util import util

        logger.info("Running command to find previous word.")
        with util.time_this('Navigated to previous word in'):
            word_navigate.navigate_backward(self.window.active_view())

class WordNavigateNextCommand(sublime_plugin.WindowCommand):
    """
    Navigates to the next same word
    """
    def run(self):
        import logging
        logger = logging.getLogger(__name__)

        from .python import word_navigate
        from .python.sublime_util import util

        logger.info("Running command to find next word.")
        with util.time_this('Navigated to next word in'):
            word_navigate.navigate_forward(self.window.active_view())

class WordNavigatePreviousInLineCommand(sublime_plugin.WindowCommand):
    """
    Navigates to the previous word in the current line
    """
    def run(self):
        import logging
        logger = logging.getLogger(__name__)

        from .python import word_navigate
        from .python.sublime_util import util

        logger.info("Running command to find previous word on the same line.")
        with util.time_this('Navigated to previous word in'):
            word_navigate.navigate_backward_in_line(self.window.active_view())

class WordNavigateNextInLineCommand(sublime_plugin.WindowCommand):
    """
    Navigates to the next word in the current line
    """
    def run(self):
        import logging
        logger = logging.getLogger(__name__)

        from .python import word_navigate
        from .python.sublime_util import util

        logger.info("Running command to find next word on the same line.")
        with util.time_this('Navigated to next word in'):
            word_navigate.navigate_forward_in_line(self.window.active_view())
