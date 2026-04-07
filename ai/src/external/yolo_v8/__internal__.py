def unpack_input(data):
    if type(data) is dict:
        return data["images"], data["bounding_boxes"]
    else:
        return data