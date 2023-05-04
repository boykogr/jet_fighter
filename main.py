import asyncio
from game import JetFighter

if __name__ == '__main__':
    jet_fighter = JetFighter()
    asyncio.run(jet_fighter.main_loop())
