#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/5/2 上午11:33
# @Author  : mrlittlepig
# @Site    : www.mrlittlepig.xyz
# @File    : TFrecords.py
# @Software: PyCharm Community Edition

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import tensorflow as tf
import utils.fileUtil as file
from utils.labelFile2Map import *
from PIL import Image

imageSZ = {'rows': 28, 'cols': 28}

# 制作二进制数据
def create_record(label_file, dst_records):
    writer = tf.python_io.TFRecordWriter(dst_records)

    lines = readLines(label_file)
    label_record = map(lines)
    file_name_length = len(file.getFileName(label_file))
    images_dir = label_file[:-1 * file_name_length]
    index = 0
    for name in label_record:
        index = index + 1
        image_file = images_dir + str(label_record[name]) + '/' + name
        img = Image.open(image_file)
        img = img.resize((imageSZ['rows'], imageSZ['cols']))
        bytesImg = img.tobytes()
        example = tf.train.Example(
            features=tf.train.Features(feature={
                "label": tf.train.Feature(int64_list=tf.train.Int64List(value=[int(label_record[name])])),
                'bytesImg': tf.train.Feature(bytes_list=tf.train.BytesList(value=[bytesImg]))
            }))
        if index % 100 == 0:
            print("processing %d:" % index + images_dir + name)
        writer.write(example.SerializeToString())
    print("done!")
    writer.close()


# 读取二进制数据
def read_and_decode(filename):
    # 创建文件队列,不限读取的数量
    filename_queue = tf.train.string_input_producer([filename])
    # create a reader from file queue
    reader = tf.TFRecordReader()
    # reader从文件队列中读入一个序列化的样本
    _, serialized_example = reader.read(filename_queue)
    # get feature from serialized example
    # 解析符号化的样本
    features = tf.parse_single_example(
        serialized_example,
        features={
            'label': tf.FixedLenFeature([], tf.int64),
            'bytesImg': tf.FixedLenFeature([], tf.string)
        }
    )
    image = tf.decode_raw(features['bytesImg'], tf.uint8)
    image = tf.reshape(image, [imageSZ[0], imageSZ[1]])
    label = tf.cast(features['label'], tf.int32)
    return image, label

def test_reader(recordsFile):
    image, label = read_and_decode(recordsFile)
    with tf.Session() as sess:  # 开始一个会话
        init_op = tf.initialize_all_variables()
        sess.run(init_op)
        coord = tf.train.Coordinator()
        threads = tf.train.start_queue_runners(coord=coord)
        for i in range(1):
            example, l = sess.run([image, label])  # 在会话中取出image和label
            # img = Image.fromarray(example, 'RGB')  # 如果img是RGB图像
            img = Image.fromarray(example)  # 这里Image是之前提到的
            img.save('./' + '_'+'Label_' + str(l) + '.jpg')  # 存下图片
            print(example, l)
        coord.request_stop()
        coord.join(threads)

if __name__ == '__main__':
    test_label_file, test_dst_records = "./MNIST_data/mnist_test/test.txt", "./MNIST_data/mnist_test.tfrecords"
    # data = create_record(test_label_file, test_dst_records)
    test_reader(test_dst_records)