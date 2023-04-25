import os

from numpy import std


# import distance_score


# print std([1,2,3,4])

# Manhattan scaled
def Dfeat(test, profile):
    mprof = sum(profile) * 1.0 / len(profile)  # find mean
    stdprof = max(10, std(profile))  # find max in std of profile
    # print [abs(i-mprof)*1.0/stdprof for i in test]
    return sum(abs(i - mprof) * 1.0 / stdprof for i in test), len(
        test)  # absolute value of the difference btw each test diagraph and profile mean diagraph and divide by std


def Dfeat2(test, profile):
    s, c = 0, 0
    for i in test:
        if i in profile:
            r = Dfeat(test[i], profile[i])
            s += r[0]
            c += r[1]
    if c == 0:
        return 10
    return s * 1.0 / c  # more like finding the mean of all the scores


# print Dfeat([2,3],[1,2,3,4])

def picardi(test, profile):
    test = [(i, sum(test[i]) * 1.0 / len(test[i])) for i in test]
    profile = [(i, sum(profile[i]) * 1.0 / len(profile[i])) for i in profile]
    result = distance_score.a_measure(test, profile) + distance_score.r_measure(test, profile)
    return result / 2


def test(alg='Dfeat2'):
    # use 'p' for picardi's algorithm, otherwise manhattan distance
    alias = {}
    users = set()
    profile = {}
    gen = {}
    attack = {}
    for root, dirs, files in os.walk('new'):
        users = list(files)
        for file in files:

            f = open(os.path.join(root, file))

            for line in f:
                s = line[0]
                # if s != 'R':
                # continue
                line = line.split('\t')[1:]
                ids = []
                time = []
                r = []
                for i in line:
                    i = i.split(':')
                    if i[-1].endswith('Id') and i[1] == '0':
                        kn = i[0][1:-1]
                        if len(kn) == 1:

                            ids.append(kn)
                        elif kn == 'Backspace' and r:
                            r.pop()
                    # if i[-1].endswith('Id') and i[1]=='0':
                    if (i[-1].startswith('declare') or i[-1].endswith('name') or i[-1].endswith('mail')) and i[
                        1] == '0':
                        # if i[1]=='0':
                        kn = i[0][1:-1]
                        ts = int(i[2])
                        if len(kn) == 1:
                            r.append(kn)
                            time.append(ts)

                # print typed output
                print(''.join(r))

                ids = ''.join(ids).upper()
                if '-' not in ids:
                    ids = ids[:-5] + '-' + ids[-5:]
                ids = ids.replace('O', '0')
                digraph = {}
                dg = [r[i] + r[i + 1] for i in range(len(r) - 1)]
                td = [int(time[i + 1] - time[i]) for i in range(len(time) - 1)]
                for i in range(len(dg)):
                    if td[i] <= 500:
                        digraph.setdefault(dg[i], [])
                        digraph[dg[i]].append(td[i])
                if not digraph: continue
                if s == 'R':
                    profile.setdefault(file, {})
                    for i in digraph:
                        profile[file].setdefault(i, [])
                        profile[file][i] += digraph[i]
                elif s == 'F':
                    gen.setdefault(file, [])
                    gen[file].append(digraph)
                elif s == 'A':
                    if ids[-5:] != file[-5:]:
                        # if ids not in profile:
                        # print ids, file, list(profile)
                        attack.setdefault(ids[-11:], [])
                        attack[ids[-11:]].append(digraph)
    # print profile
    # print attack

    # print ids, file
    # for i in line:

    # picardi2(profile, test)
    gscore = []
    ascore = []
    for user in profile:
        if user in gen:
            for t in gen[user]:
                if alg == 'p':
                    r = picardi(t, profile[user])
                else:
                    r = Dfeat2(t, profile[user])

                gscore.append(r)
        if user in attack:
            for t in attack[user]:
                if alg == 'p':
                    r = picardi(t, profile[user])
                else:
                    r = Dfeat2(t, profile[user])
                ascore.append(r)
        else:
            print(user, [i for i in attack])

    print('gscore', len(gscore))
    print('ascore', len(ascore))
    print(sum(gscore) / len(gscore))
    print(sum(ascore) / len(ascore))
    for t in range(40):
        if alg == 'p':

            th = 00.2 * t / 10
            # print 'alg =o= p', th,t, 0.02*t
        else:
            th = 0.2 * t
        # print 'th', th, alg
        frr = sum([1 for i in gscore if i > th]) * 1.0 / len(gscore)
        far = sum([1 for i in ascore if i < th]) * 1.0 / len(ascore)
        print('%.4f\t%.4f' % (frr, far))


test('p')
