# coding:utf-8
# Author: wendynail98@outlook.com

import os
import numpy as np
from PIL import Image
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score


class Classifier:
    '''
    分类器
    使用图片的直方图信息做特征
    使用KNN算法做分类算法
    '''

    def __init__(self, dest_dir, categories=None, bin=40, k=5):
        '''
        构造函数
        @param dest_dir: 存放分类好的图片的路径
        @param categories: 分类，如果没有指定则从目标路径下读取文件夹
                            分类的顺序将作为分类的依据
        @param bin: 直方图宽度
        @param k: KNN参数K
        '''
        # 验证路径存在
        if not os.path.exists(dest_dir):
            print("错误：目标路径不存在")
        else:
            self.dest_dir = dest_dir

        if categories != None:
            self.categories = categories
        else:
            self.categories = [f for f in os.listdir(dest_dir)
                            if os.path.isdir(os.path.join(self.dest_dir, f))]

        # 初始化直方图控制参数
        self.bins = list(range(0, 255, bin))
        if self.bins[-1] != 255:
            self.bins.append(255)

        # KNN
        self.clf = KNeighborsClassifier(n_neighbors=k, p=1, n_jobs=4)
        # self.clf = RandomForestClassifier(n_estimators=15, n_jobs=2, max_depth=3)

        # 组织数据
        self.x, self.y = self.get_data()

    def _get_features(self, image):
        '''从一个图片对象中抽取特征'''
        temp_x = []

        # m (height, width, channel)
        m = np.asarray(image)

        # 有的图片只有单通道
        if len(m.shape) != 3:
            f = m.flatten().shape[0]
            hist, _ = np.histogram(m.flatten(), bins=self.bins)
            temp_x.extend(hist)

            # 用0补齐剩余两个通道
            h_zero = [0] * len(hist) * 2
            temp_x.extend(h_zero)
        else:
            f = m[:, :, 0].flatten().shape[0]

            for i in range(3):
                hist, _ = np.histogram(m[:, :, i].flatten(), bins=self.bins)
                temp_x.extend(hist)

        return np.array(temp_x) / f

    def get_data(self, shuffle=True):
        '''
        抽取图片特征，组成数据格式
        返回 x_train, x_test, y_train, y_test
        '''
        # 准备数据
        x = []
        y = []

        # 遍历图片
        for i, category in enumerate(self.categories):
            for filename in os.listdir(os.path.join(self.dest_dir, category)):
                if filename.endswith(".gif"):
                    continue
                # 构造图片路径并打开
                file_path = os.path.join(self.dest_dir, category, filename)
                image = Image.open(file_path)

                # 抽取特征并添加到数据集中
                x.append(self._get_features(image))
                y.append(i)

        # 重新排序
        x = np.array(x)
        y = np.array(y)
        if shuffle:
            r = np.arange(len(x))
            np.random.shuffle(r)
            x = x[r, :]
            y = y[r]

        # 返回结果
        return x, y

    def reget_data(self):
        '''重新组织一次数据'''
        self.x, self.y = self.get_data()

    def train(self):
        '''训练算法，返回验证准确率'''
        # 划分训练集和测试集
        x_train, x_test, y_train, y_test = train_test_split(self.x, self.y)

        # 训练
        self.clf.fit(x_train, y_train)

        # 验证
        y_pred = self.clf.predict(x_test)

        # 返回验证精确率
        return accuracy_score(y_test, y_pred)

    def predict_each(self, filename):
        '''预测一个图片是否是相应的分类'''
        # 打开图片，抽取特征
        image = Image.open(filename)
        x = self._get_features(image)

        # 预测
        y_pred_ind = self.clf.predict([x])[0]

        # 返回分类的名称
        return self.categories[y_pred_ind]
