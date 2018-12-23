# brissonstagram
home video vignettes via instagram


## editing the videos into clips

if you already have long videos on s3, you'll need to break them down into short snackable content first


### ec2 instance

start up an ec2 instance, referencing keypair location & public IP

`ssh -i ".ssh/AWS_KEY_PAIR.pem" ubuntu@123.456.789.000`


### ssh key

create a ssh key

`ssh-keygen -t rsa -b 4096 -C "GITHUB ACCOUNT EMAIL ADDRESS"`

then, access that key

`cat .ssh/id_rsa.pub`

then, paste that to the deploy keys for this project


### clone repo from github & prep your server

finally, use git to clone this project onto your ec2 instance

`git clone git@github.com:harrybrisson/brissonstagram.git`

run the initialize script to set up everything you need program and module-wise

`cd brissonstagram`

`bash initialize.sh`

now, add in your credentials for aws, twitter & gmail

`nano authorizations/aws-credentials.json`

`nano authorizations/twitter-credentials.json`

`nano authorizations/gmail-credentials.json`


### time to prepare the clips

then, you can start up tmux to keep the function going even if you disconnect

`tmux`

run the snackablize function!

`python3 snackablize_videos.py`


### bring your memories into the light

after you break down your videos into clips, you can run the post random memory script

`python3 post_random_memory.py`

you can also set up a crontab to run every 6 hours; edit your scheduled tasks using `crontab -e` then add the below code at the end of the file

`0 */6 * * * python3 post_random_memory.py`
