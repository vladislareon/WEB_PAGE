import ahocorasick
import numpy as np


class DerOtr:
    def __init__(self, n):
        self.basic_skip = 0
        self.m = 1
        while self.m < n:
            self.m *= 2
        self.der = [10 ** 10] * (2 * self.m)
        for i in range(self.m, 2 * self.m):
            self.der[i] = (10 ** 10, i - self.m, -1)  # min_skipped, xpath_ind, str_ind
        self.der[self.m] = (0, 0, -1)
        for i in range(self.m - 1, 0, -1):
            self.der[i] = min(self.der[2 * i], self.der[2 * i + 1])

    def getval(self, i):
        ret = self.der[i + self.m]
        ret = (ret[0] + self.basic_skip,) + ret[1:]
        return ret

    def relaxate(self, i, val):
        if self.getval(i) < val:
            return False
        self.der[i + self.m] = val
        self.der[i + self.m] = (self.der[i + self.m][0] - self.basic_skip,) + self.der[
            i + self.m
        ][1:]
        ind = (i + self.m) // 2
        while ind != 0:
            self.der[ind] = min(self.der[2 * ind], self.der[2 * ind + 1])
            ind //= 2
        return True

    def increment_skip(self):
        self.basic_skip += 1

    def getmin(self, ind):
        a = self.m
        b = self.m + ind - 1
        minres = self.der[a]
        while a < b:
            minres = min(minres, self.der[a])
            minres = min(minres, self.der[b])
            a = (a + 1) // 2
            b = (b - 1) // 2
        if a == b:
            minres = min(minres, self.der[a])
        minres = (minres[0] + self.basic_skip,) + minres[1:]
        return minres

    def getmin_global(self):
        return self.getmin(self.m)


class StringProcess:
    def __init__(self, blocks_, text_, split_len=10):
        text = "".join(x.lower() if x.isalpha() else "" for x in text_)
        blocks = [
            "".join(x.lower() if x.isalpha() else "" for x in block["text"])
            for block in blocks_.values()
        ]
        self.blocks = list(block["text"] for block in blocks_.values())
        self.aut = ahocorasick.Automaton()
        self.blocks_keys = list(blocks_.keys())
        nblocks = []
        self.split_len = split_len
        dups = dict()
        cou = 0
        for i in range(len(blocks)):
            for j in range((len(blocks[i]) - 1) // split_len + 1):
                cou += 1
                string = blocks[i][j * split_len : j * split_len + split_len]
                if string not in self.aut:
                    self.aut.add_word(string, cou)
                    dups[cou] = set([cou])
                else:
                    ind = self.aut.get(string)
                    dups[ind].add(cou)
                nblocks.append(blocks[i][j * split_len : j * split_len + split_len])
        self.aut.make_automaton()
        self.corassick_links = [list() for i in range(len(text))]
        self.dynamic = [dict() for i in range(len(text))]
        for end, ind_ in self.aut.iter(text):
            for ind in dups[ind_]:
                self.corassick_links[end - len(nblocks[ind - 1]) + 1].append(
                    (len(nblocks[ind - 1]), ind)
                )
        self.derotr = DerOtr(len(nblocks) + 1)

    def do_step(self, ind):
        for j in self.corassick_links[ind]:
            val = self.derotr.getmin(j[1])
            self.dynamic[ind + j[0] - 1][j[1]] = val
        self.derotr.increment_skip()
        for i in self.dynamic[ind].keys():
            self.derotr.relaxate(i, (self.dynamic[ind][i][0], i, ind))

    def do_all(self):
        for i in range(len(self.corassick_links)):
            self.do_step(i)
        minres = self.derotr.getmin_global()
        skipped = minres[0]
        xpath = minres[1]
        yind = minres[2]
        ret = [xpath]
        while yind != -1:
            _, xpath, yind = self.dynamic[yind][xpath]
            ret.append(xpath)
        ret.reverse()
        cur_ind = 0
        ans_k = [-1]
        for i in range(len(self.blocks_keys)):
            j = "".join(x.lower() if x.isalpha() else "" for x in self.blocks[i])
            ans_k += [i] * ((len(j) + self.split_len - 1) // self.split_len)

        a, b = np.unique(np.array(ans_k)[ret], return_counts=True)
        true_dict = dict(zip(a, b))
        a, b = np.unique(np.array(ans_k), return_counts=True)
        all_dict = dict(zip(a, b))
        ans = []
        for i in range(len(self.blocks_keys)):
            if i in true_dict and all_dict[i] == true_dict[i]:
                ans.append(self.blocks_keys[i])

        return skipped, ret, ans
