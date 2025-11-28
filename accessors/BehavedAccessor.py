import asyncio
import random

import aiohttp

from accessors.Accessor import Accessor


class BehavedAccessor(Accessor):
    DEFAULT_HEADERS = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-CA,en-US;q=0.9,en;q=0.8,zh-CN;q=0.7,zh-TW;q=0.6,zh;q=0.5",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "DNT": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0",
        "sec-ch-ua": '"Chromium";v="142", "Microsoft Edge";v="142", "Not_A Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
    }

    def __init__(
        self,
        headers: dict[str, str] = None,
        max_concurrent: int = 20,
        max_retries: int = 5,
        base_delay: float = 1.0,
        timeout: float = 60.0,
    ):
        if headers is None:
            headers = self.DEFAULT_HEADERS
        self.headers = headers
        self.max_concurrent = max_concurrent
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.timeout = timeout
        self.session = None
        self.semaphore = None

    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        self.session = aiohttp.ClientSession(headers=self.headers, timeout=timeout)
        self.semaphore = asyncio.Semaphore(self.max_concurrent)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def get(self, url: str):
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(headers=self.headers, timeout=timeout)
        if not self.semaphore:
            self.semaphore = asyncio.Semaphore(self.max_concurrent)

        return _RateLimitedRequest(
            semaphore=self.semaphore,
            session=self.session,
            url=url,
            max_retries=self.max_retries,
            base_delay=self.base_delay,
        )


class _RateLimitedRequest:
    """Wraps an aiohttp request with rate limiting and retry logic."""

    RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
    RETRYABLE_EXCEPTIONS = (
        aiohttp.ClientError,
        asyncio.TimeoutError,
        TimeoutError,
        OSError,
    )

    def __init__(
        self,
        semaphore: asyncio.Semaphore,
        session: aiohttp.ClientSession,
        url: str,
        max_retries: int,
        base_delay: float,
    ):
        self.semaphore = semaphore
        self.session = session
        self.url = url
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.response = None

    async def __aenter__(self):
        await self.semaphore.acquire()
        try:
            self.response = await self._request_with_retry()
            return self.response
        except Exception:
            self.semaphore.release()
            raise

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if self.response:
                self.response.release()
        finally:
            self.semaphore.release()

    async def _request_with_retry(self) -> aiohttp.ClientResponse:
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                response = await self.session.get(self.url)

                if response.status not in self.RETRYABLE_STATUS_CODES:
                    return response

                response.release()
                last_exception = aiohttp.ClientResponseError(
                    response.request_info,
                    response.history,
                    status=response.status,
                    message=f"Retryable status code: {response.status}",
                )
            except self.RETRYABLE_EXCEPTIONS as e:
                last_exception = e

            if attempt < self.max_retries:
                delay = self._calculate_delay(attempt)
                print(f"Retry {attempt + 1}/{self.max_retries} for {self.url} after {delay:.2f}s")
                await asyncio.sleep(delay)

        raise last_exception

    def _calculate_delay(self, attempt: int) -> float:
        """Exponential backoff with jitter."""
        delay = self.base_delay * (2 ** attempt)
        jitter = random.uniform(0, delay * 0.1)
        return delay + jitter
