import sys
import os
import glob
import xml.etree.ElementTree as ET
import random
import time
from shutil import copyfile

class_names_dict = {'gold_mine':0,
'elx_mine':1,
'dark_mine':2,
'th':3,
'eagle':4,
'air_def':5,
'inferno':6,
'xbow':7,
'wiz_tower':8,
'bomb_tower':9,
'air_sweeper':10,
'cannon':11,
'mortar':12,
'archer_tower':13,
'queen':14,
'king':15,
'warden':16,
'gold_storage':17,
'elx_storage':18,
'dark_storage':19,
'cc':20,
'scatter':21,
'champ':22
}

def make_output_dir(random):
    if random:
        dir_name = f'{str(time.time())}'
    else:
        dir_name = 'data/data'
    os.mkdir(dir_name)
    os.mkdir(f"{dir_name}/training")
    os.mkdir(f"{dir_name}/validation")
    os.mkdir(f"{dir_name}/training/images")
    os.mkdir(f"{dir_name}/validation/images")
    os.mkdir(f"{dir_name}/training/labels")
    os.mkdir(f"{dir_name}/validation/labels")

    return dir_name

def random_split_data(random_fraction, xml_dir_path, random_seed=None):
    if random_seed == None:
        random.seed()
    else:
        random.seed(random_seed)

    all_xml_files = os.listdir(xml_dir_path)
    if len(all_xml_files) == 0:
        print("Error: no .xml files found in ground-truth")
        sys.exit()

    split_int = int(len(all_xml_files)*(1-random_fraction))

    random.shuffle(all_xml_files)

    train_list = all_xml_files[:split_int]
    val_list = all_xml_files[split_int:]

    return [train_list, val_list]

def class_to_index(class_name):
    return class_names_dict[class_name]

def make_training_txt_list():
    all_files = os.listdir(f'data/data/training/images')
    with open('data/data/training_list.txt', "w") as new_f:
        for file in all_files:
            file = file.replace('txt', 'jpg')
            line = f'data/data/training/images/{file}'
            new_f.write(f'{line}\n')

def make_validation_txt_list():
    all_files = os.listdir(f'data/data/validation/images')
    with open('data/data/validation_list.txt', "w") as new_f:
        for file in all_files:
            file = file.replace('txt', 'jpg')
            line = f'data/data/validation/images/{file}'
            new_f.write(f'{line}\n')

def make_start_command(class_names_dict):
    start_command = f"python train.py \
--weights weights/yolov5s.pt \
--data data/clash.yaml \
--batch-size 8 \
--img-size 608 \
--hyp data/hyp-clash.yaml \
--epochs 300"

    with open(f'start_command.txt', "w") as new_f:
        new_f.write(start_command)


if __name__ == '__main__':

    path_to_folder = 'data/copied_data'

    out_dir = make_output_dir(False)

    train_val_list = random_split_data(0.2, f'{path_to_folder}/xml_annotations')

    for i, xml_list in enumerate(train_val_list):

        if i == 0:
            train_or_val = 'training'
        else:
            train_or_val = 'validation'


        for tmp_file in xml_list:
            print(tmp_file)
            # 1. create new file (VOC format)
            with open(f'{out_dir}/{train_or_val}/labels/{tmp_file.replace(".xml", ".txt")}', "a") as new_f:
                root = ET.parse(f"{path_to_folder}/xml_annotations/{tmp_file}").getroot()
                img_size =  root.find('size')
                img_width = int(img_size.find('width').text)
                img_height = int(img_size.find('height').text)
                for obj in root.findall('object'):
                    obj_name = obj.find('name').text
                    try:
                        obj_index = class_to_index(obj_name)
                    except KeyError:
                        print(tmp_file)
                    bndbox = obj.find('bndbox')
                    left = bndbox.find('xmin').text
                    top = bndbox.find('ymin').text
                    right = bndbox.find('xmax').text
                    bottom = bndbox.find('ymax').text

                    x_center = str(round(((int(left)+int(right))/2)/img_width, 6))
                    y_center = str(round(((int(top)+int(bottom))/2)/img_height, 6))
                    obj_width = str(round(abs(int(left)-int(right))/img_width, 6))
                    obj_height = str(round(abs(int(top)-int(bottom))/img_height, 6))

                    new_f.write("%s %s %s %s %s\n" % (obj_index, x_center, y_center, obj_width, obj_height))
            copyfile(f'{path_to_folder}/images/{tmp_file.replace(".xml", ".jpg")}', 
                    f'{out_dir}/{train_or_val}/images/{tmp_file.replace(".xml", ".jpg")}')


    make_training_txt_list()

    make_validation_txt_list()

    make_start_command(class_names_dict)

    print("Conversion completed!")
