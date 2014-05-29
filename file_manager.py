import dbgateway
import hashlib
from worker import ServiceException
import math


BLOCK_LENGTH=int(math.pow(2, 22))

class FileManager():

    def create_initial_file_version(self, item_id, user_handle):
        dbgw = dbgateway.get()
        dbgw.create_file_version(item_id, None, user_handle.item_id)

    def create_file_version(self, item_id, previous_version, user_handle):
        dbgw = dbgateway.get()
        if previous_version and dbgw.get_file_version(item_id, previous_version)[0] is None:
            raise ServiceException(409, "Unknown previous version: {0}".format(previous_version))
        file_version = dbgw.create_file_version(item_id, previous_version, user_handle.item_id)
        if previous_version is not None:
            dbgw.copy_file_blocks(item_id, file_version, previous_version)
        return file_version

    def write_file_data(self, item_id, previous_version, file_data, user_handle):
        file_version = self.create_file_version(item_id, previous_version, user_handle)
        blocks = [file_data[i:i+BLOCK_LENGTH] for i in range(0, len(file_data), BLOCK_LENGTH)]
        last_block_number = len(blocks) - 1
        for block_number, block_data in enumerate(blocks):
            self.write_file_block(item_id, file_version, block_number, block_data, block_number == last_block_number)
        file_length, file_hash = self.finalize_version(item_id, file_version)
        return file_version, file_length, file_hash

    def list_blocks(self, item_id, file_version):
        dbgw = dbgateway.get()
        result = []
        for block_number, _, block_length, block_hash, created_at in dbgw.list_file_blocks(item_id, file_version):
            result.append({
                "block_number": block_number,
                "block_length": block_length,
                "block_hash": block_hash,
                "created_at": created_at.isoformat()
            })
        return result

    def get_block_data(self, item_id, file_version, block_number):
        dbgw = dbgateway.get()
        data_file_version = dbgw.get_file_block_data_file_version(item_id, file_version, block_number)
        if data_file_version is not None:
            file_version = data_file_version
        return dbgw.get_file_block_data(item_id, file_version, block_number)

    def write_file_block(self, item_id, file_version, block_number, block_data, last_block):
        if not last_block and len(block_data) < BLOCK_LENGTH:
            raise ServiceException(403, "Block length less than {}".format(BLOCK_LENGTH))
        dbgw = dbgateway.get()
        if self._is_file_version_completed(dbgw, item_id, file_version):
            raise ServiceException(403, "File version is complete")
        block_hash = _get_data_hash(block_data)
        if dbgw.get_file_block_hash(item_id, file_version, block_number):
            # Already a block at this location, so update existing block to overwrite existing data
            dbgw.update_file_block(item_id, file_version, block_number, block_hash, block_data)
        else:
            # Create a new block
            dbgw.create_file_block(item_id, file_version, block_number, block_hash, block_data)
        return block_hash

    def _is_file_version_completed(self, dbgw, item_id, file_version):
        _, hash, _ = dbgw.get_file_version(item_id, file_version)
        return not hash is None

    def finalize_version(self, item_id, file_version):
        dbgw = dbgateway.get()
        file_length = 0
        blocks = dbgw.list_file_blocks(item_id, file_version)
        block_hashes = []
        for _, _, block_length, block_hash, _ in blocks:
            file_length += block_length
            block_hashes.append(block_hash)
        file_hash = _get_blocks_hash(block_hashes)
        dbgw = dbgateway.get()
        dbgw.set_file_version_length_hash(item_id, file_version, file_length, file_hash)
        return file_length, file_hash

    def get_version_length(self, item_id, file_version):
        dbgw = dbgateway.get()
        length, file_hash, _ = dbgw.get_file_version(item_id, file_version)
        return length if file_hash else None

    def list_versions(self, item_id):
        dbgw = dbgateway.get()
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

def _get_data_hash(data):
    message = hashlib.sha256()
    message.update(data)
    return message.hexdigest()

def _get_blocks_hash(block_hashes):
    all_hashes = "".join(block_hashes)
    return _get_data_hash(all_hashes.encode("utf-8"))




