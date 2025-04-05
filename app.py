from flask import Flask, render_template, request

app = Flask(__name__)



@app.route('/', methods=['POST', 'GET'])
def index ():
    print(request)
    if request.method == 'POST':
        taskContent = request.form['content']
        return taskContent
    
    return render_template("index.html")
    

if __name__ == "__main__":
    app.run(debug=True)