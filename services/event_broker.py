import asyncio
import json
from collections.abc import AsyncGenerator


class EventBroker:
    """In-memory pub/sub 이벤트 브로커. Webhook → SSE 브릿지."""

    def __init__(self):
        self._subscribers: dict[int, asyncio.Queue] = {}
        self._next_id = 0

    async def subscribe(self) -> AsyncGenerator[str, None]:
        """SSE 소비자용. 이벤트를 SSE 프레임으로 yield한다."""
        sub_id = self._next_id
        self._next_id += 1
        queue: asyncio.Queue = asyncio.Queue()
        self._subscribers[sub_id] = queue
        try:
            while True:
                event = await queue.get()
                yield f"event: crawl\ndata: {json.dumps(event, ensure_ascii=False)}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            self._subscribers.pop(sub_id, None)

    async def publish(self, event: dict) -> None:
        """Webhook에서 호출. 모든 subscriber에게 이벤트를 전달한다."""
        for queue in self._subscribers.values():
            await queue.put(event)


event_broker = EventBroker()
