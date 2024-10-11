from collections import Counter


class SymbTextParser:
    def __init__(self):
        self.note_line_codes = ["1", "4", "7", "8", "9",
                                "10", "11", "12", "23", "24", "28", "44"]

        self.pitches = ["G", "A", "B", "C", "D", "E", "F"]
        self.kommas = [9, 9, 4, 9, 9, 4, 9]

    def convert_to_sharp(self, note):
        """
        Converts notes with accidental symbols to all sharp rep.'s

        G --> G, 
        Bb9 --> A, 
        Eb4 --> D#5, 
        Bb1 --> A#8, 
        Bb13 --> G#5, 
        Gb5 --> F#4, 
        F#4 --> F#4, 
        E#4 --> F, 
        E#5 --> F#1, 
        E#13 --> G
        """

        if len(note) == 1:
            return note

        accidental = note[1]
        if accidental not in ["#", "b"]:
            raise ValueError("Accidental symbol unrecognised!")

        root = note[0]
        idx = self.pitches.index(root)
        komma = int(note[2:])
        next_root, result = None, None
        remaining_komma = komma

        if accidental == "b":
            while remaining_komma > 0:
                idx = (idx - 1) % 7
                next_root = self.pitches[idx]
                remaining_komma -= self.kommas[idx]

            result = next_root
            if remaining_komma < 0:
                result += "#" + str(-1 * remaining_komma)

        elif accidental == "#":
            while remaining_komma > 0:
                remaining_komma -= self.kommas[idx]
                idx = (idx + 1) % 7
                next_root = self.pitches[idx]

            if remaining_komma < 0:
                idx = (idx - 1) % 7
                next_root = self.pitches[idx]
                remaining_komma += self.kommas[idx]

            result = next_root
            if remaining_komma != 0:
                result += "#" + str(remaining_komma)

        return result

    def get_notes_as_pitch_classes(self, file_list, makam=None):
        all_notes = []
        counts = Counter()

        for file_path in file_list:
            if makam and makam + "--" not in file_path:
                continue

            with open(file_path, "r") as in_file:
                lines = in_file.readlines()
                notes = []
                for line in lines:
                    tokens = line.split("\t")
                    if tokens[1] in self.note_line_codes:
                        note = tokens[3]
                        if note == "Es" or (not note[1].isdigit()):
                            continue

                        pitch_class = self.convert_to_sharp(note[0] + note[2:])
                        notes.append(pitch_class)

                all_notes.append(notes)
                counts.update(notes)

        return all_notes, counts
