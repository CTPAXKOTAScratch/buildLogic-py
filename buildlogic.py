import math

BEAM_MAP = [
    (8, "\x06"),  # 8-block beam
    (7, "#c"),    # 7-block beam
    (6, "\x05"),  # 6-block beam
    (5, "\x04"),  # 5-block beam
    (4, "#b"),    # 4-block beam
    (3, "\x03"),  # 3-block beam
    (2, "\x02"),  # 2-block beam
    (1, "G"),     # Single block
]

MATERIAL_MAP = {
    "plastic": "1", "glass": "2", "diamond plate": "3", "fabric": "4", 
    "grass": "5", "ice": "6", "sand": "7", "wood": "8", "planks": "9", 
    "foil": "a", "metal": "b", "brick": "c", "concrete": "d", 
    "marble": "f", "granite": "g", "slate": "h", "horrible_metal": "i", 
    "forcefield": "j"
}

class BuildLogicEngine:
    ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789#$"

    def __init__(self):
        self.block_queue = []

    def add_block(self, x: int, y: int, z: int, rot="A", r=255, g=255, b=255, material_name="plastic", block_type="G"):
        pos_val = (x & 0xFF) | ((y & 0xFF) << 8) | ((z & 0xFF) << 16)
        pos_string = (
            self.ALPHABET[pos_val & 0x3F] +
            self.ALPHABET[(pos_val >> 6) & 0x3F] +
            self.ALPHABET[(pos_val >> 12) & 0x3F] +
            self.ALPHABET[(pos_val >> 18) & 0x3F]
        )
        
        is_white = (r == 255 and g == 255 and b == 255)
        raw_mat = MATERIAL_MAP.get(material_name.lower(), "1")
        
        if is_white and raw_mat == "1":
            color_string = ""
        else:
            c1 = r & 0x3F
            c2 = ((g & 0x0F) << 2) | ((r >> 6) & 0x03)
            c3 = ((b & 0x03) << 4) | ((g >> 4) & 0x0F)
            c4 = (b >> 2) & 0x3F
            color_string = self.ALPHABET[c1] + self.ALPHABET[c2] + self.ALPHABET[c3] + self.ALPHABET[c4]

        mat_suffix = raw_mat if raw_mat != "1" else ""
        encoded_block = block_type + pos_string + rot + color_string + mat_suffix
        self.block_queue.append(encoded_block)

    def export_blueprint(self) -> str:
        return ";".join(self.block_queue)
