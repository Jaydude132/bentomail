# Author: Jason Marencic
# June 2, 2026

from . import themes
from .bentomailer import BentoMailer
from .components import (
    BarChart,
    Chart,
    CriticalNotice,
    ErrorNotice,
    ImportantNotice,
    InfoNotice,
    LineChart,
    Notice,
    PieChart,
    Section,
    SuccessNotice,
    WarningNotice,
)
from .dashboard import Dashboard

__version__ = "0.1.0"

__all__ = [
    "BentoMailer",
    "Dashboard",
    "Section",
    "Chart",
    "LineChart",
    "BarChart",
    "PieChart",
    "Notice",
    "CriticalNotice",
    "ErrorNotice",
    "WarningNotice",
    "ImportantNotice",
    "SuccessNotice",
    "InfoNotice",
    "themes",
]
