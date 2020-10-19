from scipy.stats import linregress
import numpy as np


DATAPATH = '../data/german_clean.csv'


def di_80(header, data, target, att, t_pos, att_maj):

    tidx = np.argwhere(header==target)[0, 0]
    aidx = np.argwhere(header==att)[0, 0]
    att_min = 0 if att_maj == 1 else 1

    amin_cnt = (np.argwhere(data[:, aidx]==att_min).flatten()).shape[0]
    amin_tpos_cnt = (np.argwhere((data[:, aidx]==att_min) & (data[:, tidx]==t_pos)).flatten()).shape[0]

    amaj_cnt = (np.argwhere(data[:, aidx]==att_maj).flatten()).shape[0]
    amaj_tpos_cnt = (np.argwhere((data[:, aidx]==att_maj) & (data[:, tidx]==t_pos)).flatten()).shape[0]

    di = (amin_tpos_cnt / amin_cnt) / (amaj_tpos_cnt / amaj_cnt)
    return di


def di_sp(header, data, target, att):

    tidx = np.argwhere(header==target)[0, 0]
    aidx = np.argwhere(header==att)[0, 0]
    att_min, att_maj = 0, 1

    y_att_maj = np.sum(data[np.argwhere(data[:, aidx]==att_maj).flatten(), tidx])
    att_maj_t = (np.argwhere(data[:, aidx]==att_maj).flatten()).shape[0]
    a1 = y_att_maj/att_maj_t

    y_att_min = np.sum(data[np.argwhere(data[:, aidx]==att_min).flatten(), tidx])
    att_min_t = (np.argwhere(data[:, aidx]==att_min).flatten()).shape[0]
    a2 = y_att_min/att_min_t

    di = np.abs(a1 - a2)
    return di


def main():

    header = np.loadtxt(DATAPATH, delimiter=',', dtype=str, max_rows=1)
    data = np.loadtxt(DATAPATH, delimiter=',', skiprows=1)

    header, data = header[1:], data[:, 1:]
    target, t_pos = 'Score', 1

    tidx = np.argwhere(header=='Score')[0, 0]
    data[np.argwhere(data[:, tidx]==1), tidx] = 0
    data[np.argwhere(data[:, tidx]==2), tidx] = 1

    att = 'Young/Old'
    att_maj = 1

    aidx = np.argwhere(header==att)[0, 0]
    st_y = np.std(data[:, aidx])

    di80 = di_80(header, data, target, att, t_pos, att_maj)
    disp = di_sp(header, data, target, att)

    att = 'Age in years'
    aidx = np.argwhere(header==att)[0, 0]
    data = data[np.argsort(data[:, aidx])]

    eslist, var_ds = [], []
    std = np.std(data[:, tidx])
    for ridx in range(1, data.shape[0]-1):
        nrval = np.mean(data[ridx:, tidx])
        rval = np.mean(data[:ridx, tidx])
        d = (rval - nrval) / std
        eslist.append(d)

        n1, n2 = ridx, data.shape[0]-ridx

        var_d = (
            (
                ( (n1 + n2) / (n1 * n2) ) +
                ( (d**2) / (2 * (n1 + n2 - 2)) )
            ) * (
                (n1 + n2) / (n1 + n2 - 2)
            )
        )

        var_ds.append(var_d)

    eslist = np.asarray(eslist)
    var_ds = np.asarray(var_ds)
    var_all = np.var(eslist)
    var = var_ds + var_all

    slope, intercept, r_value, p_value, std_err = linregress(
        np.arange(len(eslist)),
        eslist
    )
    slope = '+' if slope >= 0 else '-'

    es = (np.sum(eslist * (var)) / np.sum(var)) / 2

    if di80 > 1: di80 = 1/di80
    di80 = 1-di80

    print('German Credit & %.2f & %.2f & %.2f \\\\' % (di80, disp, es))


if __name__ == '__main__':
    main()
