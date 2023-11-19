import hashlib

methodist = "methodist"
counselor = "counselor"
master = "imaking"

master_hash = hashlib.sha256(master.encode())
methodist_hash = hashlib.sha256(methodist.encode())
counselor_hash = hashlib.sha256(counselor.encode())

master_pass = master_hash.hexdigest()
methodist_pass = methodist_hash.hexdigest()
counselor_pass = counselor_hash.hexdigest()
