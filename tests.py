from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)


pas1 = get_password_hash('1111')
pas2 = get_password_hash('1111')

print('1=2', pas1 == pas2)

print(verify_password('11111', pas1))