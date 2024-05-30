from flask import Flask
from flask_injector import FlaskInjector
from injector import singleton, Binder

from functools import partial

from integration.adapters.IInteractorFactory import IInteractorFactory


def _configure_binding(binder: Binder, ioc: IInteractorFactory) -> Binder:
    """_configure_binding"""

    binder.bind(IInteractorFactory, to=ioc, scope=singleton)
    return binder

def register_dependency_injection(app: Flask, **kwargs):
    """_register_dependency_injection"""

    FlaskInjector(app=app, modules=[partial(_configure_binding, **kwargs)])
