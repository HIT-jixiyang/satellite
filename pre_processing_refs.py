import os
import  numpy as np
import cv2
ref_path='/extend/2019_04'
list=os.listdir(ref_path)
list=sorted(list)
temp_date=list[0].split('_')[2]
i=0
date_radar_dict = {}
while i<len(list)-1:
    date_current=list[i].split('_')[2]
    date_next=list[i+1].split('_')[2]
    radar_num_current=int(list[i].split('_')[4].split('.')[0])
    radar_num_next=int(list[i+1].split('_')[4].split('.')[0])
    temp_list=[]

    if date_current==date_next:
        while date_current==date_next:
            if radar_num_next>radar_num_current:
                date_radar_dict[date_current]=radar_num_next
            else:
                date_radar_dict[date_current]=radar_num_current
            i = i + 1
            date_current = list[i].split('_')[2]
            date_next = list[i + 1].split('_')[2]

            radar_num_current = list[i].split('_')[4].split('.')[0]
            radar_num_next = list[i+1].split('_')[4].split('.')[0]
    else:
        i=i+1
for key in date_radar_dict.keys():
    path='/extend/2019_04'+'/cappi_ref_'+key+'_2500_'+str(date_radar_dict[key])+'.ref'
    pad_ref = np.zeros([900, 900], dtype=np.uint8)
    ref = np.fromfile(path, dtype=np.uint8).reshape(700, 900)
    ref[ref <= 15] = 0
    ref[ref >= 80] = 0
    pad_ref[100:-100, :] = ref
    cv2.imwrite('/extend/2019_png/'+'/cappi_ref_'+key+'_2500_'+str(0)+'.png',pad_ref)


print()
