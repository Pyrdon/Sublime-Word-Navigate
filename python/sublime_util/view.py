"""
Module handling stuff related to the current view
"""

import logging

# Local logger
logger = logging.getLogger(__name__)

from . import selection
import sublime

from typing import Union, Callable

def _get_word_region_near_pt(view       : sublime.View,
                             pt         : int,
                             in_line    : bool,
                             get_point  : Callable[[int, sublime.Region], sublime.Region]) -> sublime.Region:

    """
    Gets the region of the word near a point.

    :param view:        The applicable view
    :param pt:          The point of interest
    :param in_line:     Whether to limit to the current line or not
    :param get_point:   A callable determining how go get to the next point from the current
    """

    # Expand the region to word start, and end
    expanded_region = view.expand_by_class(pt,
        sublime.PointClassification.WORD_START |
        sublime.PointClassification.WORD_END)

    # If we already were at start or end then this region defines the word
    pt_classifier = view.classify(pt)
    if pt_classifier & sublime.PointClassification.WORD_START:
        return sublime.Region(pt, expanded_region.end())
    elif pt_classifier & sublime.PointClassification.WORD_END:
        return sublime.Region(expanded_region.begin(), pt)
    else:
        # We are either somewhere inside out outside a word (not at boundary)
        if view.classify(expanded_region.begin()) & sublime.PointClassification.WORD_START:
            # We are inside a word already
            return expanded_region
        else:
            start_line = view.rowcol(pt)[0]
            # The beginning of the region is at a word end. Use function to find point to continue at
            new_pt = get_point(pt, expanded_region)
            new_line = view.rowcol(new_pt)[0]
            if in_line and start_line != new_line:
                # They were not on the same line
                if new_line < start_line:
                    # We went to the previous line, so start from original point and find word start
                    # forwards instead
                    new_pt = view.find_by_class(pt, True, sublime.PointClassification.WORD_START)
                else:
                    # Go backwards and find word end
                    new_pt = view.find_by_class(pt, False, sublime.PointClassification.WORD_END)

            if view.classify(new_pt) & sublime.PointClassification.WORD_START:
                # We went to word start, word follows after
                return sublime.Region(new_pt,
                    view.find_by_class(new_pt, True, sublime.PointClassification.WORD_END))
            else:
                return sublime.Region(
                    view.find_by_class(new_pt, False, sublime.PointClassification.WORD_START),
                    new_pt)

def get_closest_word_region_from_pt(view      : sublime.View,
                                    pt        : int,
                                    in_line   : bool
                                    ) -> sublime.Region:
    """
    Gets the region of the word closest to a point.

    :param view:        The applicable view
    :param pt:          The point of interest
    :param in_line:     Whether to limit to the current line or not
    """

    def get_closest_point(view, pt, region):
        from_start = pt - region.begin()
        from_end = region.end() - pt
        if from_start <= from_end:
            return region.begin()
        else:
            return region.end()

    return _get_word_region_near_pt(
        view, pt, in_line, lambda pt, r : get_closest_point(view, pt, r))

def get_next_word_region_from_pt(view     : sublime.View,
                                 pt       : int,
                                 in_line  : bool
                                 ) -> sublime.Region:
    """
    Gets the region of the word following a point.

    :param view:        The applicable view
    :param pt:          The point of interest
    :param in_line:     Whether to limit to the current line or not
    """

    return _get_word_region_near_pt(view, pt, in_line, lambda pt, r : r.end())

def get_previous_word_region_from_pt(view     : sublime.View,
                                           pt       : int,
                                           in_line  : bool
                                           ) -> sublime.Region:
    """
    Gets the region of the word ahead of a point.

    :param view:        The applicable view
    :param pt:          The point of interest
    :param in_line:     Whether to limit to the current line or not
    """

    return _get_word_region_near_pt(view, pt, in_line, lambda pt, r : r.begin())

def is_not_part_of_any_word(view   : sublime.View,
                            region : sublime.Region) -> bool:
    """
    Determins if region is not part of any word. E.g.

    Returns True:
    "[    ]", "[ /? ]", "[  \n  ]"

    Returns False:
    "[a  ]", "flagpo[le b]anana"

    :param view:        The applicable view
    :param region:      The region of interest
    """

    start_class = view.classify(region.begin())
    if start_class & sublime.PointClassification.WORD_START and region.empty():
        # If we are exactly at the start of a word, with no characters selected it is not part
        # of any word
        return True

    # Expand start until word start/end
    exp_start_pt = view.find_by_class(
        region.begin(), True, sublime.PointClassification.WORD_START |
                               sublime.PointClassification.WORD_END)

    exp_class = view.classify(exp_start_pt)
    if exp_class & sublime.PointClassification.WORD_START:
        # If the first we find is a start then no word was selected if we also passed the end
        if exp_start_pt >= region.end():
            return True
        else:
            return False
    else:
        # We first passed end, so we must be inside a word
        return False

def is_single_complete_word(view   : sublime.View,
                            region : sublime.Region) -> bool:
    """
    Determins if region is a single complete word. E.g.

    Returns True:
    "[flagpole]", "[banana]"

    Returns False:
    "[ flagpole]", "[flagpole banana]", "f[lagpole]", "[]"

    :param view:        The applicable view
    :param region:      The region of interest
    """

    start_class = view.classify(region.begin())
    if start_class & sublime.PointClassification.WORD_START:
        # The start of word start; expand it to word end and check if it is the region end
        word_end_pt = view.find_by_class(region.begin(), True, sublime.PointClassification.WORD_END)
        return word_end_pt == region.end()

    return False

def is_multiple_complete_words(view   : sublime.View,
                               region : sublime.Region) -> bool:
    """
    Determins if region is a complete set of multiple words, with only non-word characters
    in between. E.g.

    Returns True:
    "[flagpole banana]", "[flagpole     banana]", "[flagpole.banana]"
    "[flagpole\n   banana]"

    Returns False:
    "[ flagpole]", "[flagpole banana]", "f[lagpole]", "[]"

    :param view:        The applicable view
    :param region:      The region of interest
    """

    start_class = view.classify(region.begin())
    if start_class & sublime.PointClassification.WORD_START:
        end_class = view.classify(region.end())
        if end_class & sublime.PointClassification.WORD_END:
            # Region start is word start and region end is word end. Is it a single word?
            return not is_single_complete_word(view, region)
    return False

def is_part_of_multiple_words(view   : sublime.View,
                             region : sublime.Region) -> bool:
    """
    Determins if region is part of multiple words. E.g.

    Returns True:
    "flagpo[le ban]ana", "f[lagpole banana]"

    Returns False:
    "[]", "[flagpole]", "flagpo[le] ", "[flagpole banana]"

    :param view:        The applicable view
    :param region:      The region of interest
    """

    end_point = view.find_by_class(region.begin(), True, sublime.PointClassification.WORD_END)
    start_point = view.find_by_class(end_point, True, sublime.PointClassification.WORD_START)

    return region.end() >= start_point + 1

def get_region_of_closet_same_word(view            : sublime.View,
                                   word_region     : sublime.Region,
                                   forward         : bool,
                                   wrap            : bool,
                                   case_sensitive  : bool
                                   ) -> Union[None, sublime.Region]:
    """
    Gets region of the closest same word.

    :param view:            The applicable view
    :param word_region:     The region indicating the word of interest
    :param forward:         Whether to move forward or backwards
    :param wrap:            Whether to wrap at buffer end or not
    :param case_sensitive:  Whether to match case sensitive or not
    """

    if forward:
        point = word_region.end()
    else:
        point = word_region.begin()

    word = view.substr(word_region)

    flags = 0
    if not forward:
        flags = flags | sublime.REVERSE
    if not case_sensitive:
        flags = flags | sublime.IGNORECASE
    if wrap:
        flags = flags | sublime.WRAP

    regex = r"\b" + (word) + r"\b"

    region = view.find(regex, point, flags)
    if region.empty():
        return None

    rowcol = view.rowcol(region.begin())
    line = rowcol[0] + 1
    col_start  = rowcol[1] + 1
    col_end  = view.rowcol(region.end())[1]

    adj_word = view.substr(region)
    if forward:
        txt = 'Next'
    else:
        txt = 'Previous'
    logger.debug(f"{txt} word is '{adj_word}' ({line}, [{col_start}:{col_end}]).")
    return region

def get_region_of_closest_word_in_line(view            : sublime.View,
                                       point           : int,
                                       forward         : bool,
                                       wrap            : bool
                                       ) -> Union[sublime.Region, None]:
    """
    Gets region of the closest word in line.

    :param view:            The applicable view
    :param point:           The starting point
    :param forward:         Whether to move forward or backwards
    :param wrap:            Whether to wrap at line end or not
    """

    def _get_region_of_closet_word_in_line(view            : sublime.View,
                                           forward         : int,
                                           line            : int,
                                           col             : int
                                           ) -> Union[None, sublime.Region]:
        flags = 0
        if not forward:
            flags = flags | sublime.REVERSE

        regex = r"\b(\w+)\b"

        if forward:
            line_region = sublime.Region(
                view.text_point(line, col),
                view.text_point(line + 1, 0))
        else:
            line_region = sublime.Region(
                view.text_point(line, 0),
                view.text_point(line, col))
        logger.debug(f"Searching region {line_region} ('{view.substr(line_region)}').")

        return view.find_all(regex, flags, within = line_region)

    # Use find-all through this helper function to find to/from this point of the line only
    rowcol = view.rowcol(point)
    line = rowcol[0]
    col = rowcol[1]
    logger.debug(f"Finding closest word in line from {line + 1}:{col}.")
    regions = _get_region_of_closet_word_in_line(
        view, forward, line, col)

    if not regions:
        logger.debug(f"No region found.")
        # Not found
        if not wrap:
            return None

        # Search again in the unsearched part of the line
        if forward:
            new_col = 0
        else:
            rowcol = view.rowcol(view.text_point(line + 1, 0) - 1)
            line = rowcol[0]
            new_col = rowcol[1]

        if col == new_col:
            # If we already searched the whole line there is no need to search again
            return None
        else:
            col = new_col

        regions = _get_region_of_closet_word_in_line(
            view, forward, line, col)

    # Choose the first/last region
    if not regions:
        return None

    if forward:
        region = regions[0]
    else:
        region = selection.reverse_region(regions[-1])

    rowcol = view.rowcol(region.begin())
    line = rowcol[0] + 1
    col_start  = rowcol[1] + 1
    col_end  = view.rowcol(region.end())[1]

    adj_word = view.substr(region)
    if forward:
        txt = 'Next'
    else:
        txt = 'Previous'
    logger.debug(f"{txt} word is '{adj_word}' ({line}, [{col_start}:{col_end}]).")
    return region

