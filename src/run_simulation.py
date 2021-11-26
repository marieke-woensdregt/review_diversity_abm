import urllib.request
(fn,hd) = urllib.request.urlretrieve('https://gist.githubusercontent.com/LukasWallrich/0c13537940fd34a64f3ea97586441b0c/raw/run_simulation.py')
exec(open(fn).read())

