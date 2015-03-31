echo "Enter commit message\n"
read message

git add -A
git commit -m "$message"
git push origin master
