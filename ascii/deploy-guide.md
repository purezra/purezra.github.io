# 将ASCII艺术转换器部署到自定义域名指南

## 概述

本指南将帮助您将ASCII艺术转换器网页应用部署到您自己的域名上，使其可以在任何设备上访问。我们提供了多种部署方案，您可以根据自己的需求和技术背景选择最适合的方式。

## 方案一：使用GitHub Pages（推荐，免费且免费）

### 准备工作
1. 拥有一个GitHub账号
2. 拥有一个自定义域名
3. 本地安装Git

### 步骤

#### 1. 创建GitHub仓库
- 登录GitHub，点击右上角"+"按钮，选择"New repository"
- 仓库名称必须为：`your-username.github.io`（将your-username替换为您的GitHub用户名）
- 勾选"Add a README file"
- 点击"Create repository"

#### 2. 上传ASCII艺术转换器文件
- 克隆仓库到本地：
  ```
  git clone https://github.com/your-username/your-username.github.io.git
  ```
- 将ASCII艺术转换器的所有文件（index.html、test-mobile.html等）复制到克隆仓库目录
- 提交并推送更改：
  ```
  cd your-username.github.io
  git add .
  git commit -m "Add ASCII Art Converter files"
  git push origin main
  ```

#### 3. 配置GitHub Pages
- 进入仓库设置：点击仓库页面上方的"Settings"
- 在左侧边栏找到"Pages"选项
- 在"Source"部分，选择分支为"main"，文件夹为"/ (root)"
- 点击"Save"，等待几分钟后，您的网站将可以通过`https://your-username.github.io`访问

#### 4. 绑定自定义域名
- 在GitHub Pages设置页面的"Custom domain"部分，输入您的自定义域名（例如：`ascii.yourdomain.com`）
- 点击"Save"
- 在您的域名注册商处（如阿里云、腾讯云、Namecheap等）添加DNS记录：
  - 类型：CNAME
  - 主机记录：ascii（或您想要的子域名）
  - 记录值：your-username.github.io.（注意末尾的点）
  - TTL：10分钟

#### 5. 启用HTTPS
- 在GitHub Pages设置页面，勾选"Enforce HTTPS"选项
- 等待几分钟，HTTPS证书将自动配置

## 方案二：使用云存储服务（如阿里云OSS、腾讯云COS）

### 准备工作
1. 拥有一个云服务提供商账号（阿里云、腾讯云等）
2. 拥有一个自定义域名并已备案（国内服务需要）
3. 已购买云存储服务（OSS/COS）

### 步骤

#### 1. 创建存储桶
- 登录云服务控制台，进入对象存储服务
- 创建一个新的存储桶，选择合适的区域
- 确保存储桶设置为"公有读"权限

#### 2. 开启静态网站托管
- 在存储桶设置中找到"静态网站托管"选项
- 启用静态网站托管功能
- 设置索引文档为"index.html"

#### 3. 上传文件
- 将ASCII艺术转换器的所有文件上传到存储桶根目录
- 确保文件权限设置为"公有读"

#### 4. 绑定自定义域名
- 在存储桶设置中找到"域名管理"或"自定义域名"选项
- 添加您的自定义域名（如：`ascii.yourdomain.com`）
- 获取系统生成的CNAME记录值

#### 5. 配置DNS解析
- 登录您的域名注册商控制台
- 添加CNAME记录，将您的子域名指向云存储提供的CNAME记录值

#### 6. 配置HTTPS
- 在云服务控制台申请免费SSL证书
- 将证书绑定到您的自定义域名
- 配置HTTPS强制跳转

## 方案三：使用传统Web服务器（Nginx/Apache）

### 准备工作
1. 拥有一台服务器（VPS或云服务器）
2. 已安装Web服务器软件（Nginx或Apache）
3. 拥有一个自定义域名
4. 已配置服务器防火墙，开放80和443端口

### 步骤

#### 1. 上传文件到服务器
- 使用FTP/SFTP工具（如FileZilla）将ASCII艺术转换器文件上传到服务器
- 推荐上传到`/var/www/ascii-art-converter`目录

#### 2. 配置Web服务器

##### Nginx配置示例：
```nginx
server {
    listen 80;
    server_name ascii.yourdomain.com;
    
    # 重定向到HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name ascii.yourdomain.com;
    
    # SSL证书配置
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    
    # SSL安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE:ECDH:AES:HIGH:!NULL:!aNULL:!MD5:!ADH:!RC4;
    ssl_prefer_server_ciphers on;
    
    # 网站根目录
    root /var/www/ascii-art-converter;
    index index.html;
    
    # 缓存配置
    location ~* \.(html|css|js|png|jpg|jpeg|gif|ico)$ {
        expires 1d;
        add_header Cache-Control "public, max-age=86400";
    }
    
    # 安全头配置
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
}
```

##### Apache配置示例：
```apache
<VirtualHost *:80>
    ServerName ascii.yourdomain.com
    Redirect permanent / https://ascii.yourdomain.com/
</VirtualHost>

<VirtualHost *:443>
    ServerName ascii.yourdomain.com
    DocumentRoot /var/www/ascii-art-converter
    
    SSLEngine on
    SSLCertificateFile /path/to/your/certificate.crt
    SSLCertificateKeyFile /path/to/your/private.key
    
    # 安全配置
    Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
    Header always set X-Frame-Options DENY
    Header always set X-Content-Type-Options nosniff
    Header always set X-XSS-Protection "1; mode=block"
    
    # 缓存配置
    <FilesMatch "\.(html|css|js|png|jpg|jpeg|gif|ico)$">
        Header set Cache-Control "public, max-age=86400"
    </FilesMatch>
</VirtualHost>
```

#### 3. 申请并配置SSL证书
- 使用Let's Encrypt免费证书：
  ```
  # 安装Certbot
  apt-get install certbot python3-certbot-nginx  # 对于Nginx
  # 或
  apt-get install certbot python3-certbot-apache  # 对于Apache
  
  # 申请证书
  certbot --nginx -d ascii.yourdomain.com  # 对于Nginx
  # 或
  certbot --apache -d ascii.yourdomain.com  # 对于Apache
  ```

#### 4. 配置DNS解析
- 在您的域名注册商处添加A记录，将您的子域名指向服务器IP地址

## 方案四：使用Serverless服务（如Vercel、Netlify）

### 准备工作
1. 拥有一个GitHub/GitLab/Bitbucket账号
2. 拥有一个自定义域名
3. 已将代码上传到代码仓库

### 步骤（以Vercel为例）

#### 1. 导入项目
- 登录Vercel账号
- 点击"New Project"
- 导入您的GitHub仓库

#### 2. 配置项目
- 项目名称：可以自定义
- 框架预设：选择"Other"
- 根目录：保持默认
- 构建命令：留空（静态网站不需要构建）
- 输出目录：留空

#### 3. 部署项目
- 点击"Deploy"按钮
- Vercel将自动部署您的网站，并提供一个临时域名

#### 4. 绑定自定义域名
- 在项目控制台中，点击"Settings" > "Domains"
- 输入您的自定义域名（如：`ascii.yourdomain.com`）
- 点击"Add"
- 按照提示在您的域名注册商处添加DNS记录

#### 5. 配置HTTPS
- Vercel自动为您的域名配置HTTPS证书
- 无需额外操作

## 常见问题解决

### 1. 域名解析不生效
- 检查DNS记录是否正确配置
- 等待DNS记录生效（通常需要几分钟到24小时）
- 使用`nslookup`或`dig`命令检查DNS解析：
  ```
  nslookup ascii.yourdomain.com
  dig ascii.yourdomain.com
  ```

### 2. HTTPS配置问题
- 确保SSL证书已正确安装
- 检查证书是否过期
- 清除浏览器缓存后重试

### 3. 页面样式错乱
- 检查文件路径是否正确
- 确保CSS和JavaScript文件已正确加载
- 检查浏览器控制台是否有错误信息

### 4. 功能无法正常使用
- 确保所有依赖文件已正确上传
- 检查浏览器控制台是否有JavaScript错误
- 确保CORS设置正确（如果使用API）

## 维护与更新

### 定期更新
- 当您对ASCII艺术转换器进行修改后，需要重新上传文件到服务器或代码仓库
- 如果使用GitHub Pages、Vercel或Netlify，只需推送更改即可自动更新

### 监控网站状态
- 使用网站监控工具（如UptimeRobot）监控网站可用性
- 定期检查SSL证书到期时间，及时续期

### 备份
- 定期备份您的网站文件和配置
- 对于数据库驱动的网站，定期备份数据库

## 总结

本指南提供了多种将ASCII艺术转换器部署到自定义域名的方案，从简单的GitHub Pages到复杂的自建服务器。您可以根据自己的技术背景、预算和需求选择最适合的方案。无论选择哪种方案，部署完成后，您都可以通过自己的域名随时随地访问这个有趣的ASCII艺术转换工具。
