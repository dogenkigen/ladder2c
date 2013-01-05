from src_index import app


if __name__ == "__main__":
    #To make this publicly available simply set parameter host='0.0.0.0'.
    app.debug = False
    app.run()#debug=True, host='0.0.0.0')