import torch
from torch import nn
import torch.nn.functional as F

from utils.config import cfg
from utils.net_utils import set_bn_fix, set_bn_eval

import abc

from basenet.resnet import resnet_initializer

class objectDetector(nn.Module):
    __metaclass__ = abc.ABCMeta
    def __init__(self, classes, class_agnostic,
                 feat_name = 'res101', feat_list = ('conv4',), pretrained = True):
        super(objectDetector, self).__init__()

        self.classes = classes
        self.n_classes = len(classes)
        self.class_agnostic = class_agnostic

        self.feat_name = feat_name
        self.feat_list = feat_list
        self.pretrained = pretrained

        self.feat_extractor = self._init_feature_extractor()

    def _init_feature_extractor(self):
        # init resnet feature extractor
        if self.feat_name in {'res18', 'res34', 'res50', 'res101', 'res152'}:
            return resnet_initializer(self.feat_name, self.feat_list, self.pretrained)
        elif self.feat_name in {'vgg11', 'vgg13', 'vgg16', 'vgg19'}:
            pass

    def _init_modules(self):

        # Fix blocks
        for p in self.feat_extractor.feat_layer["conv1"].parameters(): p.requires_grad = False

        assert (0 <= cfg.RESNET.FIXED_BLOCKS < 4)
        if cfg.RESNET.FIXED_BLOCKS >= 3:
            for p in self.feat_extractor.feat_layer["conv4"].parameters(): p.requires_grad = False
        if cfg.RESNET.FIXED_BLOCKS >= 2:
            for p in self.feat_extractor.feat_layer["conv3"].parameters(): p.requires_grad = False
        if cfg.RESNET.FIXED_BLOCKS >= 1:
            for p in self.feat_extractor.feat_layer["conv2"].parameters(): p.requires_grad = False

        for k in self.feat_extractor.feat_layer.keys():
            self.feat_extractor.feat_layer[k].apply(set_bn_fix)

    def train(self, mode = True):
        # Override train so that the training mode is set as we want
        nn.Module.train(self, mode)
        if mode:
            self.feat_extractor.train()

            # Set fixed blocks to be in eval mode
            self.feat_extractor.feat_layer["conv1"].eval()
            if cfg.RESNET.FIXED_BLOCKS >= 1:
                self.feat_extractor.feat_layer["conv2"].eval()
            if cfg.RESNET.FIXED_BLOCKS >= 2:
                self.feat_extractor.feat_layer["conv3"].eval()
            if cfg.RESNET.FIXED_BLOCKS >= 3:
                self.feat_extractor.feat_layer["conv4"].eval()

            for k in self.feat_extractor.feat_layer.keys():
                self.feat_extractor.feat_layer[k].apply(set_bn_eval)