from .app import routes

routes.config['TRAP_BAD_REQUEST_ERRORS'] = True

if __name__ == '__main__':
    routes.run()
