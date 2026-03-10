## alembic 配置

```bash
# 初始化
alembic init migrations


# 自动检测模型变化
alembic revision --autogenerate

# 升级到最新版本
alembic upgrade head

# 降级一个版本
alembic downgrade -1

# 查看当前版本
alembic current

# 查看历史记录
alembic history --verbose
```
