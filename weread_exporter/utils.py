import asyncio
import hashlib
import logging
import random
from typing import Any, Tuple, Union, cast

import aiohttp


class ChromeNotInstalledError(Exception):
    pass


class LoginRequiredError(RuntimeError):
    pass


class LoadChapterFailedError(RuntimeError):
    pass


class InvalidUserError(RuntimeError):
    pass


def generate_user_agent() -> str:
    user_agent_tmpl = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/%d.0.0.0 Safari/537.36"
    return user_agent_tmpl % random.randint(90, 130)


async def fetch(
    url: str,
    method: str = "GET",
    headers: Any = None,
    data: Any = None,
    respond_with_headers: bool = False,
) -> Union[bytes, Tuple[int, Any, bytes]]:
    """Fetch URL, optionally with response headers."""
    request_headers = headers or {}
    request_headers.pop("sec-ch-ua", None)
    request_headers.pop("sec-ch-ua-platform", None)
    async with aiohttp.ClientSession() as session:
        http_method = getattr(session, method.lower())
        request_data: Any = data
        if data and not isinstance(data, bytes):
            request_data = data.encode("utf-8")

        for attempt in range(3):
            try:
                async with http_method(url, headers=request_headers, data=request_data) as response:
                    result: bytes = await response.read()
                    if respond_with_headers:
                        return response.status, response.headers, result
                    else:
                        return result
            except (aiohttp.ClientError, asyncio.TimeoutError, RuntimeError) as e:
                logging.warning(
                    "Failed to fetch URL %s (attempt %d/3): %s"
                    % (url, attempt + 1, str(e))
                )
                if attempt == 2:
                    raise RuntimeError(f"Fetch url {url} failed after 3 attempts")
        else:
            raise RuntimeError(f"Fetch url {url} failed")


async def get_book_list(book_list_id: str):
    book_list = []
    url = "https://weread.qq.com/misc/booklist/" + book_list_id
    result = await fetch(url)
    html: str = cast(bytes, result).decode()
    pos = html.find("window.__NUXT__")
    if pos <= 0:
        raise RuntimeError(f"Unexpected html for book list {book_list_id}")
    pos = html.find("bookEntities:", pos)
    while True:
        if book_list:
            pos = html.find('},"', pos)
            if pos < 0:
                break
        pos = html.find('"', pos)
        pos1 = html.find('"', pos + 1)
        book_id = html[pos + 1 : pos1]
        pos = html.find("title:", pos)
        pos = html.find('"', pos)
        pos1 = html.find('"', pos + 1)
        title = html[pos + 1 : pos1]
        book_list.append({"id": wr_hash(book_id), "title": title})
    return book_list


async def get_book_list_full(book_list_id: str):
    """Get all books in a booklist with original and hashed IDs."""
    results = []
    url = "https://weread.qq.com/misc/booklist/" + book_list_id
    result = await fetch(url)
    html: str = cast(bytes, result).decode()
    pos = html.find("window.__NUXT__")
    if pos <= 0:
        raise RuntimeError(f"Unexpected html for book list {book_list_id}")
    while True:
        if results:
            pos = html.find('},"', pos)
            if pos < 0:
                break
        pos = html.find('"', pos)
        pos1 = html.find('"', pos + 1)
        original_id = html[pos + 1 : pos1]
        pos = html.find("title:", pos)
        pos = html.find('"', pos)
        pos1 = html.find('"', pos + 1)
        title = html[pos + 1 : pos1]
        results.append(
            {"original_id": original_id, "hashed_id": wr_hash(original_id), "title": title}
        )
    return results


def format_filename(filename):
    for c in ("/", "\\", ":"):
        filename = filename.replace(c, "%%%.2x" % ord(c))
    return filename


def md5(s):
    if not isinstance(s, bytes):
        s = s.encode()
    return hashlib.md5(s).hexdigest()


def wr_hash(s):
    hash = md5(s)
    result = hash[:3] + "32" + hash[-2:]
    _0x22edbf = []
    for i in range(0, len(s), 9):
        _0x22edbf.append("%x" % int(s[i : min(i + 9, len(s))]))

    for i, it in enumerate(_0x22edbf):
        _0x116344 = "%x" % len(it)
        if len(_0x116344) == 1:
            _0x116344 = "0" + _0x116344
        result += _0x116344 + it
        if i < len(_0x22edbf) - 1:
            result += "g"

    if len(result) < 20:
        result += hash[: 20 - len(result)]
    result += hashlib.md5(result.encode()).hexdigest()[:3]
    return result


def save_to_png(img_path, png_path):
    from PIL import Image

    img = Image.open(img_path)
    img.save(png_path)
