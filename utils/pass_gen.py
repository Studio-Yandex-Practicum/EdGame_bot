import hashlib

methodist = "methodist"
counsellor = "counsellor"
master = "imaking"

master_hash = hashlib.sha256(master.encode())
methodist_hash = hashlib.sha256(methodist.encode())
counsellor_hash = hashlib.sha256(counsellor.encode())

master_pass = master_hash.hexdigest()
methodist_pass = methodist_hash.hexdigest()
counsellor_pass = counsellor_hash.hexdigest()
