import jieba
import math

#读取文件
def readfile(filename):
    with open(filename,mode='r',encoding='utf-8') as f:
        content=f.readline()
        sentences=[]
        while content!='':
            sentences.append(content[2:])
            content=f.readline()

    sentences.remove(sentences[0])#去除第一行
    return sentences

#去除无关词
def removeword(words):
    removelist = []
    newlist = []
    with open('./removewords.txt',mode='r',encoding='utf-8') as f:
        removewords = f.read()
        removelist = removewords.split('\n')
    for word in words:
        if not(word in removelist):
            newlist.append(word)
    return newlist

#jieba分词
def cutsentence(sentences):
    words = []
    for sentence in sentences:
        cutword = list(jieba.cut(sentence,cut_all=False))
        words.append(cutword)
    return words


#计算联合频率
def count_intersection(word1,word2,sentences):
    count = 0
    for sentence in sentences:
        if (word1 in sentence) and (word2 in sentence):
            count += 1
    return count
#计算word的SO-PMI值
def SO_PMI(word,P_seed,N_seed,sentences):
    PMI = 0.
    num_seed = len(P_seed)
    for i in range(num_seed):
        P_COUNT = count_intersection(word,P_seed[i],sentences)
        N_COUNT = count_intersection(word,N_seed[i],sentences)
        PMI += math.log((P_COUNT+1)/(N_COUNT+1))#防止为0都+1
    return PMI

#对词语的极性进行分类
def word_classfy(word_table,P_seed,N_seed,sentences):
    positive_word = {}
    negative_word = {}
    for word in word_table:
        #排除种子词
        if not (word in P_seed) and not (word in N_seed):
            so_pmi = SO_PMI(word,P_seed,N_seed,sentences)
            if so_pmi > 0:
                if not word in positive_word.keys():
                    positive_word[word] = so_pmi
            elif so_pmi < 0:
                if not word in negative_word.keys():
                    negative_word[word] = abs(so_pmi)

    #按照频率对正/负词的so_pmi绝对值进行降序排序，绝对值越大，该词的词性越强
    sorted_positive = sorted(positive_word.items(), key=lambda item: item[1], reverse=True)
    sorted_negative = sorted(negative_word.items(),key=lambda item:item[1],reverse=True)
    return sorted_positive,sorted_negative

#写入数据
def write_result(filename_p,filename_n,positive_words,negative_words):
    with open(filename_p,mode='a',encoding='utf-8') as f1:
        with open(filename_n,mode='a',encoding='utf-8') as f2:
            for i in range(50):
                p_word = positive_words[i][0]
                n_word = negative_words[i][0]
                f1.write(f'No_{i + 1},{p_word}'+'\n')
                f2.write(f'No_{i + 1},{n_word}'+'\n')

#获得词表(评论中所有词语构成的词集)
def get_wordtable(sentences):
    word_table = []
    for sentence in sentences:
        for word in sentence:
            if not word in word_table:
                word_table.append(word)
    return word_table


if __name__ == '__main__':
    
    sentences = readfile('./外卖评论.csv')
    #先分词 再去除停用词
    sentences = cutsentence(sentences)
    new_sentences = []#单个词汇集合
    for sentence in sentences:
        new_sentences.append(removeword(sentence))

    #获得词表
    word_table = get_wordtable(new_sentences)#去除停用词后的最终词表

    #选择种子词
    P_seed = ['很好','不错','很赞','辛苦','很快','喜欢','好评','谢谢','满意','好喝']
    N_seed = ['垃圾','太慢','凉','不行','很差','太少','差评','太晚','不好','服了']


    #依据so_pmi结果对词进行分类，并排序
    print('我知道你很急但你先别急因为我也很急')
    positive_words,negative_words = word_classfy(word_table,P_seed,N_seed,new_sentences)#new
    print('分析结束')
    print(positive_words)
    print('\n')
    print(negative_words)

    #将结果写入文件中
    write_result('./positive.txt','./negative.txt',positive_words,negative_words)
   