set -x

python scrape_bbc.py
python build.py
git add data outputs
git commit -m "Update $(date +"%Y-%m-%d %H:%M:%S")" --quiet
git push --quiet
