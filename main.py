
# NO DEPENDENCIES (except Python ofc)
import os, json

if __name__ == "__main__":
    print("")
    print("ArchiSteamFarm 2FA converter to Steam Desktop Authenticator")
    print("")

    ASFPath = str(input("Enter full ASF path: ")).removesuffix("\\config\\").removesuffix("\\config") + "\\config\\"
    SDAPath = str(input("Enter full SDA path: ")).removesuffix("\\maFiles\\").removesuffix("\\maFiles") + "\\maFiles\\"

    maFilesData = {}

    for filename in os.listdir(ASFPath):
        if filename.endswith(".maFile.NEW") or filename.endswith(".db"):
            
            name = filename.removesuffix(".maFile.NEW").removesuffix(".db") + ".maFile"
            sda_name = None
            is_weak = filename.endswith(".db") # has only indentity_secret, shared_secred
            
            with open(ASFPath + "\\" + filename, "r", encoding="utf-8") as file:
                data: dict = json.load(file)
            
            maFile = data.get("_MobileAuthenticator") if is_weak else data
            
            if not maFile:
                continue
            
            if is_weak:
                maFile["Session"] = {
                    "BackingAccessToken": data.get("BackingAccessToken"),
                    "BackingRefreshToken": data.get("BackingRefreshToken")
                }
            else:
                steam_id = maFile.get("Session", {}).get("SteamID")
                if steam_id:
                    sda_name = str(steam_id) + ".maFile"
                    
            if (name not in maFilesData) or (is_weak is False):
                maFilesData[name] = {
                    "is_weak": is_weak,
                    "sda_name": sda_name, # preferred naming for sda
                    "maFile": maFile
                }

    SDAMaFiles = os.listdir(SDAPath)
    SDAManifest = SDAPath + "manifest.json"
    atleastoneneedsmanualconvert = False

    with open(SDAManifest, "r", encoding="utf-8") as file:
        manifest_data = json.load(file)

    for name, data in maFilesData.items():
        if name in SDAMaFiles or data.get("sda_name", "") in SDAMaFiles:
            print("[SKIP] %s already in SDA..." % name)
            continue
        
        if data.get("is_weak"):
            if not ";" in name:
                print("[WEAK] %s cannot be converted to SDA's maFile..." % name)
                continue

            weak_data = {
                "account_name": name.split(";")[0],
                "shared_secret": data["maFile"].get("shared_secret"),
                "identity_secret": data["maFile"].get("identity_secret"),
            }

            data["maFile"].update(weak_data)

        
        with open(SDAPath + (data["sda_name"] or name), "w", encoding="utf-8") as file:
            json.dump(data["maFile"], file, indent=2)
            print("[DONE] %s %s to SDA's maFile..." % ("NEEDS MANUAL IMPORT" if data["sda_name"] is None else "Converted", name))
        
        if not data["sda_name"]:
            atleastoneneedsmanualconvert = True
            continue
        
        manifest_data["entries"].append({
            "encryption_iv": None,
            "encryption_salt": None,
            "filename": data["sda_name"],
            "steamid": int(data["sda_name"].removesuffix(".maFile"))
        })

    if atleastoneneedsmanualconvert:
        print("")
        print("All .maFiles with non standard names for SDA must be manually imported...")
        
    with open(SDAManifest, "w", encoding="utf-8") as file:
        json.dump(manifest_data, file, indent=2)
