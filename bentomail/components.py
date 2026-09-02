# Author: Jason Marencic
# June 2, 2026

from dataclasses import dataclass, field
from typing import Optional, List, Union, ClassVar


@dataclass
class FooterLink:
    text: str
    url: str


@dataclass
class LineBreak:
    """Terminates a row early or inserts standard visual vertical space."""

    colspan: int = 2


@dataclass
class Header:
    description: str = ""
    title: str = ""
    subtitle: str = ""
    color: Optional[str] = None


@dataclass
class Hero:
    badge: str = ""
    title: str = ""
    description: str = ""
    from_color: Optional[str] = None
    to_color: Optional[str] = None
    accent_color: Optional[str] = None


@dataclass
class Card:
    title: str = ""
    value: str = ""
    label: str = ""
    color: Optional[str] = None
    colspan: Optional[int] = None
    width_pct: Optional[str] = None  # Dynamic layout calculation property
    invisible: bool = False  # True triggers a transparent spacer cell


@dataclass
class Report:
    title: str = ""
    headers: List[str] = field(default_factory=list)
    data: List[List[str]] = field(default_factory=list)
    highlight_row_index: Optional[int] = None
    header_color: str = "#1E293B"
    tip: str = ""
    colspan: int = 1
    title_align: str = "left"


@dataclass
class Footer:
    line1: str = ""
    line2: str = ""
    links: List[FooterLink] = field(default_factory=list)


@dataclass
class Notice:
    message: str
    colspan: int = 2  # Default to full-width (2) for notices
    color: ClassVar[str] = "INFO"
    header_text: ClassVar[str] = "Info"
    emoji: ClassVar[str] = "ℹ️"


@dataclass
class CriticalNotice(Notice):
    color: ClassVar[str] = "CRITICAL"
    header_text: ClassVar[str] = "Critical"
    emoji: ClassVar[str] = "⛔"


@dataclass
class ErrorNotice(Notice):
    color: ClassVar[str] = "ERROR"
    header_text: ClassVar[str] = "Error"
    emoji: ClassVar[str] = "❌"


@dataclass
class WarningNotice(Notice):
    color: ClassVar[str] = "WARNING"
    header_text: ClassVar[str] = "Warning"
    emoji: ClassVar[str] = "⚠️"


@dataclass
class ImportantNotice(Notice):
    color: ClassVar[str] = "IMPORTANT"
    header_text: ClassVar[str] = "Important"
    emoji: ClassVar[str] = "📌"


@dataclass
class SuccessNotice(Notice):
    color: ClassVar[str] = "SUCCESS"
    header_text: ClassVar[str] = "Success"
    emoji: ClassVar[str] = "✅"


@dataclass
class InfoNotice(Notice):
    color: ClassVar[str] = "INFO"
    header_text: ClassVar[str] = "Info"
    emoji: ClassVar[str] = "ℹ️"


# --- Pure-Data Chart Components ---


@dataclass
class BaseChart:
    title: str = ""
    colspan: int = 2
    x_label: str = ""
    y_label: str = ""
    color: Optional[str] = None


@dataclass
class LineChart(BaseChart):
    x: List = field(default_factory=list)
    y: List = field(default_factory=list)


@dataclass
class BarChart(BaseChart):
    categories: List[str] = field(default_factory=list)
    values: List[float] = field(default_factory=list)


@dataclass
class PieChart(BaseChart):
    labels: List[str] = field(default_factory=list)
    sizes: List[float] = field(default_factory=list)


@dataclass
class Chart:
    """Represents the compiled image placeholder rendered inside Jinja templates."""

    cid: str
    title: str = ""
    colspan: int = 2
    alt_text: str = "System Telemetry Chart"


@dataclass
class Section:
    title: str = ""
    subtitle: str = ""
    title_align: str = "left"
    widgets: List[Union[Card, Report, Notice, BaseChart]] = field(default_factory=list)

    def add_card(self, **kwargs) -> None:
        self.widgets.append(Card(**kwargs))

    def add_report(self, **kwargs) -> None:
        kwargs["colspan"] = 2  # Force full-width inside sections
        self.widgets.append(Report(**kwargs))

    def add_notice(self, notice: Notice) -> None:
        notice.colspan = 2  # Force full-width inside sections
        self.widgets.append(notice)

    def add_line_chart(self, x: list, y: list, **kwargs) -> None:
        kwargs["colspan"] = 2
        self.widgets.append(LineChart(x=x, y=y, **kwargs))

    def add_bar_chart(self, categories: list, values: list, **kwargs) -> None:
        kwargs["colspan"] = 2
        self.widgets.append(BarChart(categories=categories, values=values, **kwargs))

    def add_pie_chart(self, labels: list, sizes: list, **kwargs) -> None:
        kwargs["colspan"] = 2
        self.widgets.append(PieChart(labels=labels, sizes=sizes, **kwargs))
