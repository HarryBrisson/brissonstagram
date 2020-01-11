# brissonstagram-portfolio-viewer
 look at all these frames


### get it running

first need to set up a virtual environment

`virtualenv .env`

`source .env/bin/activate`

then, make sure to install requirements

`sudo python3 -m pip install -r requirements.txt`

you may need to also add aws configuration details

`aws configure`

then you can intialize zappa and then deploy

`zappa init`

`zappa deploy dev`


### set up the url

AWS -> Certificate Manager
* get a certificate for url
* include the reference number in zappa_settings.json

API Gateway -> Custom Domain Names -> Create Custom Domain Name
* select ACM certificate
* set up base path mapping (probably to prod)
* set up CNAME for Target Domain Name