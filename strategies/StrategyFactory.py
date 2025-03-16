from typing import Dict, Type

from strategies.NginxShareStrategy import NginxShareStrategy
from strategies.Strategy import Strategy


class StrategyFactory:
    _strategies: Dict[str, Type[Strategy]] = {
        "nginx_share": NginxShareStrategy,
    }

    @classmethod
    def create(cls, strategy_name: str) -> Strategy:
        if strategy_name not in cls._strategies:
            raise ValueError(f"Unknown strategy: {strategy_name}")
        return cls._strategies[strategy_name]()
