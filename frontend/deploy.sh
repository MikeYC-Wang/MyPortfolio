#!/usr/bin/env sh

# 確保腳本拋出遇到的錯誤
set -e

# 開始打包編譯 Vue 專案
echo "開始打包編譯..."
npm run build

# 進入打包後的資料夾 (Vite 預設是 dist)
cd dist

# 初始化 Git 並強制推送到 gh-pages 分支
git init
git add -A
git commit -m 'deploy to GitHub Pages'

# 直接推送到你的儲存庫的 gh-pages 分支
echo "準備推送到 GitHub..."
git push -f https://github.com/MikeYC-Wang/MyPortfolio.git master:gh-pages

# 回到上一層
cd -
echo "部署完成！請等待 1~2 分鐘讓 GitHub Pages 更新。"