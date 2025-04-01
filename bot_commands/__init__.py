from .command_start import router as router_start
from .command_set_goal import router as router_set_goal
from .command_search_global import router as router_search_global
from .command_search_favorite import router as router_search_favorite
from .command_create_favorite import router as router_create_favorite
from .command_favorite_from_image import router as router_favorite_from_image
from .command_daily_stats import router as router_daily_stats

__all__ = [
    "router_start",
    "router_set_goal",
    "router_search_global",
    "router_search_favorite",
    "router_create_favorite",
    "router_favorite_from_image",
    "router_daily_stats"
]
