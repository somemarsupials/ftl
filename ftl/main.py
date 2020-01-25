import asyncio
import multiprocessing as mp
import queue

from .fetch import Fetch
from .transform import Transform


class FTL:
    def __init__(self, request_concurrency=500, cores=4, verbose=False):
        self.cores = cores
        self.request_concurrency = request_concurrency
        self.verbose = verbose

    def _dequeue_results(self, result_queue):
        results = []

        while not result_queue.empty():
            try:
                results.append(result_queue.get(False))
            except queue.Empty:
                continue

        return results

        
    async def fetch_and_transform(self, urls, transform_task):
        transform_queue = mp.Manager().Queue()        
        result_queue = mp.Manager().Queue()

        fetch = Fetch(
            transform_queue,
            concurrency=self.request_concurrency,
            verbose=self.verbose
        )

        transform = Transform(
            transform_queue,
            result_queue,
            cores=self.cores,
            verbose=self.verbose
        )

        fetch_complete = await fetch.begin(urls)
        transform_complete = transform.begin(transform_task)

        await fetch_complete
        transform_complete()

        return self._dequeue_results(result_queue)


if __name__ == "__main__":
    ftl = FTL(10, 4, True)
    loop = asyncio.get_event_loop()

    urls = ['http://localhost:5000' for _ in range(30)]

    def transformer(content):
        return content[:10]

    results = loop.run_until_complete(ftl.fetch_and_transform(urls, transformer))
    print("Obtained {} results".format(len(results)))
