#IM experiment the game of life cellular automaton parameter setting
#coding on 22nd April 2019
#by Shoko Ota
import numpy as np

class CAparam:
    def __init__(self):
        self.size =  []
        self.rule_param = np.array([])

    def setSize(self):
        self.size = [8, 8]
        return self.size

    def setParam(self):
        self.rule_param = np.array(
                [[9, 2, 4, 2],  # rule 1: rich expression, less control
                [9, 2, 4, 3],  # rule 2: modest expression, good control
                [9, 2, 3, 2],  # rule 3: rich expression, modest? control
                [9, 3, 4, 3]]) # rule 4:
        return self.rule_param
