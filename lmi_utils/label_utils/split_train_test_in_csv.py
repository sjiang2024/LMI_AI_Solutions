import collections
from sklearn.model_selection import train_test_split
import os

#LMI modules
from label_utils import csv_utils


def copy_images(data, out_path):
    import shutil
    if not os.path.isdir(out_path):
        os.makedirs(out_path)
    for im_name in data:
        for mask in data[im_name]:
            shutil.copy2(mask.fullpath, out_path)

def split_data_in_csv(path_csv, path_img, test_ratio=0.25, rs=777):
    data,class_map = csv_utils.load_csv(path_csv, path_img)
    img_names = list(data.keys())
    train_names,test_names = train_test_split(img_names, test_size=test_ratio, random_state=rs)
    #deal with train
    train_data = collections.defaultdict(list)
    for name in train_names:
        train_data[name] = data[name]
    #deal with test
    test_data = collections.defaultdict(list)
    for name in test_names:
        test_data[name] = data[name]
    print(f'total images: {len(img_names)}')
    print(f'split: {len(train_data)} images to training, {len(test_data)} images ({test_ratio*100}%) to testing')
    return train_data,test_data

def generate_split_datasets(train_data, test_data, path_out, test_only):
    if not test_only:
        path_out_train = os.path.join(path_out, 'train')
        copy_images(train_data, path_out_train)
        csv_utils.write_to_csv(train_data, os.path.join(path_out_train, 'labels.csv'))

    path_out_test = os.path.join(path_out, 'test')
    copy_images(test_data, path_out_test)
    csv_utils.write_to_csv(test_data, os.path.join(path_out_test, 'labels.csv'))


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--path_imgs', required=True, help='the path to the image folder')
    ap.add_argument('--path_csv', default='labels.csv', help='[optinal] the path of a csv file that corresponds to path_imgs, default="labels.csv" in path_imgs')
    ap.add_argument('--path_out', required=True, help='the output path to the train dataset')
    ap.add_argument('--test_ratio', default=0.2, type=float, help='[optinal] the ratio of the test dataset, default=0.2')
    ap.add_argument('--test_only', action='store_true', help='[optinal] generate ONLY test dataset')
    args = vars(ap.parse_args())
    
    path_imgs = args['path_imgs']
    path_csv = args['path_csv'] if args['path_csv']!='labels.csv' else os.path.join(path_imgs, args['path_csv'])
    #check if annotation exists
    if not os.path.isfile(path_csv):
        raise Exception(f'Not found file: {path_csv}')
    train_data, test_data = split_data_in_csv(path_csv, path_imgs, test_ratio=args['test_ratio'])
    generate_split_datasets(train_data, test_data, args['path_out'], test_only=args['test_only'])
