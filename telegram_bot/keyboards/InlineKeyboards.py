from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def lands(lands, page, max_pages):
    keyboard = []

    for land in lands:
        keyboard.append(
            [InlineKeyboardButton(text=land.name, callback_data=f"land_{land.id}")]
        )

    if page < max_pages:
        keyboard.append(
            [InlineKeyboardButton(text="->", callback_data=f"page_{(page + 1)}")]
        )

    if page >= 2:
        keyboard.append(
            [InlineKeyboardButton(text="<-", callback_data=f"page_{(page - 1)}")]
        )
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def cities(cities):
    keyboard = []

    for city in cities:
        keyboard.append([InlineKeyboardButton(
            text=city.name,
            callback_data=f"city_{city.id}"
        )]),
    
    keyboard.append([InlineKeyboardButton(
        text="Back",
        callback_data="lands"
    )])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def landmarks(landmarks, land_id):
    keyboard = []

    for landmark in landmarks:
        keyboard.append([InlineKeyboardButton(
            text=landmark.name,
            callback_data=f"landmark_{landmark.id}"
        )]),

    keyboard.append([InlineKeyboardButton(
        text="Back",
        callback_data=f"land_{land_id}"
        )])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def back_landmark_to_landmarks():
    InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="back",
                    callback_data=f"back_landmark"
                )
            ]
        ]
    )


def save_topic():
    topic = InlineKeyboardMarkup(
        inline_keyboard = [
            [
                InlineKeyboardButton(
                    text="Lands",
                    callback_data="saved_lands"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Cities",
                    callback_data="saved_cities"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Landmarks",
                    callback_data="saved_landmarks"
                )
            ]
        ]
    )
    return topic

def saves_lands(lands):
    keyboard = []

    for land in lands:
        keyboard.append([InlineKeyboardButton(text=land.land.name, callback_data=f"saves_land_{land.land.id}")]),

    keyboard.append([InlineKeyboardButton(text="Back", callback_data="saves_back_to_topic")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def saves_cities(cities):
    keyboard = []

    for city in cities:
        keyboard.append([InlineKeyboardButton(text=city.city.name, callback_data=f"saves_city_{city.city.id}")])
    
    keyboard.append([InlineKeyboardButton(text="Back", callback_data="saves_back_to_topic")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def saves_landmarks(landmarks):
    keyboard = []

    for landmark in landmarks:
        keyboard.append([InlineKeyboardButton(text=landmark.landmark.name, callback_data=f"saves_landmark_{landmark.landmark.id}")])


    keyboard.append([InlineKeyboardButton(text="Back", callback_data="saves_back_to_topic")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def saves_landmark_back():
    back = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Back", callback_data="saves_back_to_landmarks")
            ]
        ]
    )
    return back


def lands_for_AddCity(lands, page, max_page):
    keyboard = []

    for land in lands:
        keyboard.append([InlineKeyboardButton(text=land.name, callback_data=f"AddCity_{land.id}")])

    if page < max_page:
        keyboard.append([InlineKeyboardButton(text="->", callback_data=f"page_{page}")])

    if page >= 2:
        keyboard.append([InlineKeyboardButton(text="<-", callback_data=f"page_{page}")])
        
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def cities_for_AddLandmark(cities, page, max_page):
    keyboard = []

    for city in cities:
        keyboard.append([InlineKeyboardButton(text=city.name, callback_data=f"AddLandmark_{city.id}")])

    if page < max_page:
        keyboard.append([InlineKeyboardButton(text="->", callback_data=f"page_{page}")])

    if page >= 2:
        keyboard.append([InlineKeyboardButton(text="<-", callback_data=f"page_{page}")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)