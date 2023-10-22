from . import settings as settings_module
# Settings initialized in the log module, to ensure that the settings object exists but to also be
# able to log initialization

from .sublime_util import log
# Call reinit to handle when this file is saved and plugin reloaded
log.reinit(settings_module)

from . import index
from . import util
from .settings import settings
from .sublime_util import view as view_util
from .sublime_util import selection

import logging
logger = logging.getLogger(__name__)

import sublime
import sublime_plugin

from typing import Union

def plugin_unloaded():
    """
    Called when plugin is unloaded
    """

    # Make sure to remove log handlers etc.
    log.deinit(settings_module)

def _get_region_of_word_closest_to_region(view   : sublime.View,
                                          region  : sublime.Region,
                                          forward : bool) -> sublime.Region:
    """
    Gets the region of the word closest to a region

    :param view:    The applicable view
    :param region:    The applicable region
    :param forward: Whether to move forwards or backwards
    """

    if view_util.is_not_part_of_any_word(view, region):
        logger.debug(f"No word selected ('{view.substr(region)}') - finding closest.")
        caret_pt = selection.get_caret_point(view)
        if forward:
            return view_util.get_next_word_region_from_pt(view, caret_pt, False)
        else:
            return view_util.get_previous_word_region_from_pt(view, caret_pt, False)
    elif view_util.is_single_complete_word(view, region):
        logger.debug(f"Single word '{view.substr(region)}' selected - finding closest.")
        word_region = region
    else:
        if view_util.is_multiple_complete_words(view, region):
            if not settings.allow_multiple_words:
                if settings.expand_first:
                    logger.debug(
                        f"Multiple words ('{view.substr(region)}') selected "
                        "- expanding to single word under caret.")
                    caret_pt = selection.get_caret_point(view)
                    return view_util.get_closest_word_region_from_pt(view, caret_pt, False)
                else:
                    logger.debug(f"Multiple words ('{view.substr(region)}') selected "
                        "- finding next closest single word from caret.")
                    caret_pt = selection.get_caret_point(view)
                    word_region = view_util.get_closest_word_region_from_pt(view, caret_pt, False)
            else:
                logger.debug(f"Multiple words ('{view.substr(region)}') selected "
                    "- finding next closest combination of words.")
                word_region = region
        elif view_util.is_part_of_multiple_words(view, region):
            if not settings.allow_multiple_words:
                if settings.expand_first:
                    logger.debug(
                        f"Part of multiple words ('{view.substr(region)}') selected "
                        "- expanding to single word under caret.")
                    caret_pt = selection.get_caret_point(view)
                    return view_util.get_closest_word_region_from_pt(view, caret_pt, False)
                else:
                    logger.debug(f"Part of multiple words ('{view.substr(region)}') selected "
                        "- finding next closest single word from caret.")
                    caret_pt = selection.get_caret_point(view)
                    word_region = view_util.get_closest_word_region_from_pt(view, caret_pt, False)
            else:
                if settings.expand_first:
                    logger.debug(f"Part of multiple words ('{view.substr(region)}') selected "
                        "- expanding to words.")
                    return view.word(region)
                else:
                    logger.debug(f"Part of multiple words ('{view.substr(region)}') selected "
                        "- finding next closest combination of words.")
                    word_region = region
        else:
            if settings.expand_first:
                logger.debug(f"Part of single word ('{view.substr(region)}') selected "
                    "- expanding to word")
                return view.word(region)
            else:
                logger.debug(f"Part of single word ('{view.substr(region)}') selected "
                    "- finding closest.")
                word_region = view.word(region)

    # Get index if we are using it
    _id = view.buffer().id()

    idx = None
    if settings.use_index:
        try:
            idx = index.get_index(_id)
        except KeyError as e:
            logger.warning(f"Failed getting index: {e}")

    if idx is not None:
        logger.warning(f"Not implemented.")
    else:
        # Error getting index or not using it
        logger.debug(f"No index - navigating manually.")
        return view_util.get_region_of_closet_same_word(
            view, word_region, forward, settings.wrap_buffer, settings.case_sensitive)

def _get_region_of_word_closest_to_selection(view     : sublime.View,
                                             forward  : bool
                                             ) -> sublime.Region:
    """
    Gets the region of the word closest to the current selection

    :param view:    The applicable view
    :param forward: Whether to move forwards or backwards
    """

    if selection.is_multiple_regions_selected(view):
        logger.warning("Multiple regions selected - doing nothing.")
        return None

    sel_region = selection.get_single_selected_region(view)
    return _get_region_of_word_closest_to_region(view, sel_region, forward)

def _navigate(view      : sublime.View,
             forward    : bool
             ) -> None:
    """
    Navigates to an adjacent same word

    :param view:    The applicable view
    :param forward: Whether to move forwards or backwards
    """

    region = _get_region_of_word_closest_to_selection(view, forward)

    if region is not None:
        word = view.substr(region)

        if forward:
            logger.debug(f"Next word is '{word}'.")
        else:
            logger.debug(f"Previous word is '{word}'.")
        selection.select_and_zoom_to_region(view, region)

def _get_region_of_closest_word_in_line(view     : sublime.View,
                                        forward  : bool
                                       ) -> sublime.Region:
    """
    Gets the region of the word closest to the current selection in the current line

    :param view:    The applicable view
    :param forward: Whether to move forwards or backwards
    """

    if selection.is_multiple_regions_selected(view):
        logger.warning("Multiple regions selected - doing nothing.")
        return None

    region = selection.get_single_selected_region(view)

    if view_util.is_not_part_of_any_word(view, region):
        logger.debug(f"No word selected ('{view.substr(region)}').")
        caret_pt = selection.get_caret_point(view)
        return view_util.get_region_of_closest_word_in_line(
            view, caret_pt, forward, settings.wrap_line)
    elif view_util.is_single_word(view, region):
        logger.debug(f"Single word '{view.substr(region)}' selected.")
        word_region = region
    else:
        logger.debug(f"Multiple or parts of word(s) selected ('{view.substr(region)}').")

        if settings.expand_first:
            logger.debug(f"'{view.substr(region)}' not a word - expanding to word.")
            caret_pt = selection.get_caret_point(view)
            return view_util.get_closest_word_region_from_pt(view, caret_pt, True)
        else:
            logger.debug(f"Text within a word ('{view.substr(region)}') selected.")
            word_region = view.word(region)

    caret_pt = selection.get_caret_point(view)

    return view_util.get_region_of_closest_word_in_line(
            view, caret_pt, forward, settings.wrap_line)

def _navigate_in_line(view       : sublime.View,
                      forward    : bool
                      ) -> None:
    """
    Navigates to an adjacent word in the current line

    :param view:    The applicable view
    :param forward: Whether to move forwards or backwards
    """

    region = _get_region_of_closest_word_in_line(view, forward)

    if region is not None:
        word = view.substr(region)

        if forward:
            logger.debug(f"Next word is '{word}'.")
        else:
            logger.debug(f"Previous word is '{word}'.")
        selection.select_and_zoom_to_region(view, region)

def navigate_backward(view : sublime.View) -> None:
    """
    Navigates to the previous same word

    :param view: The applicable view
    """

    return _navigate(view, False)

def navigate_forward(view : sublime.View) -> None:
    """
    Navigates to the next same word

    :param view: The applicable view
    """

    return _navigate(view, True)

def navigate_backward_in_line(view : sublime.View) -> None:
    """
    Navigates to the previous word in the current line

    :param view: The applicable view
    """

    return _navigate_in_line(view, False)

def navigate_forward_in_line(view : sublime.View) -> None:
    """
    Navigates to the next word in the current line

    :param view: The applicable view
    """

    return _navigate_in_line(view, True)
