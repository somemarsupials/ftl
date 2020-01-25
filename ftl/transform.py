import multiprocessing as mp

from job import CompletedJob


def create_worker(task, verbose):
    def worker(job_queue, target_queue):
        for job in iter(job_queue.get, "STOP"):
            try:
                result = task(job.content)
                target_queue.put(CompletedJob(job.url, result))
                target_queue.task_done()

                if verbose or (job.id % 100 == 0 and job.id > 0):
                    print("TRANSFORM #{} complete".format(job.id))
            except Exception as error:
                print("TRANSFORM #{} failed |".format(job.id), error)

    return worker


class Transform:
    def __init__(self, job_queue, target_queue, cores=4, verbose=False):
        self.cores = cores
        self.job_queue = job_queue
        self.target_queue = target_queue
        self.verbose = verbose

    def begin(self, transform_task):
        processes = [
            mp.Process(
                target=create_worker(transform_task, self.verbose),
                args=(self.job_queue, self.target_queue)
            )
            for _ in range(self.cores)
        ]
    
        if self.verbose:
            print("Starting transform workers...")

        for process in processes:
            process.start()

        return lambda: self.block_until_complete(processes)

    def block_until_complete(self, processes):
        if self.verbose:
            print("Terminating transform workers...")

        for _ in processes:
            self.job_queue.put("STOP")

        print("Transform processes complete")
