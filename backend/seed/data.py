"""Deterministic seed datasets conforming to PRD §17."""

AMENITIES_DATA = [
    # Essentials
    {"name": "Fast Wifi", "icon_key": "wifi", "group": "Essentials"},
    {"name": "Kitchen", "icon_key": "utensils", "group": "Essentials"},
    {"name": "Dedicated workspace", "icon_key": "laptop", "group": "Essentials"},
    {"name": "Air conditioning", "icon_key": "wind", "group": "Essentials"},
    {"name": "Heating", "icon_key": "flame", "group": "Essentials"},
    {"name": "Washer", "icon_key": "disc", "group": "Essentials"},
    {"name": "Dryer", "icon_key": "sun", "group": "Essentials"},
    {"name": "TV", "icon_key": "tv", "group": "Essentials"},
    {"name": "Hair dryer", "icon_key": "zap", "group": "Essentials"},
    {"name": "Iron", "icon_key": "minimize", "group": "Essentials"},
    # Features
    {"name": "Free parking on premises", "icon_key": "car", "group": "Features"},
    {"name": "Private pool", "icon_key": "waves", "group": "Features"},
    {"name": "Hot tub", "icon_key": "bath", "group": "Features"},
    {"name": "BBQ grill", "icon_key": "flame", "group": "Features"},
    {"name": "Fire pit", "icon_key": "flame", "group": "Features"},
    {"name": "Gym", "icon_key": "dumbbell", "group": "Features"},
    {"name": "EV charger", "icon_key": "battery-charging", "group": "Features"},
    {"name": "Self check-in", "icon_key": "key", "group": "Features"},
    {"name": "Balcony", "icon_key": "sun", "group": "Features"},
    {"name": "Garden", "icon_key": "trees", "group": "Features"},
    {"name": "Breakfast included", "icon_key": "coffee", "group": "Features"},
    {"name": "Crib", "icon_key": "baby", "group": "Features"},
    {"name": "Pets allowed", "icon_key": "paw-print", "group": "Features"},
    # Location
    {"name": "Beachfront access", "icon_key": "umbrella", "group": "Location"},
    {"name": "Ocean view", "icon_key": "eye", "group": "Location"},
    {"name": "Mountain view", "icon_key": "mountain", "group": "Location"},
    {"name": "Lake access", "icon_key": "anchor", "group": "Location"},
    # Safety
    {"name": "Smoke alarm", "icon_key": "shield-alert", "group": "Safety"},
    {"name": "First aid kit", "icon_key": "cross", "group": "Safety"},
    {"name": "Fire extinguisher", "icon_key": "shield", "group": "Safety"},
]

DESTINATIONS_DATA = [
    {"city": "Goa", "country": "India", "lat": 15.2993, "lng": 74.1240},
    {"city": "Manali", "country": "India", "lat": 32.2396, "lng": 77.1887},
    {"city": "Jaipur", "country": "India", "lat": 26.9124, "lng": 75.7873},
    {"city": "Lisbon", "country": "Portugal", "lat": 38.7223, "lng": -9.1393},
    {"city": "Ubud", "country": "Indonesia", "lat": -8.5069, "lng": 115.2625},
    {"city": "Lake Tahoe", "country": "United States", "lat": 39.0968, "lng": -120.0324},
    {"city": "Santorini", "country": "Greece", "lat": 36.3932, "lng": 25.4615},
    {"city": "Kyoto", "country": "Japan", "lat": 35.0116, "lng": 135.7681},
    {"city": "Cape Town", "country": "South Africa", "lat": -33.9249, "lng": 18.4241},
    {"city": "Tulum", "country": "Mexico", "lat": 20.2114, "lng": -87.4654},
    {"city": "Siena", "country": "Italy", "lat": 43.3188, "lng": 11.3308},
    {"city": "Banff", "country": "Canada", "lat": 51.1784, "lng": -115.5708},
]

CATEGORIES = [
    "Trending",
    "Beachfront",
    "Cabins",
    "Amazing views",
    "Countryside",
    "Design",
    "Tiny homes",
    "Lakefront",
    "Amazing pools",
    "Treehouses",
    "Camping",
    "Farms",
    "Mansions",
    "Islands",
]

PROPERTY_TYPES = [
    "House",
    "Apartment",
    "Villa",
    "Cabin",
    "Cottage",
    "Chalet",
    "Loft",
]

ROOM_TYPES = ["entire_home", "private_room", "shared_room"]

UNSPLASH_PHOTO_IDS = [
    "1502672260266-1c1ef2d93688",
    "1512917774080-9991f1c4c750",
    "1600585154340-be6161a56a0c",
    "1600596542815-ffad4c1539a9",
    "1542314831-068cd1dbfeeb",
    "1564013799919-ab600027ffc6",
    "1578683010236-d716f9a3f461",
    "1582719478250-c89cae4dc85b",
    "1613490493576-7fde63acd811",
    "1518780664697-55e3ad937233",
    "1571896349842-33c89424de2d",
    "1568605117036-5fe5e7bab0b7",
    "1576013551627-0cc20b96c2a7",
    "1600607687939-ce8a6c25118c",
    "1590490360182-c33d57733427",
    "1505691938895-1758d7feb511",
    "1600566753190-17f0baa2a6c3",
    "1566073771259-6a8506099945",
    "1580587771525-78b9dba3b914",
    "1570129477492-45c003edd2be",
    "1513694203232-719a280e022f",
    "1507089947368-19c1da9775ae",
    "1618773928121-c32242e63f39",
    "1598928506311-c55ded91a20c",
    "1600585154526-990dced4db0d",
]

REVIEW_COMMENTS_HIGH = [
    "Absolutely breathtaking location! The views were even better than the photos. Very clean and well equipped.",
    "Such a wonderful retreat! Host was super attentive, check-in was seamless, and the amenities were top-notch.",
    "One of the best Airbnb experiences we've ever had. Clean, cozy, and right where you want to be.",
    "Incredible stay! The house was spotless, comfortable beds, and the surrounding scenery was magical.",
    "Loved every minute here. We enjoyed our morning coffee looking out at the gorgeous views. Highly recommended!",
    "Exceeded all expectations. Modern design, peaceful neighborhood, and the host gave amazing local tips.",
]

REVIEW_COMMENTS_MID = [
    "Good overall stay. Great location close to local attractions, though the internet was a bit slow at times.",
    "Comfortable and clean space. Kitchen had everything we needed. A bit noisy on Saturday night, but otherwise great.",
    "Very pleasant house and lovely hosts. We would definitely stay again on our next visit.",
]
