# Explanation
I recently switched to pipewire and wanted a better way to manage connections between inputs and outputs. I love qjackctl, but honestly connect enough inputs and outputs and it becomes a confusing mess. I wanted it to be immeadiately obvious what was connected to what. So I hashed this out in a couple of hours. I'm putting it here for anyone interested. As to why It's a client server type deal written in javascript, I wanted to be able to control it with my phone. That's probably oddly specific, but that's what I wanted to do so.

# Running
Install python3, python-aiohttp and python-jack from your package manager of choice. Then run `./main.py`, connect to localhost:8096 and it's off to the races. Alternatively you can install jack and aiohttp from pip with pip install -r requirements.txt

# Connecting remotely
run `HTTP_HOST=0.0.0.0 ./main.py` or `HTTP_HOST=:: ./main.py` to expose to your network. Security is not builtin, and to control access, please do so using nginx or whatever external tool suits you best.