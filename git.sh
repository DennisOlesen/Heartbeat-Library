echo -e "Enter commit message"
read commit

echo -e "Pushing"
read pushing

git add -A
git commit -m "$commit"
git push "$pushing"
