echo -e "Enter commit message"
read commit

git add -A
git commit -m "$commit"
git push
