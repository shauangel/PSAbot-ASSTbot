import functools
from flask import (
    Blueprint, redirect, render_template, request
)

bp = Blueprint('webpage', __name__, url_prefix='/web')

#