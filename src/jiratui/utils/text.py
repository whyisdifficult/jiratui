from textual.widgets import TextArea


def char_at_location_matches(textarea: TextArea, row: int, column: int, character: str) -> bool:
    try:
        return textarea.document[row][column] == character
    except IndexError:
        return False
