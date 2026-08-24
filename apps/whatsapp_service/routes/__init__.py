# coding: utf-8
"""
Routes Blueprint initialization for WhatsApp Service Module
"""

import os
from flask import Blueprint

basedir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.abspath(os.path.join(basedir, '../templates'))

whatsapp_bp = Blueprint('whatsapp_service', __name__, template_folder=template_dir)

# Import sub-modules to register routes on whatsapp_bp
from . import webhook
from . import dashboard
from . import actions
from . import api

__all__ = ['whatsapp_bp']
