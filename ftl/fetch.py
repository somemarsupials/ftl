from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from tornado.ioloop import IOLoop
from tornado.queues import Queue

from .job import FetchJob, TransformJob


async def make_request(url):
    return await AsyncHTTPClient().fetch(url)


async def create_worker(index, job_queue, target_queue, verbose):
    async for job in job_queue:
        if not job:
            return

        try:
            url, job_id = job.url, job.id
            response = await make_request(url)
            content = response.body.decode(errors="ignore")

            transform_job = TransformJob(job_id, url, content)
            target_queue.put(transform_job)

            if verbose or (job.id % 100 == 0 and job.id > 0):
                print("#{} FETCH complete".format(job.id))

        except Exception as error:
            if job.can_retry():
                if verbose:
                    print("#{} FETCH retrying".format(job_id))
                await job_queue.put(job.retry())
            else:
                print("#{} FETCH aborted |".format(job_id), error)
        finally:
            job_queue.task_done()


def urls_to_jobs(urls):
    return [FetchJob(index, url) for index, url in enumerate(urls)]


class Fetch:
    def __init__(self, target_queue, concurrency=500, verbose=False):
        self.concurrency = concurrency
        self.job_queue = Queue()
        self.target_queue = target_queue
        self.verbose = verbose

    async def _queue_jobs(self, jobs):
        for job in jobs:
            await self.job_queue.put(job)

    def _create_workers(self):
        workers = [
            create_worker(i, self.job_queue, self.target_queue, self.verbose)
            for i in range(self.concurrency)
        ]

        return gen.multi(workers)

    async def _terminate_jobs(self):
        for _ in range(self.concurrency):
            await self.job_queue.put(None)

    async def begin(self, urls):
        await self._queue_jobs(urls_to_jobs(urls))
        workers = self._create_workers()

        if self.verbose:
            print("Starting fetch workers...")

        return self.block_until_complete(workers)

    async def block_until_complete(self, workers):
        if self.verbose:
            print("Awaiting fetch queue completion...")

        await self.job_queue.join()

        if self.verbose:
            print("Terminating fetch workers...")

        await self._terminate_jobs()
        await workers

        print("Fetch processing completed")
