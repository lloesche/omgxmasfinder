# OMG.de 2016 Weihnachtsgewinnspiel Image Finder
This year OMG.de is doing a great little Christmas Contest where each day from the 1st until the 18th of December
they post an image containing part of a sentence under a random product in their shop.
Details: http://www.makes-it-work.de/omg-de-weihnachtsgewinnspiel-2016/

There's a social element to it where they post hints where to find the image  on facebook.
However given that we're all IT folks I couldn't be bothered with any facebook nonsense.

So here's a script that will automatically search for the image in their shop and dump it to a local file.
It also creates a cache.yaml which contains all the already found image URLs.

On the 18th you can call merge.sh which will combine all the images into the final result.

Run findimg.py once a day using a cron or something similar.
