from math import sqrt

import numpy as np


def parse(keystrokes):
    k = [i for i in keystrokes if i[2] == 0]
    dic = {}
    for i in range(len(k) - 1):
        digraph = str(k[i][1] + k[i + 1][1])
        if 'Backspace' in digraph: continue
        time_diff = k[i + 1][0] - k[i][0]
        if 30 <= time_diff <= 500:
            dic.setdefault(digraph, [])
            dic[digraph].append(time_diff)
    dic2 = []
    # for i in dic:
    #     dic2.append((i, sum(dic[i]) * 1.0 / len(dic[i])))
    for i in dic:
        if len(dic[i]) >= 4:
            mean = sum(dic[i]) * 1.0 / len(dic[i])
            std = sqrt(sum((x - mean) ** 2 for x in dic[i]) / len(dic[i]))
            dic2.append((i, mean, std))
    return dic2


def parseTest(keystrokes):
    k = [i for i in keystrokes if i[2] == 0]
    dic = {}
    for i in range(len(k) - 1):
        digraph = str(k[i][1] + k[i + 1][1])
        if 'Backspace' in digraph: continue
        time_diff = k[i + 1][0] - k[i][0]
        if 30 <= time_diff <= 500:
            dic.setdefault(digraph, [])
            dic[digraph].append(time_diff)
    return dic


def manhattan(profile_sample, test_sample):
    K = 0.7
    profile_sample = parse(profile_sample)
    test_sample = parseTest(test_sample)
    # if (len(profile_sample) * K) > len([i[0] for i in profile_sample if i[0] in test_sample]):
    #     print('Failed to meet K requirement')
    #     return -1, 0
    print('Test: ', test_sample)
    # print(f'TEST: ', test_sample)
    return ManhattanScore(profile_sample, test_sample)


def ManhattanScore(profileKeys, testKeys):
    s, c, sharedDigraph = 0, 0, 0
    # xxProfile, xxTest = [], []
    for i in profileKeys:
        if i[0] in testKeys:
            sharedDigraph += 1
            # xxProfile.append(i[1])
            # xx = []
            for j in testKeys[i[0]]:
                if i[2] != 0.0:
                    c += 1
                    s += abs(i[1] - j) * 1.0 / i[2]
                    # xx.append(j)
            # xxTest.append(np.mean(xx))
    # print('xxProfile is: ', xxProfile)
    # print('xxTest is: ', xxTest)
    if s != 0 and c != 0:
        print('Score: ', s / c)
        return s / c, c
    else:
        return -1, c
    # s, c = 0, 0
    # # print(f'Profile Keys: ', profileKeys)
    # # print(f'Attack Keys: ', testKeys)
    # for i in profileKeys:
    #     if i[0] in testKeys:
    #         # print(f'Manhattan: ', i[1], trueKeys[i[0]])
    #         for j in testKeys[i[0]]:
    #             # print(f'Manhattan: ', i[0], i[1], testKeys[i[0]], abs(i[1] - j))
    #             if i[2] != 0.0:
    #                 c += 1
    #                 s += abs(i[1] - j) * 1.0 / i[2]
    # print(f'TOTAL S is: ', s)
    # print(f'C is: ', c)
    # if c == 0:
    #     score = 100
    # else:
    #     score = s / c
    # print(f'Score: ', score)
    # return score, c


def Dfeat3(test, profile):
    s, c = 0, 0
    # print(f'TEST is: ', test)
    # print(f'PROFILE is: ', profile)
    dic2 = {}
    for pair in test:
        dic2[pair[0]] = pair[1]
    pairs = []
    for i in profile:
        if i[0] in dic2:
            pairs.append([i[0], abs(i[1] - dic2[i[0]]), i[2]])
            if i[2] != 0.0:
                c += 1
                s += np.abs(i[1] - dic2[i[0]]) * 1.0 / i[2]
                # print(f'S is: ', s)
    print(f'TEST PAIR', pairs)
    if c == 0:
        return 10
    print(f'TOTAL S is: ', s)
    print(f'C is: ', c)
    print(f'SCORE is: ', str(round(s * 1.0 / 100, 3)))
    return s * 1.0 / 100  # more like finding the mean of all the scores
