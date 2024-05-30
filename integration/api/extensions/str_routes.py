from flask import Flask


def str_routes(app: Flask):
    """str_routes"""
	
    return '\n'.join((
        f'{rule.endpoint}: {rule}'
        for rule in app.url_map.iter_rules()
    ))
