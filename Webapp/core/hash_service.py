import hashlib


class HashService:

    @staticmethod
    def generate_sha256(file):
        sha256 = hashlib.sha256()

        for chunk in file.chunks():
            sha256.update(chunk)

        # 🔥 IMPORTANT: Reset pointer after reading
        file.seek(0)

        return sha256.hexdigest()

    @staticmethod
    def verify_hash(file, stored_hash):
        """
        Verify integrity of file by comparing
        newly generated hash with stored hash.
        """
        new_hash = HashService.generate_sha256(file)
        return new_hash == stored_hash
