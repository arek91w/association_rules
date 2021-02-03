from itertools import combinations
from more_itertools import set_partitions
from operator import itemgetter
from tabulate import tabulate


def create_dataset(path: str):
    data = []
    file = open(path, "r")
    for line in file:
        data.append(line.split())
    file.close()
    return data


def self_join(iterable):
    result = []
    copy = iterable.copy()
    k = len(copy[0])
    while len(copy) >= 2:
        matches_indices = [index for index, itemset in enumerate(copy) if itemset[:k - 1] == copy[0][:k - 1]]
        remaining_matches_indices = matches_indices.copy()
        while len(remaining_matches_indices) >= 2:
            base_index = remaining_matches_indices[0]
            for i in remaining_matches_indices[1:]:
                superset = (*copy[base_index], copy[i][k - 1])
                result.append(superset)
            remaining_matches_indices.pop(0)
        copy = [itemset for index, itemset in enumerate(copy) if index not in matches_indices]
    return result


def apriori(data, min_support: float):
    length = len(data)
    item_support = dict()
    for itemset in data:
        for item in itemset:
            if item not in item_support:
                item_support[(item,)] = sum(item in transaction for transaction in data) / length
    frequent_sets_support = dict(filter(lambda item : item[1] >= min_support, item_support.items()))
    frequent_sets = list(frequent_sets_support.keys())
    lattice = [frequent_sets_support]
    k = 1
    while bool(frequent_sets):
        frequent_supersets = self_join(frequent_sets)
        candidates = []
        for superset_to_check in frequent_supersets:
            sets_to_check = combinations(superset_to_check, k)
            is_frequent = True
            for set_to_check in sets_to_check:
                if set_to_check not in frequent_sets:
                    is_frequent = False
                    break
            if is_frequent:
                candidates.append(superset_to_check)


        candidates_support = dict()
        for transaction in data:
            if len(transaction) >= k:
                for candidate in candidates:
                    a = set(candidate)
                    b = set(transaction)
                    if a.issubset(b):
                        if candidate in candidates_support:
                            candidates_support[candidate] += 1
                        else:
                            candidates_support[candidate] = 1
        for itemset in candidates_support:
            candidates_support[itemset] /= length
        successful_candidates = dict(filter(lambda candidate : candidate[1] >= min_support, candidates_support.items()))
        frequent_sets = list(successful_candidates.keys())

        if bool(successful_candidates):
            lattice.append(successful_candidates)
        k += 1

    return lattice



def get_rules(lattice: list, min_confidence: float):
    valid_rules = []
    if len(lattice) <= 1:
        return valid_rules
    for frequent_sets in lattice[1:]:
        for itemset in frequent_sets:
            rules_to_test = list(set_partitions(itemset, 2))
            for i, rule in enumerate(rules_to_test):
                rules_to_test[i] = tuple(tuple(subset) for subset in rule)
            rules_to_test += list(tuple(reversed(rule)) for rule in rules_to_test)
            for rule_to_test in rules_to_test:
                subset_support = lattice[len(rule_to_test[0]) - 1][rule_to_test[0]]
                confidence = frequent_sets[itemset] / subset_support
                if confidence >= min_confidence:
                    rule = tuple(rule_to_test)
                    row = (rule, len(itemset), frequent_sets[itemset], confidence)
                    valid_rules.append(row)
    return valid_rules



if __name__ == "__main__":
    data1 = [
        [1, 3, 4],
        [2, 4],
        [1, 2, 3, 5],
        [2, 4, 6]
    ]
    data2 = [
        [1, 2, 3],
        [1, 2, 3, 4, 5],
        [1, 3, 4],
        [1, 3, 4, 5],
        [1, 2, 3, 4]
    ]
    data3 = create_dataset("ed-p03.txt")

    lattice = apriori(data2, 0.4)
    rows = get_rules(lattice, 0.6)
    rows = [(f"{set(row[0][0])} => {set(row[0][1])}", *row[1:]) for row in rows]
    rows.sort(key = itemgetter(2), reverse = True)
    rows.sort(key = itemgetter(3), reverse = True)
    rows.sort(key = itemgetter(1), reverse = True)
    headers = ("association rule", "number of elements", "support", "confidence")
    
    print(tabulate(rows, headers = headers, floatfmt = ".2f"))