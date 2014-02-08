import dbgateway
import hashlib
from worker import ServiceException


BLOCK_LENGTH=4000000

class FileManager():


    def __init__(self, locator):
        self.locator = locator

    def create_file_version(self, item_id, previous_version, user_handle):
        dbgw = dbgateway.DbGateway(self.locator)
        if previous_version and dbgw.get_file_version(item_id, previous_version) is None:
            raise ServiceException(409, "Unknown previous version: {0}".format(previous_version))
        return dbgw.create_file_version(item_id, previous_version, user_handle.item_id)

    def write_file_data(self, item_id, previous_version, file_data, user_handle):
        dbgw = dbgateway.DbGateway(self.locator)
        file_version_id, file_version = self.create_file_version(item_id, previous_version, user_handle)
        blocks = [file_data[i:i+BLOCK_LENGTH] for i in range(0, len(file_data), BLOCK_LENGTH)]
        block_hashes = []
        for block_number, block_data in enumerate(blocks):
            block_hash = _get_hash(block_data)
            block_hashes.append(block_hash)
            dbgw.create_file_block(file_version_id, block_number, block_hash, block_data)
        file_hash = _get_hash(block_hashes)
        return {
            "hash": file_hash,
            "length": len(file_data),
            "version": file_version
        }


def _get_hash(data):
    if type(data) is list:
        data = "".join([_get_hash(x.encode("utf-8")) for x in data])
    message = hashlib.sha1()
    message.update(data if type(data) is not str else data.encode("utf-8"))
    return message.hexdigest()



