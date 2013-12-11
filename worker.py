class Worker():

    def __init__(self, processor, item, user_handle):
        self.processor = processor
        self.item = item
        self.user_handle = user_handle

    def find(self, path):
        return self.processor.item_finder.find(path, self.user_handle)

    def create(self, name, type_name):
        type_item = self.processor.item_loader.load_type(type_name)
        json_data = self.processor.item_loader.load_template_json(type_name)
        pass

    def find_or_create(self, path, type_name):
        pass

    def move(self, path):
        pass

    def execute(self, verb, **kwargs):
        pass