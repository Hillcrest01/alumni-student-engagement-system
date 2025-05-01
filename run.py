from app import create_app

#this is the main app that runs the whole code.

app = create_app()


if __name__ == '__main__':
    app.run(debug=True)
