class Worker():

    def __init__(self, processor, item, worker_handle):
        self.processor = processor
        self.item = item
        self.worker_handle = worker_handle