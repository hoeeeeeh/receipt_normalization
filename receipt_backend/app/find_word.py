def find_word(raw_json_data):
    text_list = []
    json_data = raw_json_data["images"][0]["fields"]
    for data in json_data:
        text = data["inferText"]
        text_list.append(text)
    text_list = [' '.join(text_list)]
    return text_list[0]