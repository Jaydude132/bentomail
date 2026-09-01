# Author: Jason Marencic
# June 2, 2026

from dataclasses import dataclass
from .colors import *


@dataclass(frozen=True)
class EmailTheme:
    # 1. Structural layout variables (Must be defined explicitly for every theme)
    name: str
    bg_color: str
    text_color: str
    text_muted: str
    border_color: str
    header_bg: str
    accent_color: str
    section_bg: str  # Solves section background AttributeError
    hero_from_color: str  # Theme-specific hero gradient start
    hero_to_color: str  # Theme-specific hero gradient end
    hero_accent_color: str  # Theme-specific hero badge text color
    hero_text_color: str  # Theme-specific hero title & body text color

    # 2. Semantic status levels (Default to standard corporate tailwind colors)
    success_color: str = EMERALD_500  # Green (#10b981 equivalent)
    ok_color: str = EMERALD_500  # Green (Alias)
    info_color: str = BLUE_500  # Blue (#3b82f6 equivalent)
    warning_color: str = AMBER_500  # Yellow/Amber (#f59e0b equivalent)
    minor_color: str = ORANGE_500  # Orange (#f97316 equivalent)
    error_color: str = RED_500  # Crimson/Red-Orange (#ef4444 equivalent)
    critical_color: str = RED_600  # Deep Red (#dc2626 equivalent)
    important_color: str = FUCHSIA_500  # Fuchsia (#d946ef equivalent)


# --- Core Instances ---

# LIGHT: Clean light theme using BLUE_600 as accent and a vibrant sky-blue hero panel
LIGHT = EmailTheme(
    name="Light",
    bg_color=WHITE,
    text_color=SLATE_900,
    text_muted=SLATE_500,
    border_color=SLATE_200,
    header_bg=SLATE_50,
    accent_color=BLUE_600,
    section_bg=SLATE_100,
    hero_from_color="#0ea5e9",
    hero_to_color="#2563eb",
    hero_accent_color="#EFFE33",
    hero_text_color=WHITE,
)

# NEUTRAL: Pure-gray dark theme with corrected layered elevations
NEUTRAL = EmailTheme(
    name="Neutral",
    bg_color=NEUTRAL_950,
    text_color=NEUTRAL_50,
    text_muted=NEUTRAL_400,
    border_color=NEUTRAL_700,
    header_bg=NEUTRAL_800,
    accent_color=TEAL_500,
    section_bg=NEUTRAL_900,
    hero_from_color="#1e1b4b",
    hero_to_color="#311042",
    hero_accent_color=FUCHSIA_500,
    hero_text_color=WHITE,
)

# SLATE: Deep blue-slate dark theme with a vibrant neon hero block
SLATE = EmailTheme(
    name="Slate",
    bg_color=SLATE_950,
    text_color=SLATE_50,
    text_muted=SLATE_400,
    border_color=SLATE_800,
    header_bg=SLATE_900,
    accent_color=TEAL_500,
    section_bg="#171F33",
    hero_from_color="#1e1b4b",
    hero_to_color="#311042",
    hero_accent_color=FUCHSIA_500,
    hero_text_color=WHITE,
)

# MONOKAI: Overrides corporate semantics with retro, neon counterparts
MONOKAI = EmailTheme(
    name="Monokai",
    bg_color=STONE_900,  # Warm charcoal background (#1c1917)
    text_color=STONE_100,  # Soft off-white text
    text_muted=CYAN_400,  # Retro light blue highlights
    border_color=STONE_700,  # Muted warm borders
    header_bg=STONE_800,  # Darker warm accent panel
    accent_color=VIOLET_400,  # Retro Pastel Purple Accent
    section_bg=STONE_950,
    hero_from_color="#27272a",
    hero_to_color="#18181b",
    hero_accent_color=LIME_400,
    hero_text_color="#f4f4f5",
    # Overriding semantic indicators to match Monokai's retro code spectrum
    success_color=LIME_400,  # Neon Lime-green (#a3e635)
    ok_color=LIME_400,  # Neon Lime-green (Alias)
    info_color=CYAN_400,  # Retro Sky-Blue (#22d3ee)
    warning_color=YELLOW_400,  # Soft retro mustard yellow (#facc15)
    minor_color=ORANGE_400,  # Warm retro orange (#fb923c)
    error_color=FUCHSIA_500,  # Neon Warning Pink (#d946ef)
    critical_color=ROSE_500,  # High-visibility retro rose-red (#f43f5e)
    important_color=PURPLE_400,  # Retro Pastel Purple (#c084fc)
)

# GRUVBOX: Retro, high-contrast, ultra-warm terminal theme with corrected high-visibility border
GRUVBOX = EmailTheme(
    name="Gruvbox",
    bg_color="#282828",  # Warm gruvbox dark background
    text_color="#ebdbb2",  # Retro light cream text
    text_muted="#a89984",  # Warm medium gray highlights
    border_color="#504945",  # High-visibility border lines (resolves invisible row lines)
    header_bg="#3c3836",  # Slightly elevated warm panel
    accent_color="#fe8019",  # Retro Gruvbox Orange Accent
    section_bg="#1d2021",  # Deep high-contrast panel background
    hero_from_color="#1d2021",  # Solid flat background (eliminates bleed/blending)
    hero_to_color="#1d2021",
    hero_accent_color="#fabd2f",  # Gruvbox Yellow Badge
    hero_text_color="#ebdbb2",  # Retro cream body text
    # Overriding semantic indicators to match Gruvbox's classic palette
    success_color="#b8bb26",  # Gruvbox Green
    ok_color="#b8bb26",  # Gruvbox Green (Alias)
    info_color="#83a598",  # Gruvbox Aqua/Blue
    warning_color="#fabd2f",  # Gruvbox Yellow
    minor_color="#fe8019",  # Gruvbox Orange
    error_color="#fb4934",  # Gruvbox Red
    critical_color="#cc241d",  # Gruvbox Deep Red
    important_color="#d3869b",  # Gruvbox Purple
)
