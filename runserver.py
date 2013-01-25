from src_index import app


if __name__ == "__main__":
    # To make this publicly available simply set parameter host='0.0.0.0'.
    # Debug should be set to false for 
    # make possible to use eclipse debugger.
    app.run(debug=False, host='0.0.0.0') 
    