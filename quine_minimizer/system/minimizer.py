class Minimizer():
    constant = 'X'

    def __init__(self, count, arguments):
        self.primary_implicants = []
        self.count = count
        self.terms = [[int(i) for i in list("{number:0{base}b}".format(number=x, base=count))] for x in arguments]

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
        #self.print_coverage_table(table)

    def find_primary_implicants(self):
        primary_implicants = self.terms
        last = []
        while True:
            x = self.merge_implicants(primary_implicants)
            if x:
                if x != last:
                    primary_implicants = self.merge_implicants(primary_implicants)
                    last = primary_implicants.copy()
                else:
                    break
            else:
                break
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
            return 1
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
            row = self.to_str(self.primary_implicants[i]) + '|' + self.to_str(table[i]) + '\n'
            rows += row
        table = head + rows
        print(table)


    def to_str(self, array):
        return ''.join(map(lambda x: str(x), array))
