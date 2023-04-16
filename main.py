from game import JetFighter
import asyncio

if __name__ == '__main__':
    jet_fighter = JetFighter()
    asyncio.run(jet_fighter.main_loop())
