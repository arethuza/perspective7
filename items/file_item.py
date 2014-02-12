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
        return result

    @Action("get", "reader")
    def get_file(self, worker):
        return self.get_file_version(worker, self.file_version)

    @Action("get", "reader", version="")
    def get_file_version(self, worker, version):
        version = int(version)
        file_length = worker.get_file_length(version)
        def write():
            for block_number, _, _, _ in worker.list_file_blocks(version):
                yield worker.get_block_data(version, block_number)
        return self.name, file_length, write

    @Action("get", "reader", versions="true")
    def list_versions(self, worker):
        return worker.list_file_versions()


