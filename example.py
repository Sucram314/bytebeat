from bytebeat import ByteBeat

from math import cos,exp
from random import random

def envelope(t):
    return 1 - min((t/2048)**3,1)

def soft_clipper(x,order=10):
    return 1/(1+exp(-order*(x-0.5)))

def func(t):
    saws = 0

    saws += ((t*2*2**(
            [9,7,5,7,9,7,5,4]
            [(t>>14)%8]/12))%256
        )/15

    saws += ((t*2*2**(
            [16,14,12,14,16,14,12,11]
            [(t>>14)%8]/12))%256
        )/15

    saws += ((t*4*2**(
            [9,7,5,7,9,7,5,4]
            [(t>>14)%8]/12))%256
        )/15

    saws += ((t*4*2**(
        [
            19,11,12,19,11,12,19,11,12,19,11,12,23,11,19,11,
            19,11,12,19,11,12,19,11,12,24,11,12,23,11,21,11,
            19,11,12,19,11,12,19,11,12,19,11,12,17,11,16,11,
            14,11,12,14,11,12,14,11,12,14,11,12,16,11,14,11,
            12,11,12,19,11,12,19,11,12,19,11,12,23,11,19,11,
            19,11,12,19,11,12,19,11,12,24,11,12,23,11,21,11,
            19,11,12,19,11,12,19,11,12,19,11,12,17,11,16,11,
            14,11,12,14,11,12,14,11,12,14,11,12,16,11,14,11
        ][(t>>10)%128]/12))%256
    )/10

    if t % 262144 >= 131072:
        saws += ((t*8*2**(
            [19,19,19,19,19,19,17,17,16,16,16,16,14,14,16,16,9,9,9,21,19,19,23,23,16,16,16,16,8,8,14,14]
            [(t>>12)%32]/12))%256
        )/8

    kick_times = [0,16384,22528,32768,49152,52224,55296]
    t_kick = t%65536-max(i for i in kick_times if i <= t%65536)
    kick_envelope = envelope(t_kick)
    kick = soft_clipper((1-cos(49152/(t_kick+384)))*0.5 * kick_envelope) * 60

    snare_times = [-65536,8192,24576]
    t_snare = t%32768-max(i for i in snare_times if i <= t%32768)
    snare_envelope = envelope(t_snare)
    snare = soft_clipper(((1-cos(131072/(t_snare+512)))*0.5 + random())*0.5 * snare_envelope) * 60

    sidechain = (1 - kick_envelope*0.7 - snare_envelope*0.5)

    master = saws * sidechain + kick + snare

    return master*2

bytebeat = ByteBeat(
    func=func,
    width=512
)