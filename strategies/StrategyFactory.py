from typing import Dict, Type

from strategies.GbpStrategy import GbpStrategy
from strategies.NginxJsonStrategy import NginxJsonStrategy
from strategies.Strategy import Strategy


class StrategyFactory:
    _strategies: Dict[str, Type[Strategy]] = {
        "nginx_json": NginxJsonStrategy,
        "gbp": GbpStrategy,
    }

    @classmethod
    def create(cls, strategy_name: str) -> Strategy:
        if strategy_name not in cls._strategies:
            raise ValueError(f"Unknown strategy: {strategy_name}")
        return cls._strategies[strategy_name]()
