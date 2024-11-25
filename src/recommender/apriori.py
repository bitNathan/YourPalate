from __future__ import print_function
import sys
import itertools


def apriori(dataset, min_support=0.5, verbose=False):
    C1 = create_candidates(dataset)
    D = list(map(set, dataset))
    F1, support_data = get_freq(D, C1, min_support, verbose=False)
    F = [F1]
    k = 2

    while k <= 5 and (len(F[k - 2]) > 0):
        Ck = apriori_gen(F[k - 2], k)
        Fk, supK = get_freq(D, Ck, min_support)
        support_data.update(supK)
        F.append(Fk)

    five_item_frequent_sets = [itemset for itemset in F[4] if len(itemset) == 5]

    return five_item_frequent_sets, support_data


def create_candidates(dataset, verbose=False):
    c1 = []
    for transaction in dataset:
        for item in transaction:
            if not [item] in c1:
                c1.append([item])
    c1.sort()

    return list(map(frozenset, c1))


def get_freq(dataset, candidates, min_support, verbose=False):
    support_count = {}

    for transaction in dataset:
        for candidate in candidates:
            if candidate.issubset(transaction):
                support_count[candidate] = support_count.get(candidate, 0) + 1

    num_items = float(len(dataset))
    freq_list = []
    support_data = {}

    for candidate, count in support_count.items():
        support = count / num_items

        if support >= min_support:
            freq_list.append(candidate)

        support_data[candidate] = support

    return freq_list, support_data


def apriori_gen(freq_sets, k):
    candidate_list = []
    len_freq_sets = len(freq_sets)
    print(len_freq_sets)
    for i in range(len_freq_sets):
        for j in range(i + 1, len_freq_sets):
            L1 = list(freq_sets[i])[: k - 2]
            L2 = list(freq_sets[j])[: k - 2]

            if L1 == L2:
                candidate = freq_sets[i] | freq_sets[j]
                valid_candidate = True

                for subset in itertools.combinations(candidate, k - 1):
                    if frozenset(subset) not in freq_sets:
                        valid_candidate = False
                        break

                if valid_candidate:
                    candidate_list.append(candidate)

    return candidate_list


def loadDataSet(fileName, delim=','):
    fr = open(fileName)
    stringArr = [line.strip().split(delim) for line in fr.readlines()]
    return stringArr


def run_apriori(data_path, min_support, verbose=False):
    dataset = loadDataSet(data_path)
    F, support = apriori(dataset, min_support=min_support, verbose=verbose)
    return F, support


def bool_transfer(input):
    input = str(input)
    if input.lower() in ['t', '1', 'true']:
        return True
    elif input.lower() in ['f', '0', 'false']:
        return False
    else:
        raise ValueError('Input must be one of {T, t, 1, True, true, F, F, 0, False, false}')


if __name__ == '__main__':
    if len(sys.argv) == 3:
        F, support = run_apriori(sys.argv[1], float(sys.argv[2]))
    elif len(sys.argv) == 4:
        F, support = run_apriori(sys.argv[1], float(sys.argv[2]), bool_transfer(sys.argv[3]))
    else:
        raise ValueError('Usage: python apriori_templete.py <data_path> <min_support> <is_verbose>')
    print(F)
    print(support)
