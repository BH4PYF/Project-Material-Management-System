#!/bin/bash
# 材料管理系统 - 开发环境启动脚本
# 用法：bash start_dev.sh

set -e  # 出错即停

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  材料管理系统开发环境启动${NC}"
echo -e "${GREEN}========================================${NC}"

# 获取当前目录
APP_DIR=$(pwd)

echo -e "\n${GREEN}[1/5] 检查虚拟环境...${NC}"
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}创建虚拟环境...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ 虚拟环境创建完成${NC}"
fi

# 激活虚拟环境
echo -e "${YELLOW}激活虚拟环境...${NC}"
source venv/bin/activate

# 安装依赖
echo -e "\n${GREEN}[2/5] 安装依赖...${NC}"
pip install -r requirements.txt
echo -e "${GREEN}✓ 依赖安装完成${NC}"

# 检查环境变量文件
echo -e "\n${GREEN}[3/5] 检查环境变量...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}创建 .env 文件...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env 文件创建完成${NC}"
fi

# 收集静态文件
echo -e "\n${GREEN}[4/5] 收集静态文件...${NC}"
python manage.py collectstatic --noinput
echo -e "${GREEN}✓ 静态文件收集完成${NC}"

# 数据库迁移
echo -e "\n${GREEN}[5/5] 数据库迁移...${NC}"
python manage.py migrate
echo -e "${GREEN}✓ 数据库迁移完成${NC}"

# 启动开发服务器
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}✅ 环境准备完成，启动开发服务器...${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "\n访问地址: ${GREEN}http://0.0.0.0:8000/${NC}"
echo -e "超级用户: ${GREEN}admin${NC} / ${GREEN}admin123${NC}"
echo -e "\n按 ${YELLOW}Ctrl+C${NC} 停止服务器"
echo -e "\n${YELLOW}开发服务器启动中...${NC}"

python manage.py runserver 0.0.0.0:8000
