#-*- coding:utf-8 -*-


# Bachelorprojekt 2015 - Heartbeat-protokollen.
# Dennis Bøgelund Olesen & Erik David Allin

from __future__ import division


def heartbeat(hjerte, slag):
  hjerteslag = hjerte + slag
  
  return hjerteslag



# Tester opgaven
def main():
  hjerte = 1;
  slag = 2;
  print heartbeat(hjerte, slag);



# Sikrer sig at main metoden bliver eksekveret.
if __name__ == "__main__":
  main()
