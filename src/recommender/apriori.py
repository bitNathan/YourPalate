from __future__ import print_function
import sys
import itertools


def apriori(dataset, min_support=0.5, verbose=False):
    """Implements the Apriori algorithm.

    The Apriori algorithm will iteratively generate new candidate
    k-itemsets using the frequent (k-1)-itemsets found in the previous
    iteration.

    Parameters
    ----------
    dataset : list
        The dataset (a list of transactions) from which to generate
        candidate itemsets.

    min_support : float
        The minimum support threshold. Defaults to 0.5.

    Returns
    -------
    F : list
        The list of frequent itemsets.

    support_data : dict
        The support data for all candidate itemsets.

    References
    ----------
    .. [1] R. Agrawal, R. Srikant, "Fast Algorithms for Mining Association
           Rules", 1994.

    """
    C1 = create_candidates(dataset)
    D = list(map(set, dataset))
    F1, support_data = get_freq(D, C1, min_support, verbose=False) # get frequent 1-itemsets
    F = [F1] # list of frequent itemsets; initialized to frequent 1-itemsets
    k = 2 # the itemset cardinality
    while k <= 5 and (len(F[k - 2]) > 0):
        Ck = apriori_gen(F[k-2], k) # generate candidate itemsets
        Fk, supK  = get_freq(D, Ck, min_support) # get frequent itemsets
        support_data.update(supK) # update the support counts to reflect pruning
        F.append(Fk)  # add the frequent k-itemsets to the list of frequent itemsets
        k += 1
        
    five_item_frequent_sets = [itemset for itemset in F[4] if len(itemset) == 5]

    # if verbose:
    #     # Print a list of all the frequent itemsets.
    #     for kset in F:
    #         for item in kset:
    #             print(""                     + "{"                     + "".join(str(i) + ", " for i in iter(item)).rstrip(', ')                     + "}"                     + ":  sup = " + str(round(support_data[item], 3)))
        
        # # Print statements for report answers
        # for i in range(2, len(F)):
        #     candidate_itemsets = apriori_gen(F[i - 2], i)
        #     print(f"Candidate itemsets C{i} (count: {len(candidate_itemsets)}): ")
        #     # for item in candidate_itemsets:
        #     #     print("{" + ", ".join(sorted(item)) + "}")
        #     print(f"".format(i) + ", ".join("{" + ", ".join(sorted(item)) + "}" for item in candidate_itemsets))
        #     print()

        # for i in range(2, len(F)+1):
        #     print(f"Frequent itemsets L{i-1} (count: {len(F[i-2])}): ")
        #     # for item in F[i-2]:
        #     #     print("{" + ", ".join(sorted(item)) + "}")
        #     print(f"".format(i-1) + ", ".join("{" + ", ".join(sorted(item)) + "}" for item in F[i - 2]))
        #     print()

    if verbose:
        print("Frequent 5-itemsets:")
        for item in five_item_frequent_sets:
            print(f"{item}: support = {support_data[item]}")
                
    return five_item_frequent_sets, support_data

def create_candidates(dataset, verbose=False):
    """Creates a list of candidate 1-itemsets from a list of transactions.

    Parameters
    ----------
    dataset : list
        The dataset (a list of transactions) from which to generate candidate
        itemsets.

    Returns
    -------
    The list of candidate itemsets (c1) passed as a frozenset (a set that is
    immutable and hashable).
    """
    c1 = [] # list of all items in the database of transactions
    for transaction in dataset:
        for item in transaction:
            if not [item] in c1:
                c1.append([item])
    c1.sort()

    if verbose:
        # Print a list of all the candidate items.
        print(""             + "{"             + "".join(str(i[0]) + ", " for i in iter(c1)).rstrip(', ')             + "}")

    # Map c1 to a frozenset because it will be the key of a dictionary.
    return list(map(frozenset, c1))

def get_freq(dataset, candidates, min_support, verbose=False):
    """

    This function separates the candidates itemsets into frequent itemset and infrequent itemsets based on the min_support,
	and returns all candidate itemsets that meet a minimum support threshold.

    Parameters
    ----------
    dataset : list
        The dataset (a list of transactions) from which to generate candidate
        itemsets.

    candidates : frozenset
        The list of candidate itemsets.

    min_support : float
        The minimum support threshold.

    Returns
    -------
    freq_list : list
        The list of frequent itemsets.

    support_data : dict
        The support data for all candidate itemsets.
    """
    support_count = {}
    
    for transaction in dataset:
        for candidate in candidates:
            if candidate.issubset(transaction):
                support_count[candidate] = support_count.get(candidate, 0) + 1
                # if candidate not in support_count:
                #     support_count[candidate] = 1
                
                # else:
                #     support_count[candidate] += 1

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
    """Generates candidate itemsets (via the F_k-1 x F_k-1 method).

    This part generates new candidate k-itemsets based on the frequent
    (k-1)-itemsets found in the previous iteration.

    The apriori_gen function performs two operations:
    (1) Generate length k candidate itemsets from length k-1 frequent itemsets
    (2) Prune candidate itemsets containing subsets of length k-1 that are infrequent

    Parameters
    ----------
    freq_sets : list
        The list of frequent (k-1)-itemsets.

    k : integer
        The cardinality of the current itemsets being evaluated.

    Returns
    -------
    candidate_list : list
        The list of candidate itemsets.
    """
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
    ''' Transfer the input to boolean type'''
    input = str(input)
    if input.lower() in ['t', '1', 'true' ]:
        return True
    elif input.lower() in ['f', '0', 'false']:
        return False
    else:
        raise ValueError('Input must be one of {T, t, 1, True, true, F, F, 0, False, false}')




if __name__ == '__main__':
    if len(sys.argv)==3:
        F, support = run_apriori(sys.argv[1], float(sys.argv[2]))
    elif len(sys.argv)==4:
        F, support = run_apriori(sys.argv[1], float(sys.argv[2]), bool_transfer(sys.argv[3]))
    else:
        raise ValueError('Usage: python apriori_templete.py <data_path> <min_support> <is_verbose>')
    print(F)
    print(support)

    '''
    Example: 
    
    python apriori_templete.py market_data_transaction.txt 0.5 
    
    python apriori_templete.py market_data_transaction.txt 0.5 True
    
    '''





