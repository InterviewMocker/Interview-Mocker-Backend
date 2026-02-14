"""
数据库迁移管理脚本
"""
import subprocess
import sys
import os

# 确保在项目根目录运行
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_command(cmd: str) -> bool:
    """运行命令"""
    print(f"执行: {cmd}")
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0


def show_help():
    """显示帮助信息"""
    print("""
数据库迁移管理脚本

用法:
    python scripts/migrate.py <command> [options]

命令:
    upgrade     应用所有待执行的迁移 (升级到最新版本)
    downgrade   回滚最近一次迁移
    current     显示当前数据库版本
    history     显示迁移历史
    generate    生成新的迁移脚本 (需要提供描述信息)
    init        初始化数据库 (不使用迁移，直接创建表)

示例:
    python scripts/migrate.py upgrade
    python scripts/migrate.py generate "add user avatar field"
    python scripts/migrate.py downgrade
""")


def main():
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1]
    
    if command == "upgrade":
        run_command("alembic upgrade head")
    
    elif command == "downgrade":
        run_command("alembic downgrade -1")
    
    elif command == "current":
        run_command("alembic current")
    
    elif command == "history":
        run_command("alembic history")
    
    elif command == "generate":
        if len(sys.argv) < 3:
            print("错误: 请提供迁移描述信息")
            print("示例: python scripts/migrate.py generate \"add user avatar field\"")
            return
        message = sys.argv[2]
        run_command(f'alembic revision --autogenerate -m "{message}"')
    
    elif command == "init":
        print("初始化数据库...")
        # 直接使用 Python 创建表
        import asyncio
        from shared.database import init_shared_db
        asyncio.run(init_shared_db())
        print("数据库初始化完成!")
    
    elif command in ["-h", "--help", "help"]:
        show_help()
    
    else:
        print(f"未知命令: {command}")
        show_help()


if __name__ == "__main__":
    main()
