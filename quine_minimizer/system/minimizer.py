class Implicant():
    def __init__(self, string, coverage):
        self.string = string
        self.coverage = coverage
        self.weight = sum([1 for x in string if x != 'X']) + sum([1 for x in string if x == '0'])

    def __repr__(self):
        return self.string

    def __gt__(self, other):
        return self.weight <= other.weight and sum(self.coverage) >= sum(other.coverage)


class Minimizer():
    constant = 'X'

    def __init__(self, count, arguments):
        self.primary_implicants = []
        self.count = count
        self.terms = [[int(i) for i in list("{number:0{base}b}".format(number=x, base=count))] for x in arguments]
        self.table_terms = [[''.join(i for i in list("{number:0{base}b}".format(number=x, base=count)))] for x in
                            range(2 ** int(count))]
        for i in range(2 ** int(count)):
            if i in arguments:
                self.table_terms[i].append('1')
            else:
                self.table_terms[i].append('0')

    def find_core_implicants(self, table):
        if self.terms == self.primary_implicants:
            return self.terms

        core = []
        width = len(table[0])
        height = len(table)
        core_columns = []
        core_rows = []
        others_rows = None
        others_columns = None
        coverage = [0 for _ in range(width)]
        self.print_implicants(table)
        # finding indices for FIRST core implicants
        s = [sum([x[j] for x in table]) for j in range(width)]
        for i in range(len(s)):
            if s[i] == 1:
                core_columns.append(i)

        # adding FC implicants and finding indices for them
        for j in core_columns:
            for i in range(height):
                if table[i][j] == 1:
                    implicant = self.primary_implicants[i]
                    if implicant not in core:
                        core.append(implicant)
                        core_rows.append(i)

        for r in core_rows:
            for c in range(width):
                if table[r][c] == 1:
                    if c not in core_columns:
                        core_columns.append(c)

        for i in core_rows:
            coverage = self.add_to_coverage(coverage, table[i])

        if sum(coverage) >= width:
            return core
        else:
            others_columns = set(range(width)) - set(core_columns)
            others_rows = set(range(height)) - set(core_rows)
            print('o_cols:', others_columns)
            print('o_rows:', others_rows)

            secondary_implicants_strings = [''.join(str(x) for x in self.primary_implicants[i]) for i in others_rows]
            secondary_implicants_coverages = [table[row] for row in others_rows]
            secondary_implicants = [Implicant(secondary_implicants_strings[i], secondary_implicants_coverages[i]) for i
                                    in range(len(secondary_implicants_strings))]
            last = sum(coverage)
            while sum(coverage) < width:
                index = secondary_implicants.index(max(secondary_implicants))
                item = secondary_implicants.pop(index)
                if sum(self.add_to_coverage(coverage, item.coverage)) > last:
                    a = self.to_arr(item)
                    core.append(a)
                    coverage = self.add_to_coverage(coverage, item.coverage)
                    last = sum(coverage)
            print(core)
            return core

    def build_coverage_table(self):
        term_len = len(self.terms)
        impl_len = len(self.primary_implicants)
        table = [[0 for _ in range(term_len)] for _ in range(impl_len)]
        terms = self.terms
        implicants = self.primary_implicants
        for i in range(impl_len):
            for j in range(term_len):
                if self.is_in(implicants[i], terms[j]):
                    table[i][j] = 1
        return table

    def find_primary_implicants(self):
        primary_implicants = self.terms
        last = []
        result = self.terms.copy()

        while True:
            x = self.merge_implicants(primary_implicants)
            if x:
                if x != last:
                    primary_implicants = self.merge_implicants(primary_implicants)
                    last = primary_implicants.copy()
                    result.extend(last)
                else:
                    break
            else:
                break
        if result == self.terms:
            self.primary_implicants = result
            return result

        primary_implicants = []
        result = result[::-1]

        for i in range(len(result)):
            implicant = result[i]
            for j in range(i + 1, len(result)):
                term = result[j]
                if not self.is_in(implicant, term) and not implicant == term:
                    if implicant not in primary_implicants:
                        x = 0
                        for i in primary_implicants:
                            if not self.is_in(i, implicant):
                                x = x + 1
                        if x == len(primary_implicants):
                            primary_implicants.append(implicant)

        self.primary_implicants = primary_implicants
        return primary_implicants

    def merge_implicants(self, implicants):
        merged = []
        length = len(implicants)
        if length < 2:
            return implicants
        for i in range(length):
            flag = False
            current_implicant = implicants[i]

            for j in range(i + 1, length):
                second_implicant = implicants[j]
                merged_implicant = self.merge(current_implicant, second_implicant)

                if merged_implicant:
                    flag = True
                    if merged_implicant not in merged:
                        merged.append(merged_implicant)

            if j <= i and not flag and current_implicant not in merged:
                merged.append(current_implicant)
        if len(merged) > 0:
            merged.pop()

        return merged

    def merge(self, a, b):
        length = len(a)
        result = []
        delta = sum(list(map(self.xor, filter(self.is_none, a), filter(self.is_none, b))))

        if delta == 1:
            for i in range(length):
                x = self.xor(a[i], b[i])
                if x is not None:
                    if x == Minimizer.constant:
                        result.append(x)
                    elif x == 1:
                        result.append(Minimizer.constant)
                    else:
                        result.append(a[i])
                else:
                    return
            return result

    @staticmethod
    def xor(a, b):
        if type(a) == type(b):
            if type(a) is str:
                return Minimizer.constant
            else:
                return int(not a == b)

    def is_in(self, implicant, term):
        return len(term) == sum(list(map(self.equals, implicant, term)))

    @staticmethod
    def equals(a, b):
        if type(a) != type(b):
            return type(a) is str
        else:
            return int(a == b)

    @staticmethod
    def is_none(x):
        return x != Minimizer.constant

    @staticmethod
    def print_implicants(list):
        for item in list:
            print(item)

    def print_coverage_table(self, table):
        head = '\t'
        for t in self.terms:
            head += ' | ' + self.to_str(t)
        head += '\n'
        rows = ''
        for i in range(len(self.primary_implicants)):
            row = self.to_str(self.primary_implicants[i]) + '|\t' + '\t' + '        '.join(
                [str(x) for x in table[i]]) + '\n'
            rows += row
        table = head + rows
        print(table)

    def to_str(self, array):
        return ''.join(map(lambda x: str(x), array))

    def to_arr(self,string):
        result = []
        for i in string.string:
            if i == 'X':
                result.append(i)
            else:
                result.append(int(i))
        return result

    def add_to_coverage(self, a, b):
        return [self.add(a[i], b[i]) for i in range(len(a))]

    @staticmethod
    def add(a, b):
        return int(not a + b < 1)
