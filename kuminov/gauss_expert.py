import math
import dearpygui.dearpygui as dpg


class GaussExpert:
    crits = 2
    alts = 2
    grades = []
    fuzzy_grades = []
    accum_table = []
    alts_eff = []
    best_alt = []

    gauss_parametrs = [{'dominant_value': [0.0] * 3,
                        'bound_neighb': [0.0] * 2,
                        'membership_deg': [0.0] * 2,
                        'ds_sigma': [0.0] * 4,
                        'y': [0.0] * 4},
                       {'dominant_value': [0.0] * 3,
                        'bound_neighb': [0.0] * 2,
                        'membership_deg': [0.0] * 2,
                        'ds_sigma': [0.0] * 4,
                        'y': [0.0] * 4}
                       ]

    def __init__(self):
        print(self.grades)

    def calculateParams(self):
        for i in range(self.crits):
            dv_ind, bn_ind, md_ind = 0, 0, 0
            for j in range(4):
                match j:
                    case 1:
                        dv_ind = 1
                    case 2:
                        bn_ind = 1
                        md_ind = 1
                    case 3:
                        dv_ind = 2
                self.gauss_parametrs[i]['ds_sigma'][j] = ((self.gauss_parametrs[i]['bound_neighb'][bn_ind] -
                                                           self.gauss_parametrs[i]['dominant_value'][dv_ind]) ** 2) \
                                                         / (-math.log(
                    self.gauss_parametrs[i]['membership_deg'][md_ind]))

                self.gauss_parametrs[i]['y'][j] = self.gauss_parametrs[i]['dominant_value'][dv_ind] + (-1) ** j * \
                                                  math.fabs(
                                                      (-self.gauss_parametrs[i]['ds_sigma'][j] * math.log(0.05)) ** 0.5)

                if self.gauss_parametrs[i]['y'][j] > self.gauss_parametrs[i]['dominant_value'][2]:
                    self.gauss_parametrs[i]['y'][j] = self.gauss_parametrs[i]['dominant_value'][2]

                if self.gauss_parametrs[i]['y'][j] < self.gauss_parametrs[i]['dominant_value'][0]:
                    self.gauss_parametrs[i]['y'][j] = self.gauss_parametrs[i]['dominant_value'][0]

    def gaussEstimate(self, crit, alt, membership):
        if membership == 0:
            if self.grades[crit][alt] < self.gauss_parametrs[crit]['dominant_value'][0]:
                return 1

            if self.grades[crit][alt] > self.gauss_parametrs[crit]['y'][0]:
                return 0

            return math.exp(-((self.grades[crit][alt] - self.gauss_parametrs[crit]['dominant_value'][0]) ** 2)
                            / self.gauss_parametrs[crit]['ds_sigma'][0])

        if membership == 1:
            if (self.gauss_parametrs[crit]['y'][1] <= self.grades[crit][alt]) and \
                    (self.grades[crit][alt] >= self.gauss_parametrs[crit]['y'][2]):
                return 0

            if (self.grades[crit][alt] > self.gauss_parametrs[crit]['y'][1]) and \
                    (self.grades[crit][alt] < self.gauss_parametrs[crit]['dominant_value'][1]):
                return math.exp(-((self.grades[crit][alt]
                                   - self.gauss_parametrs[crit]['dominant_value'][1]) ** 2)
                                / self.gauss_parametrs[crit]['ds_sigma'][1])

            return math.exp(-((self.grades[crit][alt]
                               - self.gauss_parametrs[crit]['dominant_value'][1]) ** 2)
                            / self.gauss_parametrs[crit]['ds_sigma'][2])

        if membership == 2:
            if self.grades[crit][alt] <= self.gauss_parametrs[crit]['y'][3]:
                return 0

            if self.grades[crit][alt] >= self.gauss_parametrs[crit]['dominant_value'][2]:
                return 1

            return math.exp(-((self.grades[crit][alt]
                               - self.gauss_parametrs[crit]['dominant_value'][2]) ** 2)
                            / self.gauss_parametrs[crit]['ds_sigma'][3])
        return 0.0

    def getEffectMembership(self, crit1, crit2):
        if ((crit1 == 0 and crit2 == 0) or
                (crit1 == 0 and crit2 == 1) or
                (crit1 == 1 and crit2 == 0)):
            return 0

        if ((crit1 == 1 and crit2 == 1) or
                (crit1 == 0 and crit2 == 2) or
                (crit1 == 2 and crit2 == 0)):
            return 1

        if ((crit1 == 1 and crit2 == 2) or
                (crit1 == 2 and crit2 == 1) or
                (crit1 == 2 and crit2 == 2)):
            return 2

        return 0

    def getBestAlternative(self):
        self.fuzzy_grades = [[[0 for k in range(3)] for j in range(self.alts)] for i in range(self.crits)]
        for i in range(self.crits):
            for j in range(self.alts):
                for k in range(3):
                    self.fuzzy_grades[i][j][k] = self.gaussEstimate(i, j, k)
        self.accum_table = [[0] * 3 for i in range(self.alts)]
        compares = [[[0] for k in range(3)] for j in range(self.alts)]
        ind = 0
        for i in range(self.alts):
            for c1 in range(3):
                for c2 in range(3):
                    ind = self.getEffectMembership(c1, c2);
                    compares[i][ind].append(min(self.fuzzy_grades[0][i][c1], self.fuzzy_grades[1][i][c2]))
            for t in range(3):
                self.accum_table[i][t] = compares[i][t][0];
                for k in range(len(compares[i][t])):
                    self.accum_table[i][t] = max(self.accum_table[i][t], compares[i][t][k])
        self.alts_eff = [0 for i in range(self.alts)]
        self.best_alt = [0.0, 0]
        for i in range(self.alts):
            self.alts_eff[i] = self.accum_table[i][0] * 0.1 + self.accum_table[i][1] * 0.5 + self.accum_table[i][
                2] * 0.9;
            if self.alts_eff[i] > self.best_alt[0]:
                self.best_alt = [self.alts_eff[i], i]

# ge = GaussExpert()
# ge.calculateParams()
# ge.getBestAlternative()
