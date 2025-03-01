import json
from typing import Optional
from app.utils.logger import get_logger
from app.config import service_name

logger = get_logger(service_name)


def find_end_of_json(s: str, start_idx: int) -> int:
    """
    Finds the index where the JSON object ends.
    """
    brace_count = 0
    in_string = False
    escape = False
    for i in range(start_idx, len(s)):
        char = s[i]
        if char == '"' and not escape:
            in_string = not in_string
        if not in_string:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    return i + 1
        escape = (char == '\\' and not escape)
    return -1


def extract_product_json(html: str) -> Optional[dict]:
    """
    Extracts the JSON object assigned to window.productJSON from the HTML.
    """
    marker = "window.productJSON ="
    idx = html.find(marker)
    if idx == -1:
        logger.debug("'window.productJSON' not found in HTML.")
        return None
    start_idx = html.find("{", idx)
    if start_idx == -1:
        logger.debug("JSON start not found.")
        return None
    end_idx = find_end_of_json(html, start_idx)
    if end_idx == -1:
        logger.debug("JSON end not found.")
        return None
    json_str = html[start_idx:end_idx]
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.debug("Error decoding JSON: %s", e)
        return None
