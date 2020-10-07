import numpy as np


class RandomGenerator:
    
    def __init__(self, n_symbols, smart=False, offset=2):
        
        self.n_symbols = n_symbols
        self.smart = smart
        self.offset = offset
    
    def next_symbols(self, n):
        
        if not self.smart:
            symbols = np.random.randint(0, self.n_symbols, n)
        else:
            symbols = list(range(self.n_symbols))
            np.random.shuffle(symbols)

            while len(symbols) < n:
                new_symbols = symbols[-self.n_symbols:-self.offset]
                np.random.shuffle(new_symbols)
                symbols += new_symbols
            
        return symbols[:n]


class SequenceGenerator:
    
    def __init__(self, sequence, global_shift=0, shuffle=None):
        
        self.sequence = sequence[global_shift:] + sequence[:global_shift]
        if 'global' == shuffle:
            np.random.shuffle(self.sequence)
        self.shuffle_line = 'line' == shuffle
        
        self.shift = 0

    def next_symbols(self, n):
        symbols = self.sequence[self.shift:self.shift+n]
        if self.shuffle_line:
            np.random.shuffle(symbols)
        self.shift += n
        return symbols
