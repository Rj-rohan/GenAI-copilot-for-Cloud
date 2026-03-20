@echo off
echo Setting up Git remote and pushing code...
echo.

cd /d "%~dp0"

git init
git remote remove origin 2>nul
git remote add origin https://github.com/Rj-rohan/GenAI-copilot-for-Cloud.git

echo.
echo Staging all files...
git add .

echo.
echo Committing changes...
git commit -m "Initial commit: GenAI Cloud Security Copilot"

echo.
echo Pushing to dev branch...
git branch -M dev
git push -u origin dev --force

echo.
echo Done! Code pushed to https://github.com/Rj-rohan/GenAI-copilot-for-Cloud/tree/dev
pause
