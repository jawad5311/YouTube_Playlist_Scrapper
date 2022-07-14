
import re


def convert_duration_to_seconds(duration: str) -> int:
    """
    Converts video duration to seconds

    Parameters:
        duration: str ->.
            time duration in format '00H00M00S'

    Returns:
        int: total number of seconds
    """

    h = int(re.search('\d+H', duration)[0][:-1]) * 60 ** 2 if re.search('\d+H', duration) else 0
    m = int(re.search('\d+M', duration)[0][:-1]) * 60 if re.search('\d+M', duration) else 0
    s = int(re.search('\d+S', duration)[0][:-1]) if re.search('\d+S', duration) else 0
    return h + m + s

