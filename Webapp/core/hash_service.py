import hashlib


class HashService:

    @staticmethod
    def generate_sha256(file):
        """
        Generate SHA-256 hash for an uploaded file.
        """
        sha256 = hashlib.sha256()

        for chunk in file.chunks():
            sha256.update(chunk)

        return sha256.hexdigest()

    @staticmethod
    def verify_hash(file, stored_hash):
        """
        Verify integrity of file by comparing
        newly generated hash with stored hash.
        """
        new_hash = HashService.generate_sha256(file)
        return new_hash == stored_hash
