from flask import Flask, render_template, request, flash, redirect, url_for
from quote_maker import save_nature_image_with_quote
from instabot import Bot
import datetime

app = Flask(__name__)
app.secret_key = "TheSecretIsKnown"  # Change this to a secure key

# Initialize Instabot
bot = Bot()
bot.login(username="daily_dose_of_wise_words", password="root@insta#7")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.form['action'] == 'generate':
            save_nature_image_with_quote("static/output_image.png")
            return redirect(url_for('index'))
        elif request.form['action'] == 'upload':
            # Upload the image to Instagram
            try:
                bot.upload_photo("static/output_image.png", caption=f"Word Of Wisdom | {datetime.datetime.now().strftime('%b %d')}\n\n#motivation #inspiration #quote")
                flash("Image uploaded to Instagram successfully!", "success")
            except Exception as e:
                flash(f"Error uploading image to Instagram: {str(e)}", "danger")
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
