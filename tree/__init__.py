import random
random.seed()
import math


GENERATION_ARRAY = [50 for i in xrange(16)]
BINARY_ARRAY = [int(1*math.pow(2,i)) for i in xrange(16)]
TOLERANCE = 5

BELLOW = 0
ABOVE = 1
MIDDLE = 2

HASH_TABLE = {}

class Frame(object):
    def __init__(self, array):
        self.raw_array = array
        self.sign = None
        
    def __str__(self):
        return str(self.sign)

def calc_position(base, value):
    if value + TOLERANCE > base and \
            value - TOLERANCE > base:
        return ABOVE
    elif value - TOLERANCE < base and \
            value + TOLERANCE < base:
        return BELLOW
    else:
        return MIDDLE

def calc_hashs(raw_array):
    hashs = [0]
    sign = []
    for i in xrange(len(GENERATION_ARRAY)):
        s = calc_position(GENERATION_ARRAY[i], raw_array[i])
        sign.append(s)
        
        if s == ABOVE:
            for j in xrange(len(hashs)):
                hashs[j] = hashs[j] ^  BINARY_ARRAY[i]
        elif s == MIDDLE:
            new_hashs = []
            for j in xrange(len(hashs)):
                value = hashs[j]
                new_hashs.append(value)
                value = value ^  BINARY_ARRAY[i]
                new_hashs.append(value)
            hashs = new_hashs
            
    return (sign, hashs)

def create_random_frame():
    array = []
    for _ in xrange(16):
        array.append(random.randint(0,100))
    return Frame(array)

def main():
    print '\n'
    for i in xrange(30*15*88):
        print '\rframe: ', i
        frame = create_random_frame()
        sign, hashs = calc_hashs(frame.raw_array)
        frame.sign = sign
        
        for h in hashs:
            if HASH_TABLE.has_key(h):
                HASH_TABLE[h].append(frame)
            else:
                HASH_TABLE[h] = [frame]
    
    print '\nTamanho da tabela hash:', len(HASH_TABLE)
    biggest_leafs_value = 0
    leafs = []
    for k, v in HASH_TABLE.items():
        print len(v)
        if len(v) > biggest_leafs_value:
            biggest_leafs_value = len(v)
            leafs = [k]
        elif len(v) == biggest_leafs_value:
            leafs.append(k)
            
    print 'Maior numero de frames em uma folha:', biggest_leafs_value
    print 'Folhas: ', leafs
            
            
    
    #print HASH_TABLE
        


def test():
    print BINARY_ARRAY


if __name__ == "__main__":
    #test()
    main()