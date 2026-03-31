#!/bin/bash
# 安装根证书到系统信任库

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  安装根证书到系统信任库${NC}"
echo -e "${GREEN}========================================${NC}"

ROOT_CA="/home/abc/material-sdyhjzgc-com/TrustAsia TLS RSA Root CA.pem"

if [ ! -f "$ROOT_CA" ]; then
    echo -e "${RED}错误：根证书文件不存在：$ROOT_CA${NC}"
    exit 1
fi

echo -e "\n${YELLOW}[1/3] 复制根证书到系统目录...${NC}"
sudo cp "$ROOT_CA" /usr/local/share/ca-certificates/trustasia-root.crt

echo -e "${YELLOW}[2/3] 更新系统证书信任库...${NC}"
if command -v update-ca-certificates > /dev/null; then
    sudo update-ca-certificates
    echo -e "${GREEN}✓ 系统证书已更新${NC}"
else
    echo -e "${YELLOW}⚠ 未找到 update-ca-certificates 命令${NC}"
fi

echo -e "${YELLOW}[3/3] 重启 Nginx...${NC}"
sudo systemctl reload nginx
echo -e "${GREEN}✓ Nginx 已重启${NC}"

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}✅ 根证书安装完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e ""
echo -e "现在请："
echo -e "1. ${YELLOW}完全关闭浏览器（所有窗口）${NC}"
echo -e "2. ${YELLOW}重新打开浏览器${NC}"
echo -e "3. ${YELLOW}访问 https://material.sdyhjzgc.com${NC}"
echo -e ""
echo -e "如果仍然有问题，可能需要在浏览器中手动导入根证书。"
