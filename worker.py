class Worker():

    def __init__(self, processor, item, worker_handle):
        self.processor = processor
        self.item = item
        self.worker_handle = worker_handle

    def find_or_create(self, name, item_type):
        pass

    def move(self, path):
        pass

    def create(self, name, item_type):
        pass

    def execute(self, verb, **kwargs):
        pass