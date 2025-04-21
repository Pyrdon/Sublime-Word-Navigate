"""
Module handling stuff related to the current selection
"""

import logging

# Local logger
logger = logging.getLogger(__name__)

import sublime

from typing import Union

def get_caret_points(view : sublime.View) -> int:
    """
    Gets the positions of all carets

    :param view: The applicable view
    """

    return [region.b for region in view.sel()]

def get_caret_point(view : sublime.View) -> int:
    """
    Gets the position of the caret.

    :param view: The applicable view
    :raises RuntimeError: Raised when several regions are selected
    """

    if is_multiple_regions_selected(view):
        raise RuntimeError("Multiple regions selected!")

    return get_caret_points(view)[0]

def is_multiple_regions_selected(view : sublime.View) -> bool:
    """
    Determins if multiple regions are selected

    :param view: The applicable view
    """

    return len(view.sel()) > 1

def get_first_selected_region(view : sublime.View) -> Union[sublime.Region, None]:
    """
    Gets the first selected region (as in earliest/upmost in buffer), not specifically the region
    that was selected first in time.

    :param view: The applicable view
    """

    sel = view.sel()
    if sel is None:
        return None
    else:
        return sel[0]

def get_single_selected_region(view : sublime.View) -> Union[sublime.Region, None]:
    """
    Gets the single selected region.

    :param view: The applicable view
    :raises RuntimeError: Raised if mutiple regions are selected
    """

    if is_multiple_regions_selected(view):
        raise RuntimeError("Multiple regions selected!")

    return get_first_selected_region(view)

def select_and_zoom_to_region(view   : sublime.View,
                              region : sublime.Region) -> None:
    """
    Selects a region and moves view to its contents.

    :param view:    The applicable view
    :param region:  The region to select
    """

    sel = view.sel()

    # NOTE: There is a bug is Sublime build 4192 that selection is not updated unless the screen
    # updates. Thus if you are already centered around the word you want to select, the selection
    # won't update (because show_at_center will not cause the view to update).
    # This circumvents that
    row = view.rowcol(sel[0].begin())[0]
    view.run_command("goto_line", {"line": row} )

    sel.clear()
    sel.add(region)
    view.show_at_center(sel[0])

def reverse_region(region : sublime.Region) -> sublime.Region:
    """
    Revert a region (moving the caret if it is a selection).

    :param region: The region to revert
    """

    return sublime.Region(region.end(), region.begin())
