import hashlib

kid = "student"
counsellor = "counsellor"
methodist = "methodist"
master = "imaking"

kid_hash = hashlib.sha256(kid.encode())
counsellor_hash = hashlib.sha256(counsellor.encode())
methodist_hash = hashlib.sha256(methodist.encode())
master_hash = hashlib.sha256(master.encode())

kid_pass = kid_hash.hexdigest()
counsellor_pass = counsellor_hash.hexdigest()
methodist_pass = methodist_hash.hexdigest()
master_pass = master_hash.hexdigest()
