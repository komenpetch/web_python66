from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()
hashed_password = password_hash.hash("1234")
print(hashed_password)
print(password_hash.verify("1234", hashed_password))  # True