class RetriesExceeded(Exception):
    pass


class FailedJob:
    def __init__(self, url, error):
        self.url = url
        self.error = error


class CompletedJob:
    def __init__(self, url, result):
        self.url = url
        self.result = result


class FetchJob:
    def __init__(self, job_id, url, retries=2):
        self.id = job_id
        self.retries = retries
        self.url = url

    def can_retry(self):
        return self.retries > 0

    def retry(self):
        if not self.can_retry():
            raise RetriesExceeded(self.url)

        return FetchJob(self.id, self.url, self.retries - 1)


class TransformJob:
    def __init__(self, job_id, url, content):
        self.content = content
        self.id = job_id
        self.url = url
