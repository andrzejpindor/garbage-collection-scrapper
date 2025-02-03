import requests
import datetime

def get_waste_schedule():
    base_url = "https://bip.jaktorow.pl/odpady-komunalne/getterminy/"
    start_date = datetime.date.today().replace(month=1, day=1).isoformat()
    end_date = datetime.date.today().replace(month=12, day=31).isoformat()
    
    payload = {
        "spot": 13,
        "fraction": 0, # get all fractions
        "property_type": 0,
        "start": f"{start_date}T00:00:00+01:00",
        "end": f"{end_date}T23:59:59+01:00",
    }
    
    response = requests.post(base_url, data=payload)
    response.raise_for_status()
    return response.json()

FRACTION_EMOJIS = {
    1: "\U0001F5D1\U0001F9F9 Zmieszane",  # 🗑🧹
    2: "\U0001F5D1\U0001F5FF Szkło",     # 🗑🗿
    3: "\U0001F5D1\U0001F4DA Papier",    # 🗑📚
    4: "\U0001F5D1\U0001F6E2 Plastik",   # 🗑🛢
    5: "\U0001F5D1\U0001F331 Bio",       # 🗑🌱
}

def convert_to_ics(waste_data):
    ics_content = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//WasteSchedule//EN\n"
    for entry in waste_data:
        title = FRACTION_EMOJIS.get(entry["fraction"], "Wywóz śmieci")
        event_date = entry["start"].replace("-", "")
        ics_content += f"BEGIN:VEVENT\nSUMMARY:{title}\nDTSTART;VALUE=DATE:{event_date}\nDTEND;VALUE=DATE:{event_date}\nEND:VEVENT\n"
    ics_content += "END:VCALENDAR"
    return ics_content

if __name__ == "__main__":
    waste_data = get_waste_schedule()
    ics_data = convert_to_ics(waste_data)
    
    with open("waste_schedule.ics", "w", encoding="utf-8") as f:
        f.write(ics_data)
    
    print("Exported to 'waste_schedule.ics'")
