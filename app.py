from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Örnek veri yapısı (sonradan veritabanına taşınacak)
contents = {
    "qr123": {
        "text": "Bu bir örnek metindir. Ses dosyasıyla senkronize şekilde ilerleyecek.",
        "audio_file": "static/audio/sample.mp3",
        "timestamps": [0, 2, 5, 8]  # Saniye cinsinden zaman damgaları
    }
}

@app.route('/content/<qr_id>')
def show_content(qr_id):
    content = contents.get(qr_id)
    if not content:
        return "İçerik bulunamadı", 404
    return render_template('index.html', content=content)

if __name__ == '__main__':
    app.run(debug=True) 