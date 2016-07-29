rm distribution.zip
zip -p distribution.zip

cd venv/lib/python2.7/site-packages/
zip -r9 ../../../../distribution.zip *
cd -

zip -g distribution.zip gforge.py env_values.py __init__.py
