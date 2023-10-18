from datetime import datetime, timedelta

from PIL import Image, ImageDraw, ImageFont


async def sign_numbers():
    xbase = 136  # origin for x
    ybase = 40  # origin for y
    xstep = 170

    # Create a new image using PIL
    image = Image.open("src/repositories/bookings/schedule.jpg")
    draw = ImageDraw.Draw(image)

    lightGreen = (123, 209, 72)
    lightGray = (211, 211, 211)
    lightBlack = (48, 54, 59)
    lightBlue = (173, 216, 230)
    red = (255, 0, 0)
    black = (0, 0, 0)

    fontSimple = ImageFont.truetype("src/repositories/bookings/open_sans.ttf", size=14)

    radius = 10

    current_day = datetime.now().weekday()
    print(current_day)

    draw.ellipse(
        (
            (xbase - radius) + xstep * current_day,
            ybase - radius,
            (xbase + radius) + xstep * current_day,
            ybase + radius,
        ),
        outline=red,
    )

    image.save("sign.jpg")
