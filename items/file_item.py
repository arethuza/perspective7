from items.item import Item
from actionable import WithActions, Action
import collections

FileResponse=collections.namedtuple("FileResponse", ["name", "length", "block_yielder"])

@WithActions
class FileItem(Item):

    def __init__(self):
        super(FileItem, self).__init__()
        self.file_version = 0

    @Action("init", "system")
    def init(self, worker):
        worker.create_initial_file_version()

    @Action("put", "editor", _file_data="")
    def put_file(self, worker, _file_data):
        return self.put_file_previous(worker, None, _file_data)

    @Action("put", "editor", previous="", _file_data="")
    def put_file_previous(self, worker, previous, _file_data):
        result = worker.write_file_data(previous, _file_data)
        self.set_field("file_version", result["version"])
        return result

    @Action("put", "editor", version="", block_number="", _file_data="")
    def put_file_block(self, worker, version, block_number, _file_data):
        worker.write_block_data(version, block_number, _file_data)

    @Action("get", "reader")
    def get_file(self, worker):
        return self.get_file_version(worker, self.file_version)

    @Action("get", "reader", view="meta")
    def get_file_meta(self, worker):
        result = self.get_meta(worker)
        result["file_version"] = self.file_version
        return result

    @Action("get", "reader", version="")
    def get_file_version(self, worker, version):
        version = int(version)
        file_length = worker.get_file_length(version)
        def get_blocks():
            for block_number, _, _, _ in worker.list_file_blocks(version):
                yield worker.get_block_data(version, block_number)
        return FileResponse(self.name, file_length, get_blocks)

    @Action("get", "reader", versions="true")
    def list_versions(self, worker):
        return worker.list_file_versions()


