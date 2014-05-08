from items.item import Item
from actionable import WithActions, Action
from worker import ServiceException
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
        file_version, file_length, file_hash = worker.write_file_data(previous, _file_data)
        self.set_field("file_version", file_version)
        result = dict()
        result["file_version"] = file_version
        result["file_length"] = file_length
        result["file_hash"] = file_hash
        return result

    @Action("put", "editor", file_version="", block_number="", _file_data="")
    def put_file_block(self, worker, file_version, block_number, _file_data):
        worker.write_block_data(file_version, block_number, _file_data, False)

    @Action("put", "editor", file_version="", block_number="", last_block="", _file_data="")
    def put_file_block_completed(self, worker, file_version, block_number, last_block, _file_data):
        if len(_file_data) > 0:
            worker.write_block_data(file_version, block_number, _file_data, last_block)
        if last_block:
            worker.finalize_file_version(file_version)

    @Action("get", "reader")
    def get_file(self, worker) -> "binary":
        """ Return the current version of a file """
        return self.get_file_version(worker, self.file_version)

    @Action("get", "reader", view="meta")
    def get_file_meta(self, worker):
        result = self.get_meta(worker)
        result["file_version"] = self.file_version
        return result

    @Action("get", "reader", file_version="")
    def get_file_version(self, worker,
                         file_version: "Version of the file to return") -> "binary":
        """ Return a specified version of a file """
        file_version = int(file_version)
        file_length = worker.get_file_length(file_version)
        if file_length is None:
            raise ServiceException(404, "Bad file_version: {}".format(file_version))
        def get_blocks():
            for block_number in [a[0] for a in worker.list_file_blocks(file_version)]:
                yield worker.get_block_data(file_version, block_number)
        return FileResponse(self.name, file_length, get_blocks)

    @Action("get", "reader", versions="true")
    def list_versions(self, worker):
        return worker.list_file_versions()

    @Action("post", "editor", previous="")
    def post_file_version(self, worker, previous):
        result = dict()
        result["file_version"] = worker.create_file_version(previous)
        return result

