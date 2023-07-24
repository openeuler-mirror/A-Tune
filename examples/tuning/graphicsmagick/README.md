1.Prepare the environment
sh prepare.sh
2.Download two images for tuning,image parameters below were used for this gm tuning,but any other two different images are OK.
test00.jpg:(pixel:1160x806,type:JPEG,size:101.7KB)
test01.jpg:(pixel:4000x2500,type:JPEG,size:5.0M)
3.Modify Phoronix-test-suite file and run command below to do pts test manually 
cd /var/lib/phoronix-test-suite/test-profiles/pts/graphics-magick-2.1.0
modify all of "1.3.38" to "1.3.40"
script -a ptsBasic.txt
phoronix-test-suite run graphics-magick-2.1.0
exit
4.Start to tuning 
atune-adm tuning --project graphicsmagick  --detail gm_client.yaml
5.Restore the environment 
atune-adm tuning --restore --project graphicsmagick