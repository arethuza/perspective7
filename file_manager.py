import dbgateway
import hashlib
from worker import ServiceException
import math


BLOCK_LENGTH=int(math.pow(2, 22))

class FileManager():

    def __init__(self, locator):
        self.locator = locator

    def create_initial_file_version(self, item_id, user_handle):
        dbgw = dbgateway.DbGateway(self.locator)
        dbgw.create_file_version(item_id, None, user_handle.item_id)

    def create_file_version(self, item_id, previous_version, user_handle):
        dbgw = dbgateway.DbGateway(self.locator)
        if previous_version and dbgw.get_file_version(item_id, previous_version)[0] is None:
            raise ServiceException(409, "Unknown previous version: {0}".format(previous_version))
        return dbgw.create_file_version(item_id, previous_version, user_handle.item_id)

    def write_file_data(self, item_id, previous_version, file_data, user_handle):
        dbgw = dbgateway.DbGateway(self.locator)
        file_version = self.create_file_version(item_id, previous_version, user_handle)
        blocks = [file_data[i:i+BLOCK_LENGTH] for i in range(0, len(file_data), BLOCK_LENGTH)]
        block_hashes = []
        for block_number, block_data in enumerate(blocks):
            block_hash = _get_hash(block_data)
            block_hashes.append(block_hash)
            dbgw.create_file_block(item_id, file_version, block_number, block_hash, block_data)
        file_hash = _get_hash(block_hashes)
        file_length = len(file_data)
        dbgw.set_file_version_length_hash(item_id, file_version, file_length, file_hash)
        return {
            "hash": file_hash,
            "length": file_length,
            "file_version": file_version
        }

    def list_blocks(self, item_id, file_version):
        dbgw = dbgateway.DbGateway(self.locator)
        return dbgw.list_file_blocks(item_id, file_version)

    def get_block_data(self, item_id, file_version, block_number):
        dbgw = dbgateway.DbGateway(self.locator)
        return dbgw.get_file_block_data(item_id, file_version, block_number)

    def write_file_block(self, item_id, file_version, block_number, block_data):
        dbgw = dbgateway.DbGateway(self.locator)
        block_hash = _get_hash(block_data)
        dbgw.create_file_block(item_id, file_version, block_number, block_hash, block_data)

    def link_previous_blocks(self, item_id, file_version):
        dbgw = dbgateway.DbGateway(self.locator)
        file_version_id, _, _, previous_version = dbgw.get_file_version(item_id, file_version)
        previous_version_id, _, _, _ = dbgw.get_file_version(item_id, previous_version)


    def finalize_version(self, item_id, file_version):
        file_length = 0
        blocks = self.list_blocks(item_id, file_version)
        block_hashes = []
        for _, block_length, block_hash, _ in blocks:
            file_length += block_length
            block_hashes.append(block_hash)
        file_hash = _get_hash(block_hashes)
        dbgw = dbgateway.DbGateway(self.locator)
        dbgw.set_file_version_length_hash(item_id, file_version, file_length, file_hash)

    def get_version_length(self, item_id, file_version):
        dbgw = dbgateway.DbGateway(self.locator)
        length, hash, _ = dbgw.get_file_version(item_id, file_version)
        return length if hash else None

    def list_versions(self, item_id):
        dbgw = dbgateway.DbGateway(self.locator)
        result = []
        for file_version, previous_version, length, hash, created_at, created_by in dbgw.list_file_versions(item_id):
            result.append({
                "file_version": file_version,
                "previous": previous_version,
                "length": length,
                "hash": hash,
                "created_at": created_at.isoformat(),
                "created_by": created_by
            })
        return result

def _get_hash(data):
    if type(data) is list:
        data = "".join([_get_hash(x.encode("utf-8")) for x in data])
    message = hashlib.sha1()
    message.update(data if type(data) is not str else data.encode("utf-8"))
    return message.hexdigest()



