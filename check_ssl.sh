#!/bin/bash
# SSL 证书链验证脚本

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  SSL 证书链验证工具${NC}"
echo -e "${GREEN}========================================${NC}"

DOMAIN="material.sdyhjzgc.com"

echo -e "\n${YELLOW}[1/4] 检查本地证书文件...${NC}"
if [ -f "/etc/nginx/ssl/material.sdyhjzgc.com_fullchain.crt" ]; then
    echo -e "${GREEN}✓ 完整证书链文件存在${NC}"
    
    # 统计证书数量
    CERT_COUNT=$(grep -c "BEGIN CERTIFICATE" /etc/nginx/ssl/material.sdyhjzgc.com_fullchain.crt)
    echo -e "  证书链包含：$CERT_COUNT 个证书"
    
    if [ $CERT_COUNT -lt 3 ]; then
        echo -e "${YELLOW}⚠ 警告：证书链可能不完整（建议至少包含 3 个证书）${NC}"
    fi
else
    echo -e "${RED}✗ 完整证书链文件不存在${NC}"
fi

echo -e "\n${YELLOW}[2/4] 验证证书链完整性...${NC}"
openssl verify -CAfile "/home/abc/material-sdyhjzgc-com/TrustAsia TLS RSA Root CA.pem" \
    -untrusted "/home/abc/material-sdyhjzgc-com/LiteSSL RSA CA 2025.pem" \
    /etc/nginx/ssl/material.sdyhjzgc.com_fullchain.crt 2>&1

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 证书链验证通过${NC}"
else
    echo -e "${YELLOW}⚠ 证书链验证失败，可能需要手动信任根证书${NC}"
fi

echo -e "\n${YELLOW}[3/4] 测试 HTTPS 连接...${NC}"
RESPONSE=$(curl -k -s -o /dev/null -w "%{http_code}" https://$DOMAIN/health/ 2>/dev/null)
if [ "$RESPONSE" = "200" ]; then
    echo -e "${GREEN}✓ HTTPS 连接正常 (HTTP $RESPONSE)${NC}"
else
    echo -e "${RED}✗ HTTPS 连接失败 (HTTP $RESPONSE)${NC}"
fi

echo -e "\n${YELLOW}[4/4] 检查证书信息...${NC}"
echo | openssl s_client -connect $DOMAIN:443 -servername $DOMAIN 2>/dev/null | \
    openssl x509 -noout -dates -subject -issuer 2>/dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 证书信息读取成功${NC}"
else
    echo -e "${RED}✗ 无法读取证书信息${NC}"
fi

echo -e "\n${GREEN}========================================${NC}"
echo -e "${YELLOW}浏览器访问提示：${NC}"
echo -e ""
echo -e "如果浏览器仍然显示证书风险，请尝试以下方法："
echo -e ""
echo -e "1. ${YELLOW}清除浏览器缓存和 SSL 状态${NC}"
echo -e "   Chrome: 设置 → 隐私和安全 → 清除浏览数据"
echo -e "   Firefox: 选项 → 隐私与安全 → 清除数据"
echo -e ""
echo -e "2. ${YELLOW}手动信任根证书${NC}"
echo -e "   下载并安装：/home/abc/material-sdyhjzgc-com/TrustAsia TLS RSA Root CA.pem"
echo -e ""
echo -e "3. ${YELLOW}检查系统时间是否正确${NC}"
echo -e "   date 命令查看当前时间"
echo -e ""
echo -e "4. ${YELLOW}使用在线工具检测${NC}"
echo -e "   https://myssl.com/"
echo -e "   https://www.ssllabs.com/ssltest/"
echo -e ""
