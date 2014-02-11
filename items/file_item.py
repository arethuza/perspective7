from items.item import Item
from actionable import WithActions, Action

@WithActions
class FileItem(Item):

    @Action("put", "editor", _file_data="")
    def put_file(self, worker, _file_data):
        return self.put_file_previous(worker, None, _file_data)

    @Action("put", "editor", previous="", _file_data="")
    def put_file_previous(self, worker, previous, _file_data):
        result = worker.write_file_data(previous, _file_data)
        self.set_field("file_version", result["version"])
        self.set_field("length", result["length"])
        return result

    @Action("get", "reader")
    def get_file(self, worker):
        def write():
            for block_number, _, _ in worker.list_file_blocks(self.file_version):
                yield worker.get_block_data(self.file_version, block_number)
        return self.name, self.length, write



