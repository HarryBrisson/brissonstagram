from functions.s3.s3_downloads import *
from functions.s3.s3_uploads import *

import subprocess as sp


def snackablize_video_by_s3_key(k):

    download_file_from_s3(bucket,k,'temp/temp.mpg')

    filenamebase = k.split('.')[0].split('/')[-1].replace('Home Video #','').replace(' -- ','-')
    cmd = 'ffmpeg -i temp/temp.mpg -acodec copy -f segment -segment_time 5 -vcodec copy -reset_timestamps 1 -map 0 temp/clips/{}-%04d.mp4'.format(filenamebase)
    sp.call(cmd, shell=True)

    clips = [f for f in os.listdir("temp/clips") if '.mp4' in f]

    for c in clips:
        print(c)
        source_path = "temp/clips/{}".format(c)
        destination_path = 'clips/{}/{}'.format(c.split('-')[0],c)
        add_file_to_s3(source_path, 'brissonstagram', destination_path)
        os.remove(source_path)

    os.remove('temp/temp.mpg')
    
    
def snackablize_videos():

    keys = get_list_of_s3_object_keys('brissonstagram',filter='full-length')
    home_video_keys = [k for k in keys if 'Home Video #' in k]

    for k in home_video_keys:
        snackablize_video_by_s3_key(k)


if __name__ == '__main__':
	snackablize_videos()