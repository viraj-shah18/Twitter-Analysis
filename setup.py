import os
try:
    import twint
except:
    os.system(
        "pip3 install --upgrade git+https://github.com/twintproject/twint.git@origin/master#egg=twint"
    )
    import twint