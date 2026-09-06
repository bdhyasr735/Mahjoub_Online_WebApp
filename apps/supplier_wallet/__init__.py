# coding: utf-8
# 📂 apps/supplier_wallet/__init__.py

from .registry import (
    MODULE_NAME,
    MODULE_ICON,
    SHOW_IN_SUPPLIER,
    LINKS,
    register_module,
    get_module_stats,
    get_module_link,
    get_dashboard_card
)

__all__ = [
    'MODULE_NAME',
    'MODULE_ICON',
    'SHOW_IN_SUPPLIER',
    'LINKS',
    'register_module',
    'get_module_stats',
    'get_module_link',
    'get_dashboard_card'
]
