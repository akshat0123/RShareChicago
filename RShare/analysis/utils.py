import numpy as np


def scale(data):

    min_ = np.min(data) 
    max_ = np.max(data)
    data = (data - min_) / (max_ - min_)
    return data


def combine_columns(data, header, col1, col2):

    c1i = np.argwhere(header == col1)[0, 0]
    c2i = np.argwhere(header == col2)[0, 0]
    c1perc = np.nan_to_num(data[:, c1i] / (data[:, c1i] + data[:, c2i]))
    c1perc = c1perc.reshape((c1perc.shape[0], 1))
    data = np.concatenate([data, c1perc], axis=1)
    header = np.concatenate([header, ['%s Percentage' % (col1)]])
    data = np.delete(data, [c1i, c2i], axis=1)
    header = np.delete(header, [c1i, c2i])

    return data, header 


def calc_percent_rule(x, y, header, col, minp, maxp):

    cidx = np.argwhere(header == col)[0, 0]
    rows = np.argwhere((x[:, cidx] >= minp) & (x[:, cidx] < maxp))
    y = y[rows].flatten()

    return y


def effect_size(y, y1, y2):

    y1mn = np.mean(y1)
    y2mn = np.mean(y2)
    ystd = np.std(y)

    return (y1mn - y2mn) / ystd


