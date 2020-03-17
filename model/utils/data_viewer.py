# --------------------------------------------------------
# Visual Detection: State-of-the-Art
# Copyright: Hanbo Zhang
# Licensed under The MIT License [see LICENSE for details]
# Written by Hanbo Zhang
# --------------------------------------------------------

import numpy as np
import cv2

# Numpy data viewer to demonstrate detection results or ground truth.
class dataViewer(object):
    def __init__(self, classes):
        self.color_pool = [(255, 207, 136), (68, 187, 92), (153, 255, 0), (68, 187, 187), (0, 153, 255), (187, 68, 163),
                           (255, 119, 119), (116, 68, 187), (68, 187, 163), (163, 187, 68), (0, 204, 255), (68, 187, 140),
                           (204, 0, 255), (255, 204, 0), (102, 0, 255), (255, 0, 0), (68, 140, 187), (187, 187, 68),
                           (0, 255, 153), (119, 255, 146), (187, 163, 68), (187, 140, 68), (255, 153, 0), (255, 255, 0),
                           (153, 0, 255), (0, 255, 204), (68, 116, 187), (0, 255, 51), (187, 68, 68), (140, 187, 68),
                           (68, 163, 187), (187, 116, 68), (163, 68, 187), (204, 255, 0), (255, 0, 204), (0, 255, 255),
                           (140, 68, 187), (0, 102, 255), (153, 214, 255), (255, 102, 0)]
        self.classes = classes
        self.num_classes = len(self.classes)
        self.class_to_ind = dict(zip(self.classes, xrange(self.num_classes)))
        self.ind_to_class = dict(zip(xrange(self.num_classes), self.classes))
        self.color_dict = dict(zip(self.classes, self.color_pool[:self.num_classes]))

    def draw_single_bbox(self, img, bbox, bbox_color=(163, 68, 187), text_str="", test_bg_color = None):
        if test_bg_color is None:
            test_bg_color = bbox_color
        bbox = tuple(bbox)
        text_rd = (bbox[2], bbox[1] + 25)
        cv2.rectangle(img, bbox[0:2], bbox[2:4], bbox_color, 2)
        cv2.rectangle(img, bbox[0:2], text_rd, test_bg_color, -1)
        cv2.putText(img, text_str, (bbox[0], bbox[1] + 20),
                    cv2.FONT_HERSHEY_PLAIN,
                    2, (255, 255, 255), thickness=2)
        return img

    def draw_single_grasp(self, img, grasp, test_str=None, text_bg_color=(255, 0, 0)):
        gr_c = (int((grasp[0] + grasp[4]) / 2), int((grasp[1] + grasp[5]) / 2))
        for j in range(4):
            if j % 2 == 0:
                color = (0, 0, 255)
            else:
                color = (255, 0, 0)
            p1 = (int(grasp[2 * j]), int(grasp[2 * j + 1]))
            p2 = (int(grasp[(2 * j + 2) % 8]), int(grasp[(2 * j + 3) % 8]))
            cv2.line(img, p1, p2, color, 2)

        # put text
        if test_str is not None:
            text_len = len(test_str)
            text_w = 17 * text_len
            gtextpos = (gr_c[0] - text_w / 2, gr_c[1] + 20)
            gtext_lu = (gr_c[0] - text_w / 2, gr_c[1])
            gtext_rd = (gr_c[0] + text_w / 2, gr_c[1] + 25)
            cv2.rectangle(img, gtext_lu, gtext_rd, text_bg_color, -1)
            cv2.putText(img, test_str, gtextpos,
                        cv2.FONT_HERSHEY_PLAIN,
                        2, (255, 255, 255), thickness=2)
        return img

    def draw_graspdet(self, im, dets, g_inds=None):
        """
        :param im: original image numpy array
        :param dets: detections. size N x 8 numpy array
        :param g_inds: size N numpy array
        :return: im
        """
        # make memory contiguous
        im = np.ascontiguousarray(im)
        dets = dets[dets[:, 0] > 0].astype(np.int)
        num_grasp = dets.shape[0]
        for i in range(num_grasp):
            im = self.draw_single_grasp(im, dets[i], str(g_inds[i]) if g_inds is not None else None)
        return im

    def draw_objdet(self, im, dets, o_inds = None):
        """
        :param im: original image
        :param dets: detections. size N x 5 with 4-d bbox and 1-d class
        :return: im
        """
        # make memory contiguous
        im = np.ascontiguousarray(im)
        dets = dets[dets[:,0] > 0].astype(np.int)
        num_grasp = dets.shape[0]

        for i in range(num_grasp):
            cls = self.ind_to_class[dets[i, -1]]
            if o_inds is None:
                im = self.draw_single_bbox(im, dets[i][:4], self.color_dict[cls], cls)
            else:
                im = self.draw_single_bbox(im, dets[i][:4], self.color_dict[cls], '%s ind:%d' % (cls, o_inds[i]))
        return im

    def draw_graspdet_with_owner(self, im, o_dets, g_dets, g_inds):
        """
        :param im: original image numpy array
        :param o_dets: object detections. size N x 5 with 4-d bbox and 1-d class
        :param g_dets: grasp detections. size N x 8 numpy array
        :param g_inds: grasp indice. size N numpy array
        :return:
        """
        im = np.ascontiguousarray(im)
        o_dets = o_dets[o_dets[:,0] > 0].astype(np.int)
        g_dets = g_dets[g_dets[:,0] > 0].astype(np.int)
        o_inds = np.arange(o_dets.shape[0]) + 1
        im = self.draw_objdet(im, o_dets, o_inds)
        im = self.draw_graspdet(im, g_dets, g_inds)
        return im

    def draw_mrt(self, img):
        raise NotImplementedError