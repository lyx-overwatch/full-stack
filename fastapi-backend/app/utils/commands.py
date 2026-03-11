import click
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import os
import base64

# 注意：在 FastAPI 中你需要根据你的 ORM 配置重新导入正确的 DB session 和 User 模型
# from app.models.user import User
# from app.database import get_db

@click.group()
def cli():
    """FastAPI 项目的自定义命令行工具"""
    pass

@cli.command("insert-test-users") # name of our command
@click.argument("count") # argument of out command
def insert_test_users(count):
    """
    Run from the command line by typing: python app/utils/commands.py insert-test-users 5
    """
    print("Creating test users")
    # 注意：此处需要按 FastAPI 提供数据库连接的方式进行替换 (例如 SQLAlchemy session)
    # db = next(get_db())
    for x in range(1, int(count) + 1):
        # user = User(...)
        # db.add(user)
        # db.commit()
        print(f"User test_user{x}@test.com created.")

    print("All test users created")

@cli.command("generate-keys")
def generate_keys():
    """
    Generate RSA keys and print them for .env file
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')


    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')

    with open(".env", "a") as env_file:
        env_file.write(f"RSA_PRIVATE_KEY='{private_pem.strip()}'\n")
        env_file.write(f"RSA_PUBLIC_KEY='{public_pem.strip()}'\n")

    print("密钥已编码并保存到 .env 文件")
    

if __name__ == "__main__":
    cli()
