A_MEASURE_THRESHOLD = 1.25


def a_measure(lis2, lis1):
    """
    input are two lists, each element of a list is a (ngraph, average_time) tuple
    return difference score, a list of the n-graphs that are not similar, and a list of the n-graphs that are similar
    """
    dic2 = {}  # transform lis2 into dic2
    for pair in lis2:
        dic2[pair[0]] = pair[1]
    result_file = open('result.txt', 'a')
    pairs = [(i[0], i[1], dic2[i[0]]) for i in lis1 if i[0] in dic2]  # (ngraph, lis1_time, lis2_time)
    pro = sum([i[1] for i in pairs])
    tes = sum([i[2] for i in pairs])
    print >> result_file, pairs

    diff = [True for i in pairs if max(i[1:]) * 1.0 / min(i[1:]) > A_MEASURE_THRESHOLD]
    # diff = [True for i in pairs if max(i[1:])-min(i[1:])>60]
    speed = (1 - min([tes, pro]) / max([tes, pro])) * 3
    if pairs:
        return [len(diff) * 1.0 / len(pairs), speed]
        # return len(diff)*1.0/len(pairs), [i[0] for i in pairs if max(i[1:])-min(i[1:])>60], [i[0] for i in pairs if max(i[1:])-min(i[1:])<=60]
    else:
        return [-1, speed]


def handle_r_measure(test_ngraphs, profile_ngraphs, result):
    """
    test_ngraphs and profile_ngraphs are lists. Length is number of different kinds of n-graph used.
    e.g. if only digraphs or trigraphs are used, list length is 1,
    each element in test_ngraphs is a list of individual n-graphs.
    """

    for i in range(len(test_ngraphs)):
        dis_score = r_measure(test_ngraphs[i], profile_ngraphs[i])
        if dis_score != -1:
            result.append(dis_score)
        else:
            result.append(1)
    return result


def handle_a_measure(test_ngraphs, profile_ngraphs, result):
    """
    test_ngraphs and profile_ngraphs are lists. Length is number of different kinds of n-graph used.
    e.g. if only digraphs or trigraphs are used, list length is 1,
    each element in test_ngraphs is a list of individual n-graphs.
    """

    for i in range(len(test_ngraphs)):
        dis_score = a_measure(test_ngraphs[i], profile_ngraphs[i])
        # print 'a_measure', dis_score
        if dis_score[0] != -1:
            result = result + dis_score
        else:
            result = result + [1, dis_score[1]]
    return result


def r_measure(di1, di2):
    """
    calculate the difference distance between two ngraph lists,
    for difference score, 0 if they are the same, 1 if as different as possible
    """
    di1 = sorted(di1, key=lambda x: x[1])
    di2 = sorted(di2, key=lambda x: x[1])
    di1 = [i[0] for i in di1]
    di2 = [i[0] for i in di2]
    di2 = [i for i in di2 if i in set(di1)]
    di1 = [i for i in di1 if i in set(di2)]
    di2dic = {}
    count = 0
    for object in di2:
        di2dic[object] = count
        count += 1
    count = 0
    total = 0
    for i in di1:
        total += abs(count - di2dic[i])
        count += 1
    max_diff = len(di1) ** 2 / 2
    if max_diff:
        return total * 1.0 / max_diff


def sep_ngraph(lis):
    """
    input a list of ngraphs, return the result having digraphs and trigraphs seperated
    """
    digraphs = [t for t in lis if len(t[0]) == 2]
    trigraphs = [t for t in lis if len(t[0]) == 3]
    return digraphs, trigraphs
