1. Prepare the environment
sh prepare.sh
2. Find a video to test and name it as test00.flv(basic parameters:41m34s,640x352,flv,83.6MB,video encoding AVC1,audio encoding AAC),other flv videos are available
3. Start to tuning
atune-adm tuning --project ffmpeg --detail ffmpeg_client.yaml
4. Restore the environment
atune-adm tuning --restore --project ffmpeg