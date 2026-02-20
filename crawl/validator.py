import re

from core.exceptions.crawl import CrawlFailedException

_GARBAGE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(p, re.IGNORECASE)
    for p in [
        r"unusual.?traffic|비정상적인.?트래픽",
        r"captcha|보안문자|자동화된.?요청",
        r"access.?denied|접근.?거부",
        r"403.?forbidden|404.?not.?found|페이지를.?찾을.?수.?없",
        r"로그인이.?필요|login.?required|sign.?in.?to.?continue",
        r"존재하지.?않는.?페이지|삭제된.?게시물",
        r"일시적.?오류|service.?unavailable|503",
    ]
]

_MIN_TEXT_HTML_RATIO = 0.02
_MIN_CONTENT_LENGTH = 50


def validate(html: str, content: str) -> None:
    if len(content) < _MIN_CONTENT_LENGTH:
        raise CrawlFailedException("콘텐츠가 너무 짧습니다.")

    if html and len(html) > 0:
        ratio = len(content) / len(html)
        if ratio < _MIN_TEXT_HTML_RATIO:
            raise CrawlFailedException("텍스트 비율이 너무 낮습니다. (JS 렌더링 실패 가능)")

    for pattern in _GARBAGE_PATTERNS:
        if pattern.search(content):
            msg = f"Garbage 콘텐츠 감지: {pattern.pattern}"
            raise CrawlFailedException(msg)
