import os
import numpy as np
import collections
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from shapely.validation import make_valid
import sys

#LMI packages
from label_utils import csv_utils,rect,mask


def bbox_iou(bbox1, bbox2):
    """
    calculate the iou between bbox1 and bbox2
    arguments:
        bbox1: an array of size [N,4]
        bbox2: an array of size [M,4]
    return:
        iou of size [N,M]
    """
    if not isinstance(bbox1, np.ndarray):
        bbox1 = np.array(bbox1)
    if not isinstance(bbox2, np.ndarray):
        bbox2 = np.array(bbox2)
    xmin1, ymin1, xmax1, ymax1, = np.split(bbox1, 4, axis=-1)
    xmin2, ymin2, xmax2, ymax2, = np.split(bbox2, 4, axis=-1)
    
    area1 = (xmax1 - xmin1) * (ymax1 - ymin1)
    area2 = (xmax2 - xmin2) * (ymax2 - ymin2)
    
    ymin = np.maximum(ymin1, np.squeeze(ymin2, axis=-1))
    xmin = np.maximum(xmin1, np.squeeze(xmin2, axis=-1))
    ymax = np.minimum(ymax1, np.squeeze(ymax2, axis=-1))
    xmax = np.minimum(xmax1, np.squeeze(xmax2, axis=-1))
    
    h = np.maximum(ymax - ymin, 0)
    w = np.maximum(xmax - xmin, 0)
    intersect = h * w
    
    union = area1 + np.squeeze(area2, axis=-1) - intersect
    return intersect / union


def polygon_iou(polygon_1, polygon_2):
    """
    caluclate the IOU between two plygons
    Arugments:
        polygon_1: [[row1, col1], [row2, col2], ...]
        polygon_2: same as polygon_1
    return:
        IOU
    """
    try:
        poly_1 = Polygon(polygon_1)
        poly_2 = Polygon(polygon_2)
    except Exception as e:
        #usually less than 3 points for creating the polygons
        #print(e)
        return 0

    if not poly_1.is_valid:
        poly_1 = make_valid(poly_1)
    if not poly_2.is_valid:
        poly_2 = make_valid(poly_2)

    iou = poly_1.intersection(poly_2).area / poly_1.union(poly_2).area
    return iou


def polygon_ious(polygons_1, polygons_2):
    N,M = len(polygons_1), len(polygons_2)
    ious = np.zeros((N,M))
    for i in range(N):
        for j in range(M):
            ious[i][j] = polygon_iou(polygons_1[i],polygons_2[j])
    return ious


def precision_recall(label_dt:dict, pred_dt:dict, class_map:dict, threshold_iou=0.5, threshold_conf=0.1, skip_classes=[], image_level=False):
    """
    calculate the precision and recall based on the threshold of iou and confidence
    arguments:
        label_dt: the map <fname, list of Shapes> from label annotations
        pred_dt: the map <fname, list of Shapes> from prediction
        class_map: the map <class, class id>
        threshold_iou: iou threshold, default=0.5
        threshold_conf: confidence threshold, default=0.1
    return:
        P: the map <class: class's precision>
        R: the map <class: class's recall>
    """

    def mask_to_np(shapes):
        masks = []
        for shape in shapes:
            cur = np.empty((0,2))
            if not isinstance(shape, mask.Mask):
                continue
            for x,y in zip(shape.X,shape.Y):
                cur = np.concatenate((cur,[[x,y]]),axis=0)
            masks.append(cur)
        return masks
    
    def bboxs_to_np(bboxs):
        def bbox_to_pts(bbox):
            x1,y1,x2,y2 = bbox
            return np.array([[x1,y1],[x2,y1],[x2,y2],[x1,y2]])
        masks = []
        for bbox in bboxs:
            masks.append(bbox_to_pts(bbox))
        return masks
    
    # get TP (num of tp), FP(num of fp) and GT(num of ground truth)
    TP,FP,GT,FN = collections.defaultdict(int),collections.defaultdict(int),collections.defaultdict(int),collections.defaultdict(int)
    TP_im,FP_im,GT_im,FN_im = collections.defaultdict(int),collections.defaultdict(int),collections.defaultdict(int),collections.defaultdict(int)
    
    fnames = set([f for f in label_dt]+[f for f in pred_dt])
    total_imgs = len(fnames)
    cnt = 0
    for fname in fnames:
        # bbox: [x1,y1,x2,y2]
        bbox_label = np.array([shape.up_left+shape.bottom_right for shape in label_dt[fname] if isinstance(shape, rect.Rect) ])
        class_label = np.array([shape.category for shape in label_dt[fname] if isinstance(shape, rect.Rect) ])
        # mask: [[x1,y1],[x2,y2] ...]
        mask_pred = np.array(mask_to_np(pred_dt[fname]),np.object)
        conf = np.array([shape.confidence for shape in pred_dt[fname] if isinstance(shape, mask.Mask) ])
        class_pred = np.array([shape.category for shape in pred_dt[fname] if isinstance(shape, mask.Mask) ])
        if len(mask_pred):
            # found masks
            is_mask = 1
            # convert label bbox to masks
            mask_label = np.array(mask_to_np(label_dt[fname]) + bboxs_to_np(bbox_label),np.object)
            mask_class_label = np.array([shape.category for shape in label_dt[fname] if isinstance(shape, mask.Mask) ])
            class_label = np.concatenate((mask_class_label,class_label))
        else:
            is_mask = 0
            bbox_pred = np.array([shape.up_left+shape.bottom_right for shape in pred_dt[fname] if isinstance(shape, rect.Rect) ])
            class_pred = np.array([shape.category for shape in pred_dt[fname] if isinstance(shape, rect.Rect) ])
            conf = np.array([shape.confidence for shape in pred_dt[fname] if isinstance(shape, rect.Rect) ])
            

        #found GT but no predictions
        if class_label.shape[0] and not class_pred.shape[0]:
            cnt += 1

        #gather FP, TP and GT
        all_classes = np.concatenate((class_label, class_pred), axis=0)
        for c in set(all_classes):
            m_label = np.empty((0,))
            if class_label.shape[0]:
                m_label = class_label==c    
                
            m_pred = np.empty((0,))
            if class_pred.shape[0]:
                m_pred = np.logical_and(class_pred == c, conf >= threshold_conf)

            #update GT
            GT_im[c] += 1 if m_label.sum() else 0
            GT[c] += m_label.sum()

            # no GT labels
            if not m_label.sum():
                if m_pred.sum():
                    FP_im[c] += 1
                    FP[c] += m_pred.sum()

            # not found any bbox found
            if not m_pred.sum():
                if m_label.sum():
                    FN_im[c] += 1
                    FN[c] += m_label.sum()

            if not m_label.sum() or not m_pred.sum():
                continue

            if is_mask:
                ious = polygon_ious(mask_pred[m_pred], mask_label[m_label])
            else:
                ious = bbox_iou(bbox_pred[m_pred,:], bbox_label[m_label,:])
            M = np.max(ious, axis=1) >= threshold_iou
            N = np.max(ious, axis=0) < threshold_iou

            if N.sum():
                FN_im[c] += 1
                FN[c] += N.sum()

            if M.sum():
                TP_im[c] += 1
            else:
                FP_im[c] += 1 
            TP[c] += M.sum()
            FP[c] += (~M).sum()

    print(f'threshold_iou: {threshold_iou}, threshold_conf: {threshold_conf}')
    #calcualte precision and recall
    epsilon=1e-16
    P,R = {},{}
    Err = {} #image level results
    total_tp, total_fp, total_gt = 0,0,0
    for c in class_map:
        if c in skip_classes:
            continue
        if image_level:
            tp,fp,gt,fn = TP_im[c],FP_im[c],GT_im[c],FN_im[c]
        else:
            tp,fp,gt,fn = TP[c],FP[c],GT[c],FN[c]
        
        P[c] = min(1, tp / (tp + fp + epsilon))
        R[c] = min(1, tp / (gt + epsilon))
        Err[c] = FN_im[c]/total_imgs
        print(f'class {c}: ', f'error rate: {Err[c]:.4f}, ', f'precision: {P[c]:.4f}, ', f'recall: {R[c]:.4f}')

        total_tp += tp
        total_fp += fp
        total_gt += gt
    P['all'] = min(1, total_tp / (total_tp + total_fp + epsilon))
    R['all'] = min(1, total_tp / (total_gt + epsilon))
    print('')
    return P,R,Err


def plot_curve(px, dt_y, save_dir='my_curve.png', xlabel='Confidence', ylabel='Metric', y_range=[0, 1.1], step=0.1, threshold_iou=0.5):
    # Metric-confidence curve
    fig, ax = plt.subplots(1, 1, figsize=(9, 6), tight_layout=True)

    for k in dt_y:
        if k=='all':
            ax.plot(px, dt_y['all'], linewidth=3, color='blue', label=f'all classes @ iou_threshold={threshold_iou}')
        else:
            ax.plot(px, dt_y[k], linewidth=1, label=f'{k}')  # plot(confidence, metric)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_xlim(0, 1)
    ax.set_ylim(*y_range)
    ax.set_yticks(np.arange(*y_range, step=step))
    plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left")
    fig.savefig(save_dir, dpi=250)
    plt.close()


if __name__ == '__main__':
    import argparse
    parse = argparse.ArgumentParser()
    parse.add_argument('--model_csv', required=True, help='the path to the model prediction csv')
    parse.add_argument('--label_csv', required=True, help='the path to the ground truth csv')
    parse.add_argument('--path_out', required=True, help='the output path for storing Precision and Recall figures')
    parse.add_argument('--skip_classes', default='', help='skip calculating the P/R curves for these comma separated classes')
    parse.add_argument('--threshold_iou', type=float, default=0.5, help='[optional] the iou threshold, default=0.5')
    parse.add_argument('--image_level', action='store_true', help='[optional] calculate the precision and recall on image level')
    args = vars(parse.parse_args())

    threshold_iou = args['threshold_iou']
    model_csv = args['model_csv']
    label_csv = args['label_csv']
    out_path = args['path_out']
    image_level = args['image_level']
    skip_classes = args['skip_classes']
    if skip_classes=='':
        skip_classes = []
    else:
        skip_classes = skip_classes.split(',')

    if not os.path.isfile(model_csv):
        raise Exception(f'Not found the "preds.csv" in {os.path.dirname(model_csv)}')

    if not os.path.isfile(label_csv):
        raise Exception(f'Not found the "labels.csv" in {os.path.dirname(label_csv)}')

    label_dt,class_map = csv_utils.load_csv(label_csv)
    print(f'found class map: {class_map}')
    pred_dt,_ = csv_utils.load_csv(model_csv, class_map=class_map)
    X = np.linspace(0,1,num=20)
    print(f'confidence levels:\n {X}')

    Ps,Rs = collections.defaultdict(list),collections.defaultdict(list)
    Errs = collections.defaultdict(list)
    for conf in X:
        P,R,err = precision_recall(label_dt,pred_dt,class_map,threshold_iou,conf,skip_classes,image_level)
        for c in P:
            Ps[c].append(P[c])
        for c in R:
            Rs[c].append(R[c])
        for c in err:
            Errs[c].append(err[c]*100)

    postfix = ''
    if image_level:
        postfix = '_im_level'
    plot_curve(X, Ps, save_dir=os.path.join(out_path,'precision'+postfix+'.png'), ylabel='Precision', threshold_iou=threshold_iou, step=0.05)
    plot_curve(X, Rs, save_dir=os.path.join(out_path,'recall'+postfix+'.png'), ylabel='Recall', threshold_iou=threshold_iou, step=0.05)
    #plot_curve(X, Errs, save_dir=os.path.join(out_path,'error_rate_im_level.png'), ylabel='Error Rate (%) on image level', threshold_iou=threshold_iou, y_range=[0,20.1], step=1)
    print(f'Precision and Recall figures are saved in {out_path}')
