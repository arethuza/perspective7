from items.item import Item
from actionable import WithActions, Action
from worker import ServiceException
import collections

FileResponse=collections.namedtuple("FileResponse", ["name", "length", "block_yielder"])

@WithActions
class FileItem(Item):

    def __init__(self):
        super(FileItem, self).__init__()

    @Action("_init", "system")
    def init(self, worker):
        worker.create_initial_file_version()

    @Action("put", "editor", _file_data="")
    def put_file(self, worker,
                 _file_data):
        return self.put_file_previous(worker, None, _file_data)

    @Action("put", "editor", previous="", _file_data="")
    def put_file_previous(self, worker,
                          previous: "int: Previous version of the file that new version is based on.",
                          _file_data):
        file_version, file_length, file_hash = worker.write_file_data(previous, _file_data)
        self.props["file_version"] = file_version
        self.props["file_length"] = file_length
        self.props["file_hash"] = file_hash
        self.modified=True
        return self.get_metadata(worker)

    @Action("put", "editor", file_version="", block_number="", _file_data="")
    def put_file_block(self, worker,
                       file_version: "int: Version of the file",
                       block_number: "int: Block number",
                       _file_data):
        worker.write_block_data(file_version, block_number, _file_data, False)

    @Action("put", "editor", file_version="int:", block_number="int:", last_block="bool:", _file_data="")
    def put_file_block_completed(self, worker,
                                 file_version: "int: Version of the file",
                                 block_number: "int: Block number",
                                 last_block: "bool: Is this the last block in the file?",
                                 _file_data):
        result = dict()
        block_hash = None
        if len(_file_data) > 0:
            block_hash = worker.write_block_data(file_version, block_number, _file_data, last_block)
        if last_block:
            file_length, file_hash = worker.finalize_file_version(file_version, block_number)
            self.props["file_length"] = file_length
            self.props["file_hash"] = file_hash
            self.props["file_version"] = file_version
            self.modified = True
            result = self.get_metadata(worker)
            if block_hash:
                result["props"]["block_hash"] = block_hash
        else:
            result["block_hash"] = block_hash
        return result

    @Action("get", "reader")
    def get_file(self, worker) -> "binary":
        """ Return the current version of a file """
        return self.get_file_version(worker, self.props["file_version"])

    @Action("get", "reader", view="meta")
    def get_file_meta(self, worker):
        return self.get(worker)

    @Action("get", "reader", file_version="int:")
    def get_file_version(self, worker,
                         file_version: "Version of the file to return") -> "binary":
        """ Return a specified version of a file """
        file_length = worker.get_file_length(file_version)
        if file_length is None:
            raise ServiceException(404, "Bad file_version: {}".format(file_version))
        def get_blocks():
            for block_number in [block_info["block_number"] for block_info in worker.list_file_blocks(file_version)]:
                yield worker.get_block_data(file_version, block_number)
        return FileResponse(self.name, file_length, get_blocks)

    @Action("get", "reader", versions="true")
    def list_versions(self, worker):
        return worker.list_file_versions()

    @Action("post", "editor", previous_version="int:")
    def post_file_version_length(self, worker,
                                 previous_version):
        """ Create a new file based on a previous version """
        result = dict()
        result["file_version"] = worker.create_file_version(previous_version)
        return result

    @Action("get", "reader", list_blocks="bool:true", file_version="int:")
    def list_blocks(self, worker, file_version):
        return worker.list_file_blocks(file_version)

    @Action("get", "reader", file_version="int:", block_number="int:")
    def get_file_block(self, worker, file_version, block_number):
        block_data = worker.get_block_data(file_version, block_number)
        def get_blocks():
                yield block_data
        return FileResponse(self.name, len(block_data), get_blocks)

    @staticmethod
    def list_property_selector(public_data):
        result = dict()
        props = public_data["props"]
        result["file_version"] = props["file_version"]
        result["file_hash"] = props["file_hash"]
        result["file_length"] = props["file_length"]
        return result

