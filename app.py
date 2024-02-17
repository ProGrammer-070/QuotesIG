from flask import Flask, render_template, request, redirect, url_for, flash
from quote_maker import save_nature_image_with_quote
from instabot import Bot

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Instagram credentials
INSTAGRAM_USERNAME = 'abc@gmail.com'
INSTAGRAM_PASSWORD = 'xyz'

def upload_to_instagram(image_path, caption):
    bot = Bot()
    bot.login(username=INSTAGRAM_USERNAME, password=INSTAGRAM_PASSWORD)
    bot.upload_photo(image_path, caption=caption)
    bot.logout()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'generate' in request.form:
            # Generate the quote image
            save_nature_image_with_quote()
            flash('Nature image with quote generated successfully!', 'success')
        elif 'upload' in request.form:
            # Upload the image to Instagram
            try:
                upload_to_instagram('nature_quote.png', 'Your random caption here #tag1 #tag2')
                flash('Image uploaded to Instagram successfully!', 'success')
            except Exception as e:
                flash(f'Error uploading image: {str(e)}', 'error')
        return redirect(url_for('index'))

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
