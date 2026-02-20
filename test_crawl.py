"""임시 URL 크롤링 테스트 스크립트

사용법:
    urls 리스트에 URL을 넣고 python test_crawl.py 실행
"""

import time

from db.database import SessionLocal
from services.source import source_service

# 여기에 크롤링할 URL을 넣으세요
urls = []


async def crawl_urls():
    db = SessionLocal()
    total_start = time.perf_counter()
    try:
        for url in urls:
            print(f"\n[크롤링 시작] {url}")
            url_start = time.perf_counter()
            try:
                source = await source_service.create_from_url(url, db)
                elapsed = time.perf_counter() - url_start
                print(f"  [성공] id={source.id} | 소요시간: {elapsed:.2f}s")
                print(f"  제목: {source.title}")
                print(
                    f"  요약: {source.summary[:200]}..."
                    if source.summary and len(source.summary) > 200
                    else f"  요약: {source.summary}"
                )
            except Exception as e:
                elapsed = time.perf_counter() - url_start
                print(f"  [실패] {type(e).__name__}: {getattr(e, 'message', None) or e} | 소요시간: {elapsed:.2f}s")
    finally:
        db.close()
        total_elapsed = time.perf_counter() - total_start
        print(f"\n 크롤링 완료! 총 {len(urls)}개 URL 처리 | 총 소요시간: {total_elapsed:.2f}s")


if __name__ == "__main__":
    import asyncio

    asyncio.run(crawl_urls())
