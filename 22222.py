import paddle
import jieba
import re
import collections
import numpy as np
from tqdm import tqdm
import paddle.nn as nn


class MyLSTM(paddle.nn.Layer):
    def __init__(self):
        super(MyLSTM, self).__init__()
        self.embedding = nn.Embedding(10135, 256)
        self.lstm = nn.LSTM(256, 128, num_layers=2, direction='bidirect', dropout=0.5)
        self.linear = nn.Linear(in_features=128 * 2, out_features=len(label_idx))
        self.dropout = nn.Dropout(0.5)

    def forward(self, inputs):
        emb = self.dropout(self.embedding(inputs))
        # output形状大小为[batch_size,time_steps,num_directions * hidden_size]
        # h和c的形状大小为[num_layers * num_directions, batch_size, hidden_size]
        output, (h, c) = self.lstm(emb)
        x = paddle.mean(output, axis=1)
        # x形状大小为[batch_size, hidden_size * num_directions]
        x = self.dropout(x)
        return self.linear(x)


class MyLSTM_Attention(paddle.nn.Layer):
    def __init__(self):
        super(MyLSTM_Attention, self).__init__()
        self.embedding = nn.Embedding(10135, 256)
        self.lstm = nn.LSTM(256, 128, num_layers=2, direction='bidirect', dropout=0.5)
        self.attention = nn.MultiHeadAttention(embed_dim=128 * 2, num_heads=2, dropout=0.2)  # embed_dim要能被num_heads整除
        self.linear = nn.Linear(in_features=128 * 2, out_features=len(label_idx))
        self.dropout = nn.Dropout(0.5)

    def forward(self, inputs):
        emb = self.dropout(self.embedding(inputs))
        # output形状大小为[batch_size,time_steps,num_directions * hidden_size]
        # h和c的形状大小为[num_layers * num_directions, batch_size, hidden_size]
        output, (h, c) = self.lstm(emb)
        att = self.attention(output)
        # attention输入与输出tensor shape相同
        x = paddle.mean(att, axis=1)
        # x形状大小为[batch_size, hidden_size * num_directions]
        x = self.dropout(x)
        return self.linear(x)


def tokenize(string):
    jieba.load_userdict(r"major_library.txt")
    string = re.sub(r'\s+', '', string)
    words = jieba.cut_for_search(string)
    # print(words)
    return words


def build_dict(train_data):
    word_freq = collections.defaultdict(int)
    label_set = set()
    for seq, label in train_data:
        for word in seq:
            word_freq[word] += 1
        label_set.add(label)
    temp = sorted(word_freq.items(), key=lambda x: x[1], reverse=False)
    words, _ = list(zip(*temp))
    word_idx = dict(list(zip(words, range(len(words)))))
    word_idx['<unk>'] = len(words)
    word_idx['<pad>'] = len(words) + 1
    label_idx = dict(list(zip(label_set, range(len(label_set)))))
    return word_idx, label_idx


def load_data(data_path, is_test=False):
    dataset = []
    with open(data_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not is_test:
                items = line.strip().split(' ')
                if len(items) != 3:
                    continue
                sent = items[2].strip()
                label = items[1].strip()
                dataset.append((sent, label))
            else:
                dataset.append(line.strip())
    return dataset


if __name__ == '__main__':

    # 加载训练数据
    train_data = load_data(r'1.txt')

    # 构建词汇表和标签索引
    word_idx, label_idx = build_dict(train_data)

    # 输出词汇表大小
    vocab_size = len(word_idx) + 1

    # 加载模型参数
    model_state_dict = paddle.load('./model_final.pdparams')

    # 创建模型实例
    model = MyLSTM_Attention()
    model.set_state_dict(model_state_dict)
    model.eval()

    label_map = dict(zip(label_idx.values(), label_idx.keys()))

    while True:
        input_text = input("请输入要分类的文本（输入'exit'退出）: ")

        if input_text == 'exit':
            break

        # 预处理输入文本
        input_tokens = [word for word in tokenize(input_text)]  # 使用分词函数进行分词
        input_numeric = [word_idx.get(token, word_idx['<unk>']) for token in input_tokens]  # 转换为数字表示

        # 填充或截断到固定长度（例如，15）
        max_sequence_length = 15
        if len(input_numeric) > max_sequence_length:
            input_numeric = input_numeric[:max_sequence_length]
        elif len(input_numeric) < max_sequence_length:
            padding = [word_idx['<pad>']] * (max_sequence_length - len(input_numeric))
            input_numeric += padding

        # 将数字序列转换为Paddle张量
        input_tensor = paddle.to_tensor(input_numeric)
        input_tensor = paddle.unsqueeze(input_tensor, axis=0)  # 添加批次维度

        with paddle.no_grad():
            model.eval()  # 将模型设置为评估模式
            results = model(input_tensor)  # 输入文本并获取模型的输出

        # 处理模型的输出，找到最有可能的类别
        probs = results[0].numpy()
        idx = np.argmax(probs)
        predicted_label = label_map[idx]

        print("预测类别:", predicted_label)
