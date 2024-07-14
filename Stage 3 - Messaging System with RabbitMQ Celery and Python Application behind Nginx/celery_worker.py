from app import celery, app

if __name__ == '__main__':
    with app.app_context():
        celery.start()