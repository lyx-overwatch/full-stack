# 测试 passlib 和 bcrypt 支持
try:
    import bcrypt
    # bcrypt.__about__ = bcrypt

    def get_password_hash(password: str) -> bytes:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def verify_password(plain_password: str, hashed_password: bytes) -> bool:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)
    
    test_password = "test_password"

    hashed = get_password_hash(test_password)
    print(f"Hashed password: {hashed}")

    if verify_password(test_password, hashed):
        print("✅ Password verification successful")


except ImportError as e:
    print(f"❌ 导入失败: {e}")
except Exception as e:
    print(f"❌ 其他错误: {e}")