from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# Product Search
@app.route("/product-search")
@app.route("/product-search/<category>")
def product_search(category=None):

    background_images = {
        "video_games": "VIdeo game p1.png",
        "sports": "Sport_product.jpg",
        "appliances": "appliences.jpg",
        "musical_instruments": "Musical products.jpg"
    }

    bg_image = background_images.get(category)

    return render_template(
        "product_search.html",
        category=category,
        bg_image=bg_image
    )


if __name__ == "__main__":
    app.run(debug=True)