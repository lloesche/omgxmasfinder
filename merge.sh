#!/bin/bash
set -o errexit -o nounset -o pipefail
hash convert > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "Install ImageMagick to merge images"
  exit 1
fi
for image in [0-9]*.jpg
do
  convert "$image" -fuzz 5% -transparent white ${image/%.jpg/.png}
done
declare -a pages
for png in [0-9]*.png
do
  pages+=(-page +0+0 $png)
done
convert "${pages[@]}" -layers flatten result.jpg
rm -f *.png
echo "Wrote result.jpg"
