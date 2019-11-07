from .app import app

app.config['TRAP_BAD_REQUEST_ERRORS'] = True

if __name__ == '__main__':
    app.run()
