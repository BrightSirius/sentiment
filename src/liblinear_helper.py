#encoding=utf-8 
#!/usr/bin/env python 
import sys, os
import json, logging, time, copy, random, math

from const import TAG2INDEX
from easy_tool import EasyTool as ET
from stats_tool import StatsTool as ST
reload(sys)
sys.setdefaultencoding('utf-8')


linfo = logging.info
ldebug = logging.debug

#optimize: svm L2RL2L_Dual with unigram and bigram mixed. precision 74.8151

class LinearModelInputHelper(object):

    def __init__(self, ct):
        self._path = '../train_data/%s_train_data' % ct
        if ct not in ['bi', 'tri']:
            raise Exception('INVALID Classifier Type')
        self.classifier_type = ct
        self.tag2index = TAG2INDEX
        self._train_xs, self._train_ys = ST.load_data(self._path)
        self._train_ys = map(lambda x: self.tag2index[x], self._train_ys)

        self._feature_extract_config = ['unigram', 'bigram']
        linfo('feature extract config: %s' % self._feature_extract_config)
        linfo('classifier type %s' % ct)

    def test(self, emoticon=True):
        test_path='../test_data/%s_test_data' % self.classifier_type
        self._test_xs, self._test_ys = ST.load_data(test_path)
        self._test_ys = map(lambda x:self.tag2index[x], self._test_ys)
        if not emoticon:
            ST.remove_emoticon(self._train_xs)
        self.format_sparse(self._test_xs, self._test_ys, '../test_data/%s_sparse_test_data_%s' % (self.classifier_type, 'icon' if emoticon else 'no_icon'))

    def train(self, emoticon=True):
        if not emoticon:
            ST.remove_emoticon(self._train_xs)
        self.format_sparse(self._train_xs, self._train_ys, '../train_data/%s_sparse_train_data_uni_bi_%s' % (self.classifier_type, 'icon' if emoticon else 'no_icon'))

    def format_sparse(self,_xs, _ys, out_path):
        if os.path.exists(out_path):
            os.system('rm %s' % out_path)
        w2id = self._extract_feature()
        for txt, tag in zip(_xs, _ys):
            bags = ST.retrieve_feature(txt, feature_extract_config=self._feature_extract_config)
            wids = [w2id[w] for w in bags if w in w2id]
            wids = set(wids)
            wids = sorted([x for x in wids])
            features = ['%s:%s' % (wid, 1) for wid in wids]
            line = '%s %s' % (tag, ' '.join(features))
            ET.write_file(out_path, 'a', '%s\n' % line)

    def _extract_feature(self, word2cnt_path=None, cnt_threshold=10):
        w2id = {} 
        w2cnt = {}
        for txt in self._train_xs:
            bags = ST.retrieve_feature(txt, feature_extract_config=self._feature_extract_config)
            for w in bags:
                w2cnt.setdefault(w, 0)
                w2cnt[w] += 1
                if w not in w2id:
                    w2id[w] = len(w2id) + 1
        if word2cnt_path:
            if os.path.exists(word2cnt_path):
                os.system('rm %s' % word2cnt_path)
            words = sorted(w2cnt.keys(), key=lambda x: w2cnt[x], reverse=True)
            for w in words:
                cnt = w2cnt[w]
                ET.write_file(word2cnt_path, 'a', '%s %s\n' % (w, cnt))
        #w2id = {w:d for w, d in w2id.items() if w2cnt[w] >= cnt_threshold}
        linfo('gram cnt: %s' % len(w2id))
        return w2id

    def debug(self):
        ws_1 = set(self._extract_feature().keys())
        ST.remove_emoticon(self._train_xs)
        ws_2 = set(self._extract_feature().keys())
        linfo('uni_bi_icon_feature_cnt: %s. no_icon: %s' % (len(ws_1), len(ws_2)))
        rms =  ws_2 - ws_1
        for x in rms:
            print x
        #linfo(ws_1 - ws_2)

def main():
    #print dir(WorkClassifier)
    obj = LinearModelInputHelper('tri')
    #obj._extract_feature()
    #obj.debug()
    #obj.train(emoticon=False)
    obj.test(emoticon=False)
    
    
if __name__ == '__main__':
    logging.basicConfig(filename='/home/lizhitao/log/sentiment.log',format='%(asctime)s %(levelname)s %(message)s',level=logging.INFO)
    logging.info('---------------------------\nbegin supervise classifier')
    main()
    logging.info('end')