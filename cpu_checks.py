# coding:utf-8
import logging
import configparser
import os
from glob import glob
import subprocess

# 获取脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))

# 读取配置文件（与脚本同级）
config = configparser.ConfigParser()
config_path = os.path.join(script_dir, 'config.ini')


# 检查配置文件是否存在
if not os.path.exists(config_path):
    print(f"错误：配置文件不存在 - {config_path}")
    exit(1)

config.read(config_path)

# 获取最新日志文件
logs = os.path.join(script_dir, 'logs')
os.makedirs(logs, exist_ok=True)
log_files = sorted(glob(os.path.join(logs, '*.log')), key=os.path.getmtime)
if log_files:
    log_file = log_files[-1]
else:
    log_file = os.path.join(logs, 'cpu_checks.log')

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# 封装本地命令执行函数
def run_local_command(cmd):
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    return result.stdout.strip()

# 遍历配置文件中的每个节点
for section in config.sections():
    # 跳过Settings和Database节点
    if section != 'Settings' and section != 'Database':
        try:
            # 获取节点信息
            name = config.get(section, 'name')
            ip = config.get(section, 'ip')
            username = config.get(section, 'username')  # 虽然不再使用，但保留原字段读取
            password = config.get(section, 'password')
            ssh_port = config.getint(section, 'ssh_port', fallback=22)

            # 本地执行命令获取 CPU 信息
            cpu_count = run_local_command('nproc --all')
            cpu_model = run_local_command('lscpu | grep "Model name" | cut -d ":" -f 2 | sed -e "s/^[[:space:]]*//"')

            # 记录 CPU 信息到日志文件
            logger.info(f"Node: {name} ({ip})")
            logger.info(f"CPU Count: {cpu_count}")
            logger.info(f"CPU Model: {cpu_model}")

        except Exception as e:
            logger.error(f"未知错误：{name} ({ip}): {e}")
