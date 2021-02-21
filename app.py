from flask import Flask, render_template, url_for, request, redirect, Markup
from sleep import predict_sleep
from text import analyze_text

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sleep', methods=['POST', 'GET'])
def sleep():
    if request.method == 'POST':
        sleep = request.form['sleep_hrs']
        need2drive = float(request.form["need2drive_hrs"])
        predict = round(predict_sleep(app, sleep), 2)
        drive_ok = predict >= need2drive
        data = {"username": request.form["username"], "sleep_hrs": sleep, "need2drive_hrs": need2drive, "predict": predict, "drive_ok": drive_ok}
        return render_template('sleep.html', data=data)
    else:
        return render_template('sleep.html')

@app.route('/text', methods=['POST', 'GET'])
def text():
    if request.method == 'POST':
        sample = request.form['sample']
        data = analyze_text(sample)
        s = "Sentiment is "
        if(data['whole_sentiment'].polarity<-0.25): s = s + "negative (" + str(round(data['whole_sentiment'].polarity, 2)) +") and "
        elif(data['whole_sentiment'].polarity>0.25): s = s + "positive (" + str(round(data['whole_sentiment'].polarity, 2)) +") and "
        else: s = s + "neutral (" + str(round(data['whole_sentiment'].polarity, 2)) +") and "
        if(data['whole_sentiment'].subjectivity>=0.5): s = s + "it is subjective (" + str(round(data['whole_sentiment'].subjectivity, 2)) +")"
        else: s = s + "it is objective (" + str(round(data['whole_sentiment'].subjectivity, 2)) +")"

        data["sentiment_summary"] = s

        segments = []
        for i in range(len(data['segments'])):
            sent = ""
            if (data['sentiments'][i].polarity<-0.25):
                sent = " Negative (" + str(round(data['sentiments'][i].polarity, 2)) + ")"
            elif (data['sentiments'][i].polarity>0.25):
                sent = " Positive (" + str(round(data['sentiments'][i].polarity, 2)) + ")"
            else:
                sent = " Neutral (" + str(round(data['sentiments'][i].polarity, 2)) + ")"
            if(data['sentiments'][i].subjectivity>=0.5): sent = sent + "  Subjective (" + str(round(data['sentiments'][i].subjectivity, 2)) +")"
            else: sent = sent + "  Objective (" + str(round(data['sentiments'][i].subjectivity, 2)) +")"

            sent = Markup("<blockquote class='blockquote'><p class='mb-0'>"+data['segments'][i]+"</p><footer class='blockquote-footer'><cite>"+sent+"</cite></footer></blockquote>")
            segments.append(sent)
        data["segments"] = segments
        return render_template('text.html', data=data)
    else:
        return render_template('text.html')
"""
@app.route('/sleep/predict', methods=['POST'])
def sleep_predict():
    if request.method == 'POST':
        return Flask.jso
    else:
        return redirect('/sleep')

@app.route('/text/predict', methods=['POST'])
def text_predict():
    return render_template('text.html')
"""

if __name__ == "__main__":
    app.run(debug=True)