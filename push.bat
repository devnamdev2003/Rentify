echo "Start"

pip freeze > .\requirements.txt
git status
git add .
git commit -m "update"
git push -u origin main
git status