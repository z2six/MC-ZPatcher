# CurseForgeAPI.py
import requests
import hashlib

class CurseForgeSync:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.curseforge.com/v1"
        self.headers = {
            "x-api-key": self.api_key
        }

    def query_mod_by_hash(self, file_path):
        """Queries CurseForge by Game ID and SHA-1 file hash."""
        sha1_hash = self.calculate_sha1(file_path)
        if not sha1_hash:
            print(f"[ERROR] Failed to calculate SHA-1 for file: {file_path}")
            return None

        # Send request to CurseForge to find a mod with the hash
        response = requests.get(
            f"{self.base_url}/mods/files/hash/{sha1_hash}",
            headers=self.headers
        )

        if response.status_code == 200:
            result = response.json().get("data")
            if result:
                match = {
                    "name": result["modName"],
                    "curseforge_id": result["modId"],
                    "curseforge_url": f"https://www.curseforge.com/minecraft/mc-mods/{result['modSlug']}"
                }
                print(f"[SUCCESS] SHA-1 hash match found: {match['name']} - URL: {match['curseforge_url']}")
                return match
            else:
                print(f"[INFO] No match found for SHA-1 hash: {sha1_hash}")
        else:
            print(f"[ERROR] Hash query failed with status {response.status_code}: {response.text}")

        return None

    def query_mod_by_filename(self, mod_name, file_name):
        """Queries CurseForge by Game ID and mod name, then filters results to find an exact file name match."""
        params = {
            "gameId": 432,  # Minecraft game ID on CurseForge
            "searchFilter": mod_name,
            "pageSize": 50  # Maximum allowed page size
        }
        index = 0  # Starting index for pagination
        max_pages = 3  # Limit for pagination (fetch up to 3 pages)

        while index < max_pages * params["pageSize"]:
            params["index"] = index
            response = requests.get(
                f"{self.base_url}/mods/search",
                headers=self.headers,
                params=params
            )

            if response.status_code == 200:
                results = response.json().get("data", [])
                if not results:
                    print(f"[INFO] No more results found after {index // params['pageSize']} page(s).")
                    break

                print(f"[INFO] Found {len(results)} mod(s) on page {index // params['pageSize'] + 1} for mod name '{mod_name}'.")

                # Log each found mod with a link to its CurseForge page
                for result in results:
                    mod_url = f"https://www.curseforge.com/minecraft/mc-mods/{result['slug']}"
                    print(f"[INFO] Mod found: {result['name']} - URL: {mod_url}")

                # Check each mod's files for an exact filename match
                for result in results:
                    mod_url = f"https://www.curseforge.com/minecraft/mc-mods/{result['slug']}"
                    print(f"[INFO] Checking files for mod '{result['name']}' ({mod_url}) for exact filename match.")

                    mod_files_response = requests.get(
                        f"{self.base_url}/mods/{result['id']}/files",
                        headers=self.headers
                    )

                    if mod_files_response.status_code == 200:
                        mod_files = mod_files_response.json().get("data", [])
                        for file in mod_files:
                            if file["fileName"] == file_name:
                                exact_match = {
                                    "name": result["name"],
                                    "curseforge_id": result["id"],
                                    "curseforge_url": mod_url
                                }
                                print(f"[SUCCESS] Exact filename match found: {exact_match['name']} - URL: {exact_match['curseforge_url']}")
                                return exact_match
                        print(f"[INFO] No exact filename match found in files for '{result['name']}'.")

                # Move to the next page of results
                index += params["pageSize"]

            else:
                print(f"[ERROR] Filename query failed with status {response.status_code}: {response.text}")
                break

        print(f"[INFO] No exact match found for filename: {file_name} within mod results for: {mod_name}")
        return None

    def calculate_sha1(self, file_path):
        """Calculate the SHA-1 hash of a given file."""
        sha1 = hashlib.sha1()
        try:
            with open(file_path, "rb") as f:
                while chunk := f.read(8192):
                    sha1.update(chunk)
            sha1_hex = sha1.hexdigest()
            print(f"[INFO] Generated SHA-1 hash for {file_path}: {sha1_hex}")
            return sha1_hex
        except Exception as e:
            print(f"[ERROR] Failed to read file {file_path} for hashing: {e}")
            return None
