# gforgeZulipBridge


### Setup
```
git clone https://github.com/jmandel/gforgeZulipBridge
cd gforgeZulipBridge
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configure

Create `env_values.py` with secrets, like:

```
cat > env_values.py

import os

os.environ['GFORGE_PASSWORD'] = "secret"
os.environ['ZULIP_EMAIL'] = "secret"
os.environ['ZULIP_API_KEY'] = "secret"
```

### Deploy to lambda

    sh deploy.sh
